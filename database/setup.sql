-- WhatsApp Cost Calculator Database Setup
-- This script creates the necessary tables and sample data for the API

-- Create whatsapp_messages table
CREATE TABLE IF NOT EXISTS whatsapp_messages (
    id SERIAL PRIMARY KEY,
    telefone VARCHAR(20) NOT NULL,
    mensagem TEXT NOT NULL,
    data_envio TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'sent',
    categoria VARCHAR(50),
    custo_total DECIMAL(10, 6),
    country_code VARCHAR(10)
);

-- Create index for faster queries on unprocessed messages
CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_custo_total_null ON whatsapp_messages(id) WHERE custo_total IS NULL;

-- Create index for country_code
CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_country_code ON whatsapp_messages(country_code);

-- Create index for categoria
CREATE INDEX IF NOT EXISTS idx_whatsapp_messages_categoria ON whatsapp_messages(categoria);

-- Create meta_pricing table
CREATE TABLE IF NOT EXISTS meta_pricing (
    id SERIAL PRIMARY KEY,
    country_code VARCHAR(10) NOT NULL,
    category VARCHAR(50) NOT NULL,
    cost_per_message DECIMAL(10, 6) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create unique constraint to prevent duplicate pricing entries
CREATE UNIQUE INDEX IF NOT EXISTS idx_meta_pricing_unique ON meta_pricing(country_code, category);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_meta_pricing_country_category ON meta_pricing(country_code, category);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_meta_pricing_updated_at ON meta_pricing;
CREATE TRIGGER update_meta_pricing_updated_at
    BEFORE UPDATE ON meta_pricing
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample pricing data for Brazil (country code 55)
INSERT INTO meta_pricing (country_code, category, cost_per_message) VALUES
    ('55', 'service', 0.015),
    ('55', 'utility', 0.012),
    ('55', 'authentication', 0.010),
    ('55', 'marketing', 0.020)
ON CONFLICT (country_code, category) DO NOTHING;

-- Insert sample pricing data for USA (country code 1)
INSERT INTO meta_pricing (country_code, category, cost_per_message) VALUES
    ('1', 'service', 0.018),
    ('1', 'utility', 0.015),
    ('1', 'authentication', 0.012),
    ('1', 'marketing', 0.025)
ON CONFLICT (country_code, category) DO NOTHING;

-- Insert sample pricing data for UK (country code 44)
INSERT INTO meta_pricing (country_code, category, cost_per_message) VALUES
    ('44', 'service', 0.016),
    ('44', 'utility', 0.013),
    ('44', 'authentication', 0.011),
    ('44', 'marketing', 0.022)
ON CONFLICT (country_code, category) DO NOTHING;

-- Insert sample WhatsApp messages for testing
INSERT INTO whatsapp_messages (telefone, mensagem, status) VALUES
    ('+5511999999999', 'Your verification code is 123456', 'sent'),
    ('+5511888888888', 'Your order #12345 has been shipped', 'sent'),
    ('+5511777777777', 'Your bill is due tomorrow. Amount: $100.00', 'sent'),
    ('+5511666666666', 'Check out our new products! 50% off today only!', 'sent'),
    ('+14155552671', 'Welcome to our service! Your account has been created.', 'sent'),
    ('+14155552672', 'Your password reset code is 987654', 'sent'),
    ('+442071234567', 'Payment received. Thank you for your purchase!', 'sent'),
    ('+442071234568', 'Reminder: Your appointment is tomorrow at 10 AM', 'sent')
ON CONFLICT (id) DO NOTHING;

-- Create a function to add country_code to existing messages
CREATE OR REPLACE FUNCTION add_country_code_to_messages()
RETURNS VOID AS $$
BEGIN
    UPDATE whatsapp_messages 
    SET country_code = SUBSTRING(telefone FROM 2 FOR POSITION(' ' IN telefone + '0') - 2)
    WHERE country_code IS NULL AND telefone LIKE '+%';
END;
$$ language 'plpgsql';

-- Execute the function to update existing messages
SELECT add_country_code_to_messages();

-- Create a view for processed messages
CREATE OR REPLACE VIEW processed_messages AS
SELECT 
    id,
    telefone,
    mensagem,
    data_envio,
    status,
    categoria,
    custo_total,
    country_code
FROM whatsapp_messages 
WHERE custo_total IS NOT NULL;

-- Create a view for unprocessed messages
CREATE OR REPLACE VIEW unprocessed_messages AS
SELECT 
    id,
    telefone,
    mensagem,
    data_envio,
    status
FROM whatsapp_messages 
WHERE custo_total IS NULL;

-- Create a view for cost statistics by category
CREATE OR REPLACE VIEW cost_statistics_by_category AS
SELECT 
    categoria,
    COUNT(*) as message_count,
    SUM(custo_total) as total_cost,
    AVG(custo_total) as avg_cost
FROM whatsapp_messages 
WHERE custo_total IS NOT NULL
GROUP BY categoria;

-- Create a view for cost statistics by country
CREATE OR REPLACE VIEW cost_statistics_by_country AS
SELECT 
    country_code,
    COUNT(*) as message_count,
    SUM(custo_total) as total_cost,
    AVG(custo_total) as avg_cost
FROM whatsapp_messages 
WHERE custo_total IS NOT NULL
GROUP BY country_code;

-- Grant permissions (adjust as needed for your Supabase setup)
-- These are examples and may need to be adjusted based on your authentication setup

-- For anon role (public access)
GRANT SELECT ON whatsapp_messages TO anon;
GRANT SELECT ON meta_pricing TO anon;
GRANT UPDATE ON whatsapp_messages TO anon;
GRANT INSERT ON whatsapp_messages TO anon;

-- For authenticated role
GRANT ALL ON whatsapp_messages TO authenticated;
GRANT ALL ON meta_pricing TO authenticated;

-- For service role (admin)
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO service_role;

-- Enable Row Level Security (RLS) if needed
-- ALTER TABLE whatsapp_messages ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE meta_pricing ENABLE ROW LEVEL SECURITY;

-- Example RLS policy for whatsapp_messages (uncomment if using RLS)
-- CREATE POLICY "Allow read access to all messages" ON whatsapp_messages
--     FOR SELECT USING (true);

-- CREATE POLICY "Allow update of cost fields" ON whatsapp_messages
--     FOR UPDATE TO anon USING (
--         pg_has_role('anon', 'member')
--     ) WITH CHECK (
--         pg_has_role('anon', 'member')
--     );

-- Example RLS policy for meta_pricing (uncomment if using RLS)
-- CREATE POLICY "Allow read access to pricing" ON meta_pricing
--     FOR SELECT USING (true);

-- Create a function to get statistics
CREATE OR REPLACE FUNCTION get_api_statistics()
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'total_messages', COUNT(*),
        'processed_messages', COUNT(*) FILTER (WHERE custo_total IS NOT NULL),
        'unprocessed_messages', COUNT(*) FILTER (WHERE custo_total IS NULL),
        'total_cost', COALESCE(SUM(custo_total), 0),
        'categories', (
            SELECT json_agg(
                json_build_object(
                    'category', categoria,
                    'count', COUNT(*),
                    'total_cost', COALESCE(SUM(custo_total), 0)
                )
            )
            FROM whatsapp_messages
            WHERE custo_total IS NOT NULL
            GROUP BY categoria
        ),
        'countries', (
            SELECT json_agg(
                json_build_object(
                    'country_code', country_code,
                    'count', COUNT(*),
                    'total_cost', COALESCE(SUM(custo_total), 0)
                )
            )
            FROM whatsapp_messages
            WHERE custo_total IS NOT NULL
            GROUP BY country_code
        )
    ) INTO result
    FROM whatsapp_messages;
    
    RETURN result;
END;
$$ language 'plpgsql';

-- Comment on tables and columns for documentation
COMMENT ON TABLE whatsapp_messages IS 'Stores WhatsApp messages with their metadata and calculated costs';
COMMENT ON TABLE meta_pricing IS 'Stores pricing information for WhatsApp messages by country and category';

COMMENT ON COLUMN whatsapp_messages.telefone IS 'Phone number in international format (e.g., +5511999999999)';
COMMENT ON COLUMN whatsapp_messages.mensagem IS 'The content of the WhatsApp message';
COMMENT ON COLUMN whatsapp_messages.categoria IS 'Classified category: service, utility, authentication, or marketing';
COMMENT ON COLUMN whatsapp_messages.custo_total IS 'Total cost of the message in USD';
COMMENT ON COLUMN whatsapp_messages.country_code IS 'Extracted country code from the phone number';

COMMENT ON COLUMN meta_pricing.country_code IS 'Country code (e.g., 55 for Brazil, 1 for USA)';
COMMENT ON COLUMN meta_pricing.category IS 'Message category: service, utility, authentication, or marketing';
COMMENT ON COLUMN meta_pricing.cost_per_message IS 'Cost per message in USD';
