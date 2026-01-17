const axios = require('axios');
const NodeCache = require('node-cache');

// Cache de 30 minutos
const cache = new NodeCache({ stdTTL: 1800 });

// ============================================
// CONFIGURAÇÃO OFICIAL DATAJUD CNJ
// ============================================

const DATAJUD_CONFIG = {
    baseURL: 'https://api-publica.datajud.cnj.jus.br',
    endpoints: {
        'TJ-SP': '/api_publica_tjsp/_search',
        'TJ-RJ': '/api_publica_tjrj/_search',
        'TJ-MG': '/api_publica_tjmg/_search',
        'TJ-RS': '/api_publica_tjrs/_search',
        'TJ-PR': '/api_publica_tjpr/_search',
        'TJ-BA': '/api_publica_tjba/_search',
        'TJ-SC': '/api_publica_tjsc/_search',
        'TJ-PE': '/api_publica_tjpe/_search'
    },
    timeout: 60000,
    // CREDENCIAIS: Obtidas em https://www.cnj.jus.br/sistemas/datajud/api-publica/
    auth: {
        username: process.env.DATAJUD_USER || '',
        password: process.env.DATAJUD_PASS || ''
    }
};

// ============================================
// CONSTRUIR QUERY ELASTICSEARCH (OFICIAL)
// ============================================

function construirQueryOficial(filtros) {
    const query = {
        size: Math.min(parseInt(filtros.quantidade) || 50, 100),
        query: {
            bool: {
                must: [],
                filter: []
            }
        },
        sort: [
            { "@timestamp": { "order": "desc" } }
        ]
    };
    
    // Filtro de valor (usando valorCausa conforme glossário oficial)
    if (filtros.valorMinimo || filtros.valorMaximo) {
        const rangeQuery = { 
            range: { 
                "valorCausa": {} 
            } 
        };
        
        if (filtros.valorMinimo) {
            rangeQuery.range.valorCausa.gte = parseFloat(filtros.valorMinimo);
        }
        
        if (filtros.valorMaximo) {
            rangeQuery.range.valorCausa.lte = parseFloat(filtros.valorMaximo);
        }
        
        query.query.bool.filter.push(rangeQuery);
    }
    
    // Filtro de classe processual (natureza)
    if (filtros.natureza) {
        // Mapear natureza para códigos de classe processual
        const classesMap = {
            'Alimentar': [276, 1116], // Códigos exemplo
            'Tributária': [1116, 1117],
            'Previdenciária': [1218, 1219],
            'Trabalhista': [39, 40],
            'Comum': [0]
        };
        
        const codigos = classesMap[filtros.natureza] || [];
        
        if (codigos.length > 0) {
            query.query.bool.should = codigos.map(codigo => ({
                match: { "classe.codigo": codigo }
            }));
            query.query.bool.minimum_should_match = 1;
        }
    }
    
    // Filtro de ano (usando dataAjuizamento)
    if (filtros.anoLOA) {
        const ano = parseInt(filtros.anoLOA) - 2; // LOA é +2 anos após ajuizamento
        query.query.bool.filter.push({
            range: {
                "dataAjuizamento": {
                    gte: `${ano}-01-01`,
                    lte: `${ano}-12-31`
                }
            }
        });
    }
    
    return query;
}

// ============================================
// BUSCA REAL NO DATAJUD CNJ
// ============================================

async function buscarDataJudReal(filtros) {
    const cacheKey = `datajud_${JSON.stringify(filtros)}`;
    const cached = cache.get(cacheKey);
    
    if (cached) {
        console.log('✅ Cache hit - retornando dados salvos');
        return cached;
    }
    
    const endpoint = DATAJUD_CONFIG.endpoints[filtros.tribunal] || DATAJUD_CONFIG.endpoints['TJ-SP'];
    const url = `${DATAJUD_CONFIG.baseURL}${endpoint}`;
    const query = construirQueryOficial(filtros);
    
    console.log(`\n🔍 BUSCA REAL DATAJUD CNJ`);
    console.log(`   URL: ${url}`);
    console.log(`   Tribunal: ${filtros.tribunal}`);
    console.log(`   Valor: ${filtros.valorMinimo} - ${filtros.valorMaximo}`);
    console.log(`   Query:`, JSON.stringify(query, null, 2));
    
    try {
        const response = await axios({
            method: 'POST',
            url: url,
            data: query,
            headers: {
                'Content-Type': 'application/json'
            },
            auth: DATAJUD_CONFIG.auth,
            timeout: DATAJUD_CONFIG.timeout
        });
        
        console.log(`   Status: ${response.status}`);
        console.log(`   Total hits: ${response.data.hits?.total?.value || 0}`);
        
        if (response.data.hits && response.data.hits.hits && response.data.hits.hits.length > 0) {
            const processos = processarResultadosOficiais(response.data.hits.hits, filtros);
            
            console.log(`✅ ${processos.length} processos REAIS encontrados`);
            
            // Salvar no cache
            cache.set(cacheKey, processos);
            
            return processos;
        }
        
        console.log('⚠️ Nenhum processo encontrado com esses filtros');
        return [];
        
    } catch (error) {
        if (error.response) {
            console.error(`❌ Erro HTTP ${error.response.status}:`, error.response.data);
            
            if (error.response.status === 401) {
                console.error('⚠️ ERRO DE AUTENTICAÇÃO!');
                console.error('   Configure as credenciais:');
                console.error('   1. Crie conta em: https://www.cnj.jus.br/sistemas/datajud/api-publica/');
                console.error('   2. Defina variáveis: DATAJUD_USER e DATAJUD_PASS');
                
                return {
                    erro: 'autenticacao',
                    mensagem: 'Credenciais não configuradas. Acesse https://www.cnj.jus.br/sistemas/datajud/api-publica/ para criar conta.'
                };
            }
        }
        
        console.error('❌ Erro na busca:', error.message);
        return [];
    }
}

// ============================================
// PROCESSAR RESULTADOS (FORMATO OFICIAL)
// ============================================

function processarResultadosOficiais(hits, filtros) {
    return hits.map(hit => {
        const source = hit._source;
        
        return {
            numero: source.numeroProcesso || 'N/A',
            tribunal: source.tribunal || filtros.tribunal,
            credor: extrairCredorOficial(source),
            valor: parseFloat(source.valorCausa || 0),
            status: determinarStatus(source),
            natureza: extrairNatureza(source),
            anoLOA: extrairAnoLOA(source),
            dataDistribuicao: formatarData(source.dataAjuizamento),
            classe: source.classe?.nome || 'N/A',
            orgaoJulgador: source.orgaoJulgador?.nome || 'N/A',
            grau: source.grau || 'N/A',
            fonte: 'DataJud CNJ (Oficial)',
            _id: hit._id
        };
    });
}

function extrairCredorOficial(source) {
    // Conforme documentação oficial, não há campo "credor" direto
    // Precisa extrair dos polos (mas isso requer processo individual)
    return 'Consultar processo individual';
}

function determinarStatus(source) {
    if (!source.movimentos || source.movimentos.length === 0) {
        return 'Em Análise';
    }
    
    const ultimoMov = source.movimentos[source.movimentos.length - 1];
    const nomeMovimento = (ultimoMov.nome || '').toLowerCase();
    
    if (nomeMovimento.includes('aprovad') || nomeMovimento.includes('deferi')) {
        return 'Aprovado';
    }
    
    if (nomeMovimento.includes('pendent') || nomeMovimento.includes('aguard')) {
        return 'Pendente';
    }
    
    if (nomeMovimento.includes('arquiv') || nomeMovimento.includes('baixa')) {
        return 'Arquivado';
    }
    
    return 'Em Análise';
}

function extrairNatureza(source) {
    if (!source.assuntos || source.assuntos.length === 0) {
        return source.classe?.nome || 'Comum';
    }
    
    const assunto = source.assuntos[0].nome || '';
    const assuntoLower = assunto.toLowerCase();
    
    if (assuntoLower.includes('aliment')) return 'Alimentar';
    if (assuntoLower.includes('tribut') || assuntoLower.includes('fiscal')) return 'Tributária';
    if (assuntoLower.includes('previd') || assuntoLower.includes('inss')) return 'Previdenciária';
    if (assuntoLower.includes('trabalh') || assuntoLower.includes('clt')) return 'Trabalhista';
    
    return source.classe?.nome || 'Comum';
}

function extrairAnoLOA(source) {
    if (!source.dataAjuizamento) {
        return new Date().getFullYear() + 1;
    }
    
    try {
        const ano = parseInt(source.dataAjuizamento.substring(0, 4));
        return ano + 2; // LOA normalmente 2 anos após ajuizamento
    } catch {
        return new Date().getFullYear() + 1;
    }
}

function formatarData(dataISO) {
    if (!dataISO) return 'N/A';
    
    try {
        const data = new Date(dataISO);
        return data.toLocaleDateString('pt-BR');
    } catch {
        return 'N/A';
    }
}

// ============================================
// EXPORTAR
// ============================================

module.exports = { buscarDataJudReal, DATAJUD_CONFIG };
