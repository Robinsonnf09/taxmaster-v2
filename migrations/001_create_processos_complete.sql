-- TAX MASTER V3 - MIGRACAO COMPLETA
DROP TABLE IF EXISTS processos CASCADE;

CREATE TABLE processos (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(50) UNIQUE NOT NULL,
    tribunal VARCHAR(100) NOT NULL,
    tipo VARCHAR(100) NOT NULL,
    natureza VARCHAR(50) DEFAULT 'Comum',
    valor_principal NUMERIC(15,2) NOT NULL CHECK (valor_principal >= 0),
    juros NUMERIC(15,2) DEFAULT 0 CHECK (juros >= 0),
    valor_total NUMERIC(15,2) NOT NULL CHECK (valor_total >= 0),
    status VARCHAR(50) DEFAULT 'Em Análise' CHECK (status IN ('Em Análise', 'Expedido', 'Pago', 'Suspenso', 'Cancelado')),
    prioridade INTEGER DEFAULT 3 CHECK (prioridade BETWEEN 1 AND 5),
    data_expedicao DATE,
    data_pagamento DATE,
    data_vencimento DATE,
    beneficiario VARCHAR(255) NOT NULL,
    cpf_cnpj VARCHAR(20) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(255),
    advogado VARCHAR(255),
    oab VARCHAR(20),
    escritorio VARCHAR(255),
    observacoes TEXT,
    tags VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE UNIQUE INDEX idx_processos_numero ON processos(numero) WHERE deleted_at IS NULL;
CREATE INDEX idx_processos_tipo_status ON processos(tipo, status) WHERE deleted_at IS NULL;
CREATE INDEX idx_processos_tribunal ON processos(tribunal) WHERE deleted_at IS NULL;
CREATE INDEX idx_processos_beneficiario ON processos(beneficiario) WHERE deleted_at IS NULL;
CREATE INDEX idx_processos_cpf_cnpj ON processos(cpf_cnpj) WHERE deleted_at IS NULL;
CREATE INDEX idx_processos_data_expedicao ON processos(data_expedicao DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_processos_valor_total ON processos(valor_total) WHERE deleted_at IS NULL;
CREATE INDEX idx_processos_active ON processos(is_active) WHERE deleted_at IS NULL;
CREATE INDEX idx_processos_dashboard ON processos(status, tipo, valor_total) WHERE deleted_at IS NULL;

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_processos_updated_at
    BEFORE UPDATE ON processos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE FUNCTION calculate_valor_total()
RETURNS TRIGGER AS $$
BEGIN
    NEW.valor_total = COALESCE(NEW.valor_principal, 0) + COALESCE(NEW.juros, 0);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_processos_valor_total
    BEFORE INSERT OR UPDATE OF valor_principal, juros ON processos
    FOR EACH ROW
    EXECUTE FUNCTION calculate_valor_total();

CREATE OR REPLACE VIEW vw_processos_ativos AS
SELECT * FROM processos WHERE deleted_at IS NULL AND is_active = TRUE;

CREATE OR REPLACE VIEW vw_processos_por_status AS
SELECT status, COUNT(*) as total_processos, SUM(valor_total) as valor_total, AVG(valor_total) as valor_medio
FROM processos WHERE deleted_at IS NULL GROUP BY status;

CREATE OR REPLACE VIEW vw_processos_por_tribunal AS
SELECT tribunal, COUNT(*) as total_processos, SUM(valor_total) as valor_total, AVG(valor_total) as valor_medio
FROM processos WHERE deleted_at IS NULL GROUP BY tribunal ORDER BY valor_total DESC;

ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS tipo VARCHAR(50) DEFAULT 'usuario';