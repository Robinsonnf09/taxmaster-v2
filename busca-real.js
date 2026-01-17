const puppeteer = require('puppeteer');
const axios = require('axios');
const cheerio = require('cheerio');
const NodeCache = require('node-cache');

// Cache de 1 hora
const cache = new NodeCache({ stdTTL: 3600 });

// Configurações
const CONFIG = {
    TJSP_URL: 'https://esaj.tjsp.jus.br/cprecatorio/open.do',
    TIMEOUT: 30000,
    MAX_RETRIES: 3,
    RETRY_DELAY: 2000,
    USER_AGENT: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
};

// ============================================
// BUSCA NO TJ-SP ESAJ (SCRAPING REAL)
// ============================================

async function buscarPrecatoriosTJSP(filtros) {
    const cacheKey = `tjsp_${JSON.stringify(filtros)}`;
    const cached = cache.get(cacheKey);
    
    if (cached) {
        console.log('✅ Retornando resultados do cache');
        return cached;
    }
    
    console.log('🔍 Iniciando busca REAL no TJ-SP ESAJ...');
    
    let browser;
    try {
        browser = await puppeteer.launch({
            headless: 'new',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        });
        
        const page = await browser.newPage();
        await page.setUserAgent(CONFIG.USER_AGENT);
        await page.setViewport({ width: 1920, height: 1080 });
        
        console.log(`   Acessando: ${CONFIG.TJSP_URL}`);
        await page.goto(CONFIG.TJSP_URL, { 
            waitUntil: 'networkidle2',
            timeout: CONFIG.TIMEOUT 
        });
        
        // Preencher formulário de busca
        await preencherFormularioBusca(page, filtros);
        
        // Clicar no botão de busca
        await page.click('#btnPesquisar, button[type="submit"]');
        
        // Aguardar resultados
        await page.waitForSelector('.resultado, #listagem, table', { 
            timeout: CONFIG.TIMEOUT 
        });
        
        // Extrair dados
        const processos = await extrairDadosPagina(page, filtros);
        
        console.log(`✅ ${processos.length} processos encontrados no TJ-SP`);
        
        // Salvar no cache
        cache.set(cacheKey, processos);
        
        return processos;
        
    } catch (error) {
        console.error('❌ Erro no scraping TJ-SP:', error.message);
        return [];
    } finally {
        if (browser) await browser.close();
    }
}

async function preencherFormularioBusca(page, filtros) {
    try {
        // Valor mínimo
        if (filtros.valorMinimo) {
            await page.type('#valorMinimo, input[name="valorMin"]', filtros.valorMinimo);
        }
        
        // Valor máximo
        if (filtros.valorMaximo) {
            await page.type('#valorMaximo, input[name="valorMax"]', filtros.valorMaximo);
        }
        
        // Natureza
        if (filtros.natureza) {
            await page.select('#natureza, select[name="natureza"]', filtros.natureza);
        }
        
        // Ano
        if (filtros.anoLOA) {
            await page.select('#ano, select[name="ano"]', filtros.anoLOA);
        }
        
        console.log('   ✅ Formulário preenchido');
    } catch (error) {
        console.log('   ⚠️ Alguns campos não encontrados:', error.message);
    }
}

async function extrairDadosPagina(page, filtros) {
    const html = await page.content();
    const $ = cheerio.load(html);
    const processos = [];
    
    // Seletor para linhas da tabela
    $('table tbody tr, .resultado-item').each((i, elem) => {
        try {
            const $elem = $(elem);
            
            const numero = $elem.find('.numero, td:nth-child(1)').text().trim();
            const credor = $elem.find('.credor, td:nth-child(2)').text().trim();
            const valorTexto = $elem.find('.valor, td:nth-child(3)').text().trim();
            const natureza = $elem.find('.natureza, td:nth-child(4)').text().trim();
            const ano = $elem.find('.ano, td:nth-child(5)').text().trim();
            
            // Limpar e converter valor
            const valor = parseFloat(valorTexto.replace(/[^\d,]/g, '').replace(',', '.')) || 0;
            
            if (numero && valor > 0) {
                processos.push({
                    numero: numero,
                    tribunal: filtros.tribunal || 'TJ-SP',
                    credor: credor || 'Não informado',
                    valor: valor,
                    status: 'Em Análise',
                    natureza: natureza || filtros.natureza || 'Comum',
                    anoLOA: parseInt(ano) || parseInt(filtros.anoLOA) || new Date().getFullYear(),
                    dataDistribuicao: 'Consultar processo',
                    fonte: 'TJ-SP ESAJ (Real)'
                });
            }
        } catch (err) {
            console.log('   ⚠️ Erro ao processar linha:', err.message);
        }
    });
    
    return processos;
}

// ============================================
// BUSCA NA API DATAJUD CNJ (OFICIAL)
// ============================================

async function buscarDataJudCNJ(filtros) {
    const cacheKey = `datajud_${JSON.stringify(filtros)}`;
    const cached = cache.get(cacheKey);
    
    if (cached) {
        console.log('✅ Retornando resultados do cache');
        return cached;
    }
    
    console.log('🔍 Consultando API DataJud CNJ...');
    
    const tribunalPaths = {
        'TJ-SP': 'api_publica_tjsp',
        'TJ-RJ': 'api_publica_tjrj',
        'TJ-MG': 'api_publica_tjmg',
        'TJ-RS': 'api_publica_tjrs',
        'TJ-PR': 'api_publica_tjpr'
    };
    
    const path = tribunalPaths[filtros.tribunal] || 'api_publica_tjsp';
    const url = `https://api-publica.datajud.cnj.jus.br/${path}/_search`;
    
    const query = {
        size: Math.min(parseInt(filtros.quantidade) || 50, 100),
        query: {
            bool: {
                must: [
                    { exists: { field: "valorCausa" } }
                ],
                filter: []
            }
        },
        sort: [{ "dataAjuizamento": { "order": "desc" } }]
    };
    
    // Filtro de valor
    if (filtros.valorMinimo || filtros.valorMaximo) {
        const rangeQuery = { range: { valorCausa: {} } };
        if (filtros.valorMinimo) rangeQuery.range.valorCausa.gte = parseFloat(filtros.valorMinimo);
        if (filtros.valorMaximo) rangeQuery.range.valorCausa.lte = parseFloat(filtros.valorMaximo);
        query.query.bool.filter.push(rangeQuery);
    }
    
    try {
        const response = await axios.post(url, query, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'APIKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=='
            },
            timeout: CONFIG.TIMEOUT
        });
        
        if (response.data.hits && response.data.hits.hits) {
            const processos = response.data.hits.hits.map(hit => ({
                numero: hit._source.numeroProcesso,
                tribunal: filtros.tribunal,
                credor: extrairCredor(hit._source),
                valor: parseFloat(hit._source.valorCausa || 0),
                status: 'Em Análise',
                natureza: extrairNatureza(hit._source),
                anoLOA: extrairAnoLOA(hit._source),
                dataDistribuicao: formatarData(hit._source.dataAjuizamento),
                fonte: 'DataJud CNJ (Real)'
            }));
            
            console.log(`✅ ${processos.length} processos encontrados no DataJud`);
            cache.set(cacheKey, processos);
            return processos;
        }
        
        return [];
        
    } catch (error) {
        console.error('❌ Erro na API DataJud:', error.message);
        return [];
    }
}

function extrairCredor(source) {
    if (source.polo?.polo) {
        const poloAtivo = source.polo.polo.find(p => p.polo === 'Ativo');
        if (poloAtivo?.partes?.[0]?.nome) {
            return poloAtivo.partes[0].nome;
        }
    }
    return 'Não informado';
}

function extrairNatureza(source) {
    if (!source.assunto) return 'Comum';
    const assunto = Array.isArray(source.assunto) ? source.assunto[0] : source.assunto;
    const texto = (typeof assunto === 'string' ? assunto : '').toLowerCase();
    
    if (texto.includes('aliment')) return 'Alimentar';
    if (texto.includes('tribut')) return 'Tributária';
    if (texto.includes('previd')) return 'Previdenciária';
    if (texto.includes('trabalh')) return 'Trabalhista';
    return 'Comum';
}

function extrairAnoLOA(source) {
    if (source.dataAjuizamento) {
        const ano = parseInt(source.dataAjuizamento.substring(0, 4));
        return ano + 2;
    }
    return new Date().getFullYear() + 1;
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
// BUSCA COM RETRY E FALLBACK
// ============================================

async function buscarProcessosReais(filtros) {
    console.log(`\n🔍 BUSCA REAL INICIADA`);
    console.log(`   Tribunal: ${filtros.tribunal}`);
    console.log(`   Valor: ${filtros.valorMinimo} - ${filtros.valorMaximo}`);
    console.log(`   Natureza: ${filtros.natureza || 'Todas'}`);
    
    let processos = [];
    let fonte = 'nenhuma';
    
    // Tentativa 1: API DataJud (mais rápida)
    try {
        console.log('\n🔹 Tentativa 1: API DataJud CNJ');
        processos = await buscarDataJudCNJ(filtros);
        if (processos.length > 0) {
            fonte = 'DataJud CNJ';
            return { processos, fonte };
        }
    } catch (error) {
        console.log('   ❌ DataJud falhou:', error.message);
    }
    
    // Tentativa 2: Scraping TJ-SP (mais confiável)
    try {
        console.log('\n🔹 Tentativa 2: Scraping TJ-SP ESAJ');
        processos = await buscarPrecatoriosTJSP(filtros);
        if (processos.length > 0) {
            fonte = 'TJ-SP ESAJ';
            return { processos, fonte };
        }
    } catch (error) {
        console.log('   ❌ Scraping falhou:', error.message);
    }
    
    // Fallback: Aviso
    console.log('\n⚠️ Nenhuma fonte disponível no momento');
    console.log('💡 Sugestão: Importe planilha com dados reais');
    
    return { 
        processos: [], 
        fonte: 'indisponível',
        mensagem: 'Tribunais temporariamente indisponíveis. Use a importação de planilha.'
    };
}

module.exports = { buscarProcessosReais };
