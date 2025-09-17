-- Create API keys table for storing API credentials
CREATE TABLE api_keys (
  id BIGSERIAL PRIMARY KEY,
  service_name TEXT NOT NULL UNIQUE, -- 'perplexity', 'serp', 'ninja_api', etc.
  description TEXT, -- What this API is used for (e.g., "Real-time news search", "Academic papers", "Weather data")
  api_key TEXT NOT NULL,
  base_url TEXT, -- API endpoint URL
  headers JSONB, -- Custom headers for this API
  rate_limit_per_minute INTEGER DEFAULT 60,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS for security
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

-- Create policy for API keys access
CREATE POLICY "api_keys_policy" ON api_keys FOR ALL USING (true);

-- Create index for faster lookups
CREATE INDEX idx_api_keys_service_name ON api_keys(service_name);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);

-- Add trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_api_keys_updated_at BEFORE UPDATE ON api_keys
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
