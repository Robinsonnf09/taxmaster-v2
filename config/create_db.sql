-- Criar banco de dados taxmaster_crm
DROP DATABASE IF EXISTS taxmaster_crm;
CREATE DATABASE taxmaster_crm;

-- Conectar ao banco
\c taxmaster_crm;

-- Criar extensoes
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Mensagem de sucesso
SELECT 'Banco de dados criado com sucesso!' as status;
