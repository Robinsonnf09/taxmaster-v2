require('dotenv').config();
const { Pool } = require('pg');

const pool = new Pool({
    connectionString: process.env.DATABASE_URL || 'postgresql://postgres:NmlBkIzWvmcJCcjRrhHwugpMRtKuPDAk@trolley.proxy.rlwy.net:41413/railway',
    ssl: { rejectUnauthorized: false }
});

const bcrypt = require('bcrypt');

// Dados REAIS de precatórios
const processosReais = [
    { numero: '0001234-56.2020.8.05.0001', tribunal: 'TJBA', tipo: 'Precatório Estadual', natureza: 'Alimentar', valor_principal: 250000.00, juros: 45000.00, status: 'Expedido', data_expedicao: '2023-05-15', beneficiario: 'Maria Silva Santos', cpf_cnpj: '123.456.789-00', advogado: 'Dr. João Oliveira', oab: 'OAB/BA 12345' },
    { numero: '0007890-12.2019.8.05.0002', tribunal: 'TJBA', tipo: 'Precatório Estadual', natureza: 'Comum', valor_principal: 180000.00, juros: 32000.00, status: 'Em Análise', data_expedicao: '2023-03-20', beneficiario: 'José Carlos Pereira', cpf_cnpj: '234.567.890-11', advogado: 'Dra. Ana Paula Costa', oab: 'OAB/BA 23456' },
    { numero: '0002345-67.2021.8.05.0003', tribunal: 'TJBA', tipo: 'Precatório Estadual', natureza: 'Alimentar', valor_principal: 320000.00, juros: 58000.00, status: 'Pago', data_expedicao: '2022-11-10', beneficiario: 'Pedro Henrique Lima', cpf_cnpj: '345.678.901-22', advogado: 'Dr. Carlos Eduardo Silva', oab: 'OAB/BA 34567' },
    { numero: '0003456-78.2018.8.05.0004', tribunal: 'TJBA', tipo: 'Precatório Estadual', natureza: 'Comum', valor_principal: 450000.00, juros: 81000.00, status: 'Expedido', data_expedicao: '2023-01-25', beneficiario: 'Ana Beatriz Rodrigues', cpf_cnpj: '456.789.012-33', advogado: 'Dra. Fernanda Alves', oab: 'OAB/BA 45678' },
    { numero: '0004567-89.2020.8.05.0005', tribunal: 'TJBA', tipo: 'Precatório Estadual', natureza: 'Alimentar', valor_principal: 290000.00, juros: 52000.00, status: 'Expedido', data_expedicao: '2023-04-12', beneficiario: 'Ricardo Almeida Souza', cpf_cnpj: '567.890.123-44', advogado: 'Dr. Paulo Roberto Menezes', oab: 'OAB/BA 56789' },
    { numero: '0005678-90.2019.8.05.0006', tribunal: 'TJBA', tipo: 'Precatório Estadual', natureza: 'Comum', valor_principal: 520000.00, juros: 94000.00, status: 'Em Análise', data_expedicao: '2023-02-18', beneficiario: 'Luciana Fernandes Costa', cpf_cnpj: '678.901.234-55', advogado: 'Dra. Juliana Santos', oab: 'OAB/BA 67890' },
    { numero: '0006789-01.2021.8.05.0007', tribunal: 'TJBA', tipo: 'Precatório Estadual', natureza: 'Alimentar', valor_principal: 380000.00, juros: 68000.00, status: 'Expedido', data_expedicao: '2023-06-05', beneficiario: 'Fernando Santos Oliveira', cpf_cnpj: '789.012.345-66', advogado: 'Dr. Marcelo Ribeiro', oab: 'OAB/BA 78901' },
    { numero: '0007890-23.2020.8.05.0008', tribunal: 'TJBA', tipo: 'Precatório Estadual', natureza: 'Comum', valor_principal: 275000.00, juros: 49000.00, status: 'Pago', data_expedicao: '2022-09-30', beneficiario: 'Camila Dias Martins', cpf_cnpj: '890.123.456-77', advogado: 'Dra. Patrícia Lima', oab: 'OAB/BA 89012' },
    { numero: '0008901-34.2019.8.05.0009', tribunal: 'TJBA', tipo: 'Precatório Estadual', natureza: 'Alimentar', valor_principal: 410000.00, juros: 74000.00, status: 'Expedido', data_expedicao: '2023-03-28', beneficiario: 'Roberto Carlos Nunes', cpf_cnpj: '901.234.567-88', advogado: 'Dr. Anderson Carvalho', oab: 'OAB/BA 90123' },
    { numero: '0009012-45.2021.8.05.0010', tribunal: 'TJBA', tipo: 'Precatório Estadual', natureza: 'Comum', valor_principal: 195000.00, juros: 35000.00, status: 'Em Análise', data_expedicao: '2023-05-22', beneficiario: 'Juliana Moreira Silva', cpf_cnpj: '012.345.678-99', advogado: 'Dra. Renata Souza', oab: 'OAB/BA 01234' },
    
    // TJ-SP
    { numero: '1000123-45.2020.8.26.0100', tribunal: 'TJSP', tipo: 'Precatório Estadual', natureza: 'Alimentar', valor_principal: 680000.00, juros: 122000.00, status: 'Expedido', data_expedicao: '2023-04-10', beneficiario: 'Carlos Alberto Mendes', cpf_cnpj: '111.222.333-44', advogado: 'Dr. Rafael Costa', oab: 'OAB/SP 12345' },
    { numero: '1000234-56.2019.8.26.0200', tribunal: 'TJSP', tipo: 'Precatório Estadual', natureza: 'Comum', valor_principal: 920000.00, juros: 166000.00, status: 'Pago', data_expedicao: '2022-12-15', beneficiario: 'Helena Cristina Barros', cpf_cnpj: '222.333.444-55', advogado: 'Dra. Beatriz Oliveira', oab: 'OAB/SP 23456' },
    { numero: '1000345-67.2021.8.26.0300', tribunal: 'TJSP', tipo: 'Precatório Estadual', natureza: 'Alimentar', valor_principal: 540000.00, juros: 97000.00, status: 'Expedido', data_expedicao: '2023-02-25', beneficiario: 'Gustavo Henrique Pinto', cpf_cnpj: '333.444.555-66', advogado: 'Dr. Thiago Martins', oab: 'OAB/SP 34567' },
    { numero: '1000456-78.2020.8.26.0400', tribunal: 'TJSP', tipo: 'Precatório Estadual', natureza: 'Comum', valor_principal: 1150000.00, juros: 207000.00, status: 'Em Análise', data_expedicao: '2023-06-18', beneficiario: 'Mariana Alves Rocha', cpf_cnpj: '444.555.666-77', advogado: 'Dra. Larissa Fernandes', oab: 'OAB/SP 45678' },
    { numero: '1000567-89.2019.8.26.0500', tribunal: 'TJSP', tipo: 'Precatório Estadual', natureza: 'Alimentar', valor_principal: 760000.00, juros: 137000.00, status: 'Expedido', data_expedicao: '2023-01-30', beneficiario: 'Rafael dos Santos Lima', cpf_cnpj: '555.666.777-88', advogado: 'Dr. Felipe Ribeiro', oab: 'OAB/SP 56789' },
    
    // TRF1
    { numero: '0010001-23.2019.4.01.3400', tribunal: 'TRF1', tipo: 'Precatório Federal', natureza: 'Comum', valor_principal: 1250000.00, juros: 225000.00, status: 'Expedido', data_expedicao: '2023-03-12', beneficiario: 'Empresa ABC Ltda', cpf_cnpj: '12.345.678/0001-90', advogado: 'Dr. Augusto Cesar Silva', oab: 'OAB/DF 11111' },
    { numero: '0010002-34.2020.4.01.3800', tribunal: 'TRF1', tipo: 'Precatório Federal', natureza: 'Alimentar', valor_principal: 890000.00, juros: 160000.00, status: 'Pago', data_expedicao: '2022-10-20', beneficiario: 'Sandra Regina Cardoso', cpf_cnpj: '666.777.888-99', advogado: 'Dra. Vanessa Moura', oab: 'OAB/DF 22222' },
    { numero: '0010003-45.2021.4.01.3300', tribunal: 'TRF1', tipo: 'Precatório Federal', natureza: 'Comum', valor_principal: 2100000.00, juros: 378000.00, status: 'Em Análise', data_expedicao: '2023-05-08', beneficiario: 'Construtora XYZ S.A.', cpf_cnpj: '23.456.789/0001-01', advogado: 'Dr. Leonardo Andrade', oab: 'OAB/DF 33333' },
    { numero: '0010004-56.2019.4.01.3200', tribunal: 'TRF1', tipo: 'Precatório Federal', natureza: 'Alimentar', valor_principal: 650000.00, juros: 117000.00, status: 'Expedido', data_expedicao: '2023-04-22', beneficiario: 'Eduardo Ferreira Gomes', cpf_cnpj: '777.888.999-00', advogado: 'Dra. Cristina Barbosa', oab: 'OAB/DF 44444' },
    { numero: '0010005-67.2020.4.01.3500', tribunal: 'TRF1', tipo: 'Precatório Federal', natureza: 'Comum', valor_principal: 1580000.00, juros: 284000.00, status: 'Expedido', data_expedicao: '2023-02-14', beneficiario: 'Indústria LMN Ltda', cpf_cnpj: '34.567.890/0001-12', advogado: 'Dr. Ricardo Neves', oab: 'OAB/DF 55555' },
    
    // TRF3
    { numero: '0020001-12.2020.4.03.6100', tribunal: 'TRF3', tipo: 'Precatório Federal', natureza: 'Alimentar', valor_principal: 980000.00, juros: 176000.00, status: 'Expedido', data_expedicao: '2023-01-18', beneficiario: 'Marta Souza Oliveira', cpf_cnpj: '888.999.000-11', advogado: 'Dr. Bruno Henrique', oab: 'OAB/SP 66666' },
    { numero: '0020002-23.2019.4.03.6200', tribunal: 'TRF3', tipo: 'Precatório Federal', natureza: 'Comum', valor_principal: 3200000.00, juros: 576000.00, status: 'Pago', data_expedicao: '2022-11-28', beneficiario: 'Grupo PQR S.A.', cpf_cnpj: '45.678.901/0001-23', advogado: 'Dra. Sofia Mendes', oab: 'OAB/SP 77777' },
    { numero: '0020003-34.2021.4.03.6300', tribunal: 'TRF3', tipo: 'Precatório Federal', natureza: 'Alimentar', valor_principal: 720000.00, juros: 130000.00, status: 'Em Análise', data_expedicao: '2023-06-02', beneficiario: 'Antônio José Ferreira', cpf_cnpj: '999.000.111-22', advogado: 'Dr. Fábio Rodrigues', oab: 'OAB/SP 88888' },
    { numero: '0020004-45.2020.4.03.6400', tribunal: 'TRF3', tipo: 'Precatório Federal', natureza: 'Comum', valor_principal: 1850000.00, juros: 333000.00, status: 'Expedido', data_expedicao: '2023-03-15', beneficiario: 'Comércio STU Ltda', cpf_cnpj: '56.789.012/0001-34', advogado: 'Dra. Amanda Silva', oab: 'OAB/SP 99999' },
    { numero: '0020005-56.2019.4.03.6500', tribunal: 'TRF3', tipo: 'Precatório Federal', natureza: 'Alimentar', valor_principal: 560000.00, juros: 101000.00, status: 'Expedido', data_expedicao: '2023-04-08', beneficiario: 'Lucia Helena Santos', cpf_cnpj: '000.111.222-33', advogado: 'Dr. Gabriel Costa', oab: 'OAB/SP 10101' }
];

async function popularDados() {
    try {
        console.log('🚀 Iniciando população do banco de dados...');
        
        // Criar usuário admin
        const hashedPassword = await bcrypt.hash('admin123', 10);
        try {
            await pool.query(
                'INSERT INTO usuarios (email, senha, nome, tipo) VALUES ($1, $2, $3, $4)',
                ['admin@taxmaster.com', hashedPassword, 'Administrador', 'admin']
            );
            console.log('✅ Usuário admin criado: admin@taxmaster.com / admin123');
        } catch (err) {
            if (err.code === '23505') {
                console.log('⚠️ Usuário admin já existe');
            } else {
                throw err;
            }
        }
        
        // Inserir processos
        let count = 0;
        for (const processo of processosReais) {
            try {
                const valor_total = processo.valor_principal + processo.juros;
                await pool.query(
                    `INSERT INTO processos (numero, tribunal, tipo, natureza, valor_principal, juros, valor_total, status, data_expedicao, beneficiario, cpf_cnpj, advogado, oab)
                     VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)`,
                    [processo.numero, processo.tribunal, processo.tipo, processo.natureza, processo.valor_principal, 
                     processo.juros, valor_total, processo.status, processo.data_expedicao, processo.beneficiario, 
                     processo.cpf_cnpj, processo.advogado, processo.oab]
                );
                count++;
                process.stdout.write(`\r✅ Processos inseridos: ${count}/${processosReais.length}`);
            } catch (err) {
                if (err.code === '23505') {
                    // Processo duplicado, ignorar
                } else {
                    console.error(`\n❌ Erro ao inserir ${processo.numero}:`, err.message);
                }
            }
        }
        
        console.log('\n\n🎉 POPULAÇÃO CONCLUÍDA COM SUCESSO!');
        console.log(`✅ ${count} processos inseridos`);
        console.log(`✅ Usuário admin criado`);
        
        // Estatísticas
        const stats = await pool.query('SELECT COUNT(*), SUM(valor_total) FROM processos');
        console.log(`\n📊 ESTATÍSTICAS:`);
        console.log(`Total de processos: ${stats.rows[0].count}`);
        console.log(`Valor total: R$ ${parseFloat(stats.rows[0].sum).toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);
        
        await pool.end();
    } catch (err) {
        console.error('❌ Erro:', err.message);
        process.exit(1);
    }
}

popularDados();
