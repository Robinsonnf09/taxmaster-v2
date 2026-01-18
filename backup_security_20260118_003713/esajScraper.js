// esajScraper.js - Tax Master V3 - Versão Segura
const axios = require('axios');
const logger = require('./config/logger') || console;

// ⚠️ IMPORTANTE: Configure CNJ_API_KEY no arquivo .env
const CNJ_API_URL = process.env.CNJ_API_URL || 'https://api-publica.datajud.cnj.jus.br';
const CNJ_API_KEY = process.env.CNJ_API_KEY;

if (!CNJ_API_KEY) {
    logger.error('❌ ERRO CRÍTICO: CNJ_API_KEY não configurada!');
    logger.error('Configure a variável CNJ_API_KEY no arquivo .env');
    process.exit(1);
}

async function buscarProcessosESAJ(params) {
    const { valorMin, valorMax, natureza, anoLoa, status, quantidade = 30 } = params;

    logger.info('\n╔═══════════════════════════════════════════════════════╗');
    logger.info('║  🔍 BUSCA 100% REAL - API CNJ DataJud               ║');
    logger.info('╚═══════════════════════════════════════════════════════╝\n');
    
    logger.info('📋 Filtros aplicados:', {
        valorMin: valorMin || 'N/A',
        valorMax: valorMax || 'N/A',
        natureza: natureza || 'Todas',
        anoLoa: anoLoa || 'Todos',
        quantidade
    });

    try {
        const query = {
            size: quantidade * 2,
            query: { match_all: {} },
            sort: [{ 'dataHoraUltimaAtualizacao': { order: 'desc' } }]
        };

        const response = await axios.post(
            `${CNJ_API_URL}/api_publica_tjsp/_search`,
            query,
            {
                headers: {
                    'Authorization': `APIKey ${CNJ_API_KEY}`,
                    'Content-Type': 'application/json'
                },
                timeout: 30000
            }
        );

        const hits = response.data?.hits?.hits || [];
        logger.info(`📊 Processos retornados da API: ${hits.length}`);

        const processados = hits
            .map(hit => processarDados(hit._source))
            .filter(p => validarNumeroProcesso(p.numero));
        
        logger.info(`✅ Processos válidos: ${processados.length}`);

        const filtrados = aplicarFiltros(processados, { valorMin, valorMax, natureza, anoLoa, status });
        const resultado = filtrados.slice(0, quantidade);

        logger.info(`✅ Processos retornados: ${resultado.length}\n`);

        return {
            processos: resultado,
            stats: {
                total: hits.length,
                validos: processados.length,
                filtrados: filtrados.length,
                retornados: resultado.length
            }
        };

    } catch (error) {
        logger.error(`❌ Erro na busca: ${error.message}`);
        return { 
            processos: [], 
            stats: { erro: error.message } 
        };
    }
}

function processarDados(p) {
    return {
        numero: p.numeroProcesso || '',
        tribunal: 'TJ-SP',
        credor: extrairCreador(p.partes),
        valor: p.valorCausa || 0,
        classe: p.classe?.nome || 'Não informado',
        assunto: extrairAssunto(p.assunto),
        dataDistribuicao: formatarData(p.dataAjuizamento),
        comarca: p.orgaoJulgador?.comarca || 'São Paulo',
        vara: p.orgaoJulgador?.nome || 'Não informado',
        natureza: determinarNatureza(p.classe?.nome, p.assunto),
        anoLOA: extrairAno(p.numeroProcesso) + 7,
        status: 'Pendente',
        fonte: '✅ API CNJ DataJud (OFICIAL)'
    };
}

function validarNumeroProcesso(numero) {
    if (!numero || numero.length < 15) return false;
    const limpo = numero.replace(/\D/g, '');
    return limpo.length >= 20;
}

function extrairAno(numero) {
    if (!numero || numero.length < 13) return new Date().getFullYear();
    const ano = parseInt(numero.substring(9, 13));
    return isNaN(ano) ? new Date().getFullYear() : ano;
}

function extrairCreador(partes) {
    if (!partes || !Array.isArray(partes)) return 'Não informado';
    const ativo = partes.find(p => p.polo === 'ATIVO' || p.tipo === 'AUTOR');
    return ativo?.nome || 'Não informado';
}

function extrairAssunto(assuntos) {
    if (!assuntos || !Array.isArray(assuntos)) return 'Não informado';
    return assuntos.map(a => a.nome).join(', ');
}

function determinarNatureza(classe, assuntos) {
    const texto = [classe || '', ...(assuntos || []).map(a => a.nome || '')].join(' ').toLowerCase();
    if (texto.match(/aliment|pensão|salário/i)) return 'Alimentar';
    if (texto.match(/tribut|fiscal|iptu/i)) return 'Tributária';
    if (texto.match(/previd|benefício/i)) return 'Previdenciária';
    return 'Comum';
}

function formatarData(dataStr) {
    if (!dataStr) return new Date().toISOString().split('T')[0];
    if (dataStr.match(/^\d{8}/)) {
        return `${dataStr.substring(0,4)}-${dataStr.substring(4,6)}-${dataStr.substring(6,8)}`;
    }
    return dataStr.split('T')[0];
}

function aplicarFiltros(processos, filtros) {
    return processos.filter(p => {
        if (filtros.valorMin && p.valor > 0 && p.valor < filtros.valorMin) return false;
        if (filtros.valorMax && p.valor > 0 && p.valor > filtros.valorMax) return false;
        if (filtros.natureza && filtros.natureza !== 'Todas' && p.natureza !== filtros.natureza) return false;
        if (filtros.anoLoa && filtros.anoLoa !== 'Todos' && parseInt(filtros.anoLoa) !== p.anoLOA) return false;
        if (filtros.status && filtros.status !== 'Todos' && p.status !== filtros.status) return false;
        return true;
    });
}

module.exports = { buscarProcessosESAJ };
