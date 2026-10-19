-- GOWM-X schema v0001: PostgreSQL; run through a privileged migration job.
-- Future schema changes must be versioned. Never run CREATE TABLE in request handling.
BEGIN;

CREATE TABLE IF NOT EXISTS virtual_dids (
  id VARCHAR(36) PRIMARY KEY,
  tenant_id VARCHAR(128) NOT NULL,
  e164 VARCHAR(16) NOT NULL,
  alias VARCHAR(64) NOT NULL,
  provider_id VARCHAR(128) NOT NULL,
  provider_reference VARCHAR(256) NOT NULL,
  target_uri VARCHAR(256) NOT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'reserved',
  voice_enabled BOOLEAN NOT NULL DEFAULT FALSE,
  sms_enabled BOOLEAN NOT NULL DEFAULT FALSE,
  cli_verified BOOLEAN NOT NULL DEFAULT FALSE,
  dno_blocked BOOLEAN NOT NULL DEFAULT TRUE,
  dno_checked_at TIMESTAMPTZ,
  provisioning_verified_at TIMESTAMPTZ,
  CONSTRAINT uq_tenant_alias UNIQUE (tenant_id, alias),
  CONSTRAINT ck_did_status CHECK (status IN ('reserved', 'active', 'suspended', 'released'))
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_virtual_dids_e164 ON virtual_dids (e164);
CREATE INDEX IF NOT EXISTS ix_virtual_dids_tenant_id ON virtual_dids (tenant_id);
CREATE INDEX IF NOT EXISTS ix_virtual_dids_tenant_status ON virtual_dids (tenant_id, status);

COMMIT;
