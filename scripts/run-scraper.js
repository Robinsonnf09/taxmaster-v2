require('dotenv').config();
const { Pool } = require('pg');
const TRF3Scraper = require('../backend/scrapers/trf3-scraper');
const TJBAScraper = require('../backend/scrapers/tjba-scraper');

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

async function salvarOficios(oficios) {
    let novos = 0;
    let erros = 0;
    
    for (const oficio of oficios) {
        try {
            await pool.query(`
                INSERT INTO oficios (
                    numero_oficio, numero_processo, tribunal, tipo, natureza,
                    valor_principal, juros, valor_total, beneficiario, cpf_cnpj,
                    data_expedicao, status, prioridade, score, url_origem
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                ON CONFLICT (numero_oficio) DO UPDATE SET
                    valor_total = EXCLUDED.valor_total,
                    updated_at = CURRENT_TIMESTAMP
            `, [
                oficio.numero_oficio, oficio.numero_processo, oficio.tribunal,
                oficio.tipo, oficio.natureza, oficio.valor_principal, oficio.juros,
                oficio.valor_total, oficio.beneficiario, oficio.cpf_cnpj,
                oficio.data_expedicao, oficio.status, oficio.prioridade,
                oficio.score, oficio.url_origem
            ]);
            
            novos++;
        } catch (err) {
            erros++;
            console.error(`❌ Erro ao salvar ${oficio.numero_oficio}:`, err.message);
        }
    }
    
    return { novos, erros };
}

async function runScraper(tribunal) {
    const startTime = Date.now();
    
    try {
        console.log('\n═══════════════════════════════════════════════════════════════');
        console.log(`  🤖 EXECUTANDO SCRAPER REAL: ${tribunal.toUpperCase()}`);
        console.log('═══════════════════════════════════════════════════════════════\n');
        
        let scraper;
        
        switch (tribunal.toLowerCase()) {
            case 'trf3':
                scraper = new TRF3Scraper();
                break;
            case 'tjba':
                scraper = new TJBAScraper();
                break;
            default:
                console.log(`❌ Scraper ${tribunal} não implementado`);
                return;
        }
        
        // Executar scraper
        const resultado = await scraper.run();
        const tempoExecucao = Math.round((Date.now() - startTime) / 1000);
        
        if (resultado.success && resultado.oficios.length > 0) {
            console.log(`\n💾 Salvando ${resultado.oficios.length} ofícios no banco...`);
            const { novos, erros } = await salvarOficios(resultado.oficios);
            
            console.log(`\n✅ Salvos: ${novos} ofícios`);
            if (erros > 0) console.log(`⚠️  Erros: ${erros}`);
            
            // Salvar log no banco
            await pool.query(`
                INSERT INTO scrapers_log (tribunal, status, oficios_encontrados, oficios_novos, tempo_execucao)
                VALUES ($1, $2, $3, $4, $5)
            `, [
                tribunal.toUpperCase(),
                'Sucesso',
                resultado.oficios.length,
                novos,
                tempoExecucao
            ]);
            
            console.log('\n✅ Log salvo no banco');
        } else {
            console.log('\n⚠️  Nenhum ofício encontrado');
            
            await pool.query(`
                INSERT INTO scrapers_log (tribunal, status, oficios_encontrados, tempo_execucao, erro_mensagem)
                VALUES ($1, $2, $3, $4, $5)
            `, [
                tribunal.toUpperCase(),
                'Parcial',
                0,
                tempoExecucao,
                'Nenhum dado extraído'
            ]);
        }
        
        console.log('\n═══════════════════════════════════════════════════════════════');
        console.log(`  ✅ SCRAPER CONCLUÍDO EM ${tempoExecucao}s`);
        console.log('═══════════════════════════════════════════════════════════════\n');
        
        await pool.end();
        
    } catch (err) {
        console.error('\n❌ ERRO FATAL:', err.message);
        console.error(err.stack);
        
        const tempoExecucao = Math.round((Date.now() - startTime) / 1000);
        
        try {
            await pool.query(`
                INSERT INTO scrapers_log (tribunal, status, tempo_execucao, erro_mensagem)
                VALUES ($1, $2, $3, $4)
            `, [tribunal.toUpperCase(), 'Erro', tempoExecucao, err.message]);
        } catch (e) {
            console.error('Erro ao salvar log:', e.message);
        }
        
        await pool.end();
        process.exit(1);
    }
}

const tribunal = process.argv[2] || 'trf3';
runScraper(tribunal);