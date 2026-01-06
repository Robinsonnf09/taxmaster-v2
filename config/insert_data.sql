\c taxmaster_crm;

-- Inserir processos de exemplo
INSERT INTO processos (numero_processo, tribunal, tipo, valor_principal, valor_atualizado, credor_nome, fase, score_oportunidade, dados_completos, created_at, updated_at)
VALUES 
('0001234-56.2024.8.19.0001', 'TJRJ', 'Precatorio', 2300000, 2530000, 'Joao Silva', 'Expedido', 9.2, '{"exemplo": true}', NOW(), NOW()),
('1234567-89.2024.8.26.0100', 'TJSP', 'Precatorio', 450000, 495000, 'Maria Santos', 'Transito em julgado', 8.7, '{"exemplo": true}', NOW(), NOW()),
('0012345-67.2024.4.01.0000', 'TRF1', 'Precatorio', 1800000, 1980000, 'Pedro Costa', 'Fase final', 8.9, '{"exemplo": true}', NOW(), NOW()),
('9876543-21.2024.8.21.0001', 'TJRS', 'Precatorio', 680000, 748000, 'Ana Oliveira', 'Em andamento', 7.5, '{"exemplo": true}', NOW(), NOW()),
('5555555-55.2024.4.02.0000', 'TRF2', 'Precatorio', 320000, 352000, 'Carlos Souza', 'Inicial', 6.8, '{"exemplo": true}', NOW(), NOW());

SELECT 'Dados de exemplo inseridos!' as status;
SELECT COUNT(*) as total_processos FROM processos;
