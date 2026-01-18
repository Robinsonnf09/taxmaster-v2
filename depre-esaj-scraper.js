// depre-esaj-scraper.js - Web Scraping Real dos Portais Oficiais
const axios = require('axios');
const cheerio = require('cheerio');
const { wrapper } = require('axios-cookiejar-support');
const { CookieJar } = require('tough-cookie');

// Configurar axios com suporte a cookies
const jar = new CookieJar();
const client = wrapper(axios.create({ jar }));

// URLs dos portais oficiais
const DEPRE_BASE_URL = 'https://www.tjsp.jus.br/Depre';
const ESAJ_BASE_URL = 'https://esaj.tjsp.jus.br';

// ============================================
// SCRAPING DO PORTAL DEPRE
// ============================================

async function scrapeDEPRE(quantidade = 30, filtros = {}) {
  console.log(`\n🌐 Iniciando scraping Portal DEPRE (TJ-SP)...`);
  console.log(`   URL: ${DEPRE_BASE_URL}/Pesquisas/PesquisaPublica`);
  
  const processos = [];
  
  try {
    // PASSO 1: Acessar página de consulta
    const urlConsulta = `${DEPRE_BASE_URL}/Pesquisas/PesquisaPublica`;
    
    console.log(`   📡 Acessando portal DEPRE...`);
    
    const response = await client.get(urlConsulta, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
      },
      timeout: 30000,
      maxRedirects: 5
    });

    console.log(`   ✅ Status: ${response.status}`);
    
    const $ = cheerio.load(response.data);
    
    // PASSO 2: Extrair token de sessão (se houver)
    const viewState = $('input[name="__VIEWSTATE"]').val();
    const eventValidation = $('input[name="__EVENTVALIDATION"]').val();
    
    console.log(`   🔑 ViewState: ${viewState ? 'Encontrado' : 'Não encontrado'}`);
    
    // PASSO 3: Realizar busca de precatórios
    const formData = {
      '__VIEWSTATE': viewState || '',
      '__EVENTVALIDATION': eventValidation || '',
      'ctl00$conteudoPagina$txtNumeroProcesso': '',
      'ctl00$conteudoPagina$txtNomeCredor': '',
      'ctl00$conteudoPagina$ddlNatureza': filtros.natureza === 'Alimentar' ? 'A' : 
                                           filtros.natureza === 'Comum' ? 'C' : '',
      'ctl00$conteudoPagina$txtAnoLOA': filtros.anoLoa || '',
      'ctl00$conteudoPagina$btnPesquisar': 'Pesquisar'
    };
    
    console.log(`   🔍 Executando busca com filtros...`);
    
    const searchResponse = await client.post(urlConsulta, formData, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': urlConsulta
      },
      timeout: 30000
    });

    const $results = cheerio.load(searchResponse.data);
    
    // PASSO 4: Extrair dados da tabela de resultados
    const linhas = $results('table.gridResultado tbody tr, table#GridView1 tbody tr, table[id*="Grid"] tbody tr');
    
    console.log(`   📊 Linhas encontradas na tabela: ${linhas.length}`);
    
    linhas.each((index, element) => {
      if (processos.length >= quantidade) return false;
      
      const cols = $results(element).find('td');
      
      if (cols.length >= 6) {
        const numeroProcesso = $results(cols[0]).text().trim();
        const credor = $results(cols[1]).text().trim();
        const valorStr = $results(cols[2]).text().trim();
        const natureza = $results(cols[3]).text().trim();
        const anoLOAStr = $results(cols[4]).text().trim();
        const status = $results(cols[5]).text().trim();
        
        // Validar número de processo
        if (!numeroProcesso || numeroProcesso.length < 15) {
          console.log(`   ⚠️ Processo inválido ignorado: ${numeroProcesso}`);
          return;
        }
        
        const valor = parseValorMonetario(valorStr);
        const anoLOA = parseInt(anoLOAStr) || new Date().getFullYear() + 1;
        
        processos.push({
          numero: numeroProcesso,
          tribunal: 'TJ-SP',
          credor: credor || 'Não informado',
          valor: valor,
          classe: 'Precatório',
          assunto: 'Requisição de Pagamento',
          dataDistribuicao: extrairDataDoNumero(numeroProcesso),
          comarca: 'São Paulo',
          vara: extrairVaraDoNumero(numeroProcesso),
          natureza: mapearNatureza(natureza),
          anoLOA: anoLOA,
          status: mapearStatus(status),
          fonte: '✅ Portal DEPRE TJ-SP (OFICIAL - WEB SCRAPING)',
          fonteOriginal: 'Portal DEPRE TJ-SP',
          tipoFonte: '🟢 OFICIAL',
          detalhesExtras: {
            statusDEPRE: status,
            naturezaDEPRE: natureza
          }
        });
        
        console.log(`   ✅ Processo ${index + 1}: ${numeroProcesso} - R$ ${valor.toLocaleString('pt-BR')}`);
      }
    });
    
    console.log(`\n   ✅ Total extraído do DEPRE: ${processos.length} processos\n`);
    
    return processos;
    
  } catch (error) {
    console.log(`   ❌ Erro no scraping DEPRE: ${error.message}`);
    
    // Tentar método alternativo
    if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
      console.log(`   🔄 Tentando método alternativo...`);
      return await scrapeDEPREAlternativo(quantidade, filtros);
    }
    
    return [];
  }
}

// ============================================
// MÉTODO ALTERNATIVO - DEPRE (API Interna)
// ============================================

async function scrapeDEPREAlternativo(quantidade, filtros) {
  console.log(`   📡 Método alternativo: API interna DEPRE...`);
  
  try {
    // Alguns portais do TJ-SP expõem APIs internas
    const apiUrl = `${DEPRE_BASE_URL}/api/ConsultaPrecatorios`;
    
    const response = await client.get(apiUrl, {
      params: {
        natureza: filtros.natureza,
        anoLOA: filtros.anoLoa,
        limite: quantidade
      },
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'application/json'
      },
      timeout: 15000
    });
    
    if (response.data && Array.isArray(response.data)) {
      console.log(`   ✅ API retornou ${response.data.length} processos`);
      return response.data.map(p => processarDadosDEPREAPI(p));
    }
    
    return [];
    
  } catch (error) {
    console.log(`   ⚠️ API alternativa não disponível: ${error.message}`);
    return [];
  }
}

// ============================================
// SCRAPING DO ESAJ (Detalhes do Processo)
// ============================================

async function enriquecerComESAJ(processo) {
  console.log(`   🔍 Buscando detalhes no ESAJ: ${processo.numero}`);
  
  try {
    const numeroLimpo = processo.numero.replace(/\D/g, '');
    const urlConsulta = `${ESAJ_BASE_URL}/cpopg/show.do`;
    
    const response = await client.get(urlConsulta, {
      params: {
        processo: {
          codigo: numeroLimpo
        },
        conversationId: '',
        dadosConsulta: {
          localPesquisa: {
            cdLocal: '-1'
          },
          numeroDigitoAnoUnificado: numeroLimpo.substring(0, 15),
          foroNumeroUnificado: numeroLimpo.substring(15, 19)
        }
      },
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'text/html,application/xhtml+xml'
      },
      timeout: 20000
    });

    const $ = cheerio.load(response.data);
    
    // Extrair informações adicionais
    const valorCausaTexto = $('#valorAcaoProcesso').text().trim();
    const assunto = $('#assuntoProcesso').text().trim();
    const classe = $('#classeProcesso').text().trim();
    const vara = $('#varaProcesso').text().trim();
    const comarca = $('#comarcaProcesso').text().trim();
    
    // Extrair partes (credores)
    const credores = [];
    $('#tableTodasPartes tr').each((i, el) => {
      const tipo = $(el).find('td:nth-child(1)').text().trim();
      const nome = $(el).find('td:nth-child(2)').text().trim();
      
      if (tipo.match(/autor|exequente|requerente/i) && nome) {
        credores.push(nome);
      }
    });
    
    // Extrair movimentações (para detectar ofício requisitório)
    const movimentacoes = [];
    $('#tabelaTodasMovimentacoes tr, #tabelaUltimasMovimentacoes tr').each((i, el) => {
      const data = $(el).find('td:nth-child(1)').text().trim();
      const descricao = $(el).find('td:nth-child(2), td:nth-child(3)').text().trim();
      
      if (descricao) {
        movimentacoes.push({ data, descricao });
      }
    });
    
    // Detectar ofício requisitório e valor atualizado
    let valorAtualizado = processo.valor;
    let temOficio = false;
    
    movimentacoes.forEach(mov => {
      if (mov.descricao.match(/ofício.*requisitório|precatório.*expedido|requisição.*pagamento/i)) {
        temOficio = true;
        
        // Tentar extrair valor do movimento
        const valorMatch = mov.descricao.match(/R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)/);
        if (valorMatch) {
          const valor = parseValorMonetario(valorMatch[1]);
          if (valor > valorAtualizado) {
            valorAtualizado = valor;
          }
        }
      }
    });
    
    console.log(`   ✅ Dados enriquecidos: Credor=${credores[0] || 'não encontrado'}, Valor=${valorAtualizado}`);
    
    return {
      ...processo,
      credor: credores[0] || processo.credor,
      valor: valorAtualizado,
      classe: classe || processo.classe,
      assunto: assunto || processo.assunto,
      vara: vara || processo.vara,
      comarca: comarca || processo.comarca,
      valorAtualizado: valorAtualizado,
      valorOriginal: processo.valor,
      temOficioRequisitorio: temOficio,
      movimentacoes: movimentacoes.slice(0, 5),
      fonte: processo.fonte + ' + ESAJ',
      fontesUtilizadas: ['DEPRE', 'ESAJ']
    };
    
  } catch (error) {
    console.log(`   ⚠️ Erro ao acessar ESAJ: ${error.message}`);
    return processo; // Retorna processo original sem enriquecimento
  }
}

// ============================================
// FUNÇÃO PRINCIPAL: BUSCAR E ENRIQUECER
// ============================================

async function buscarEEnriquecer(quantidade, filtros) {
  console.log(`\n╔═══════════════════════════════════════════════════════╗`);
  console.log(`║  🌐 WEB SCRAPING PORTAIS OFICIAIS                    ║`);
  console.log(`╚═══════════════════════════════════════════════════════╝\n`);
  
  // ETAPA 1: Scraping DEPRE
  const processosDEPRE = await scrapeDEPRE(quantidade, filtros);
  
  if (processosDEPRE.length === 0) {
    console.log(`   ⚠️ Nenhum processo encontrado no DEPRE`);
    return [];
  }
  
  // ETAPA 2: Enriquecer com dados do ESAJ (com rate limiting)
  console.log(`\n🔍 Enriquecendo dados com ESAJ...`);
  console.log(`   ⏱️ Rate limiting: 2s entre requisições\n`);
  
  const processosEnriquecidos = [];
  
  for (let i = 0; i < processosDEPRE.length && i < 10; i++) {
    const processo = processosDEPRE[i];
    
    try {
      const enriquecido = await enriquecerComESAJ(processo);
      processosEnriquecidos.push(enriquecido);
      
      // Rate limiting: aguardar 2 segundos entre requisições
      if (i < processosDEPRE.length - 1) {
        await delay(2000);
      }
      
    } catch (error) {
      console.log(`   ⚠️ Falha ao enriquecer ${processo.numero}: ${error.message}`);
      processosEnriquecidos.push(processo); // Adiciona sem enriquecimento
    }
  }
  
  // Adicionar processos restantes sem enriquecimento
  if (processosDEPRE.length > 10) {
    console.log(`\n   ℹ️ Adicionando ${processosDEPRE.length - 10} processos sem enriquecimento ESAJ (limite de rate)`);
    processosEnriquecidos.push(...processosDEPRE.slice(10));
  }
  
  console.log(`\n✅ Total de processos coletados e enriquecidos: ${processosEnriquecidos.length}\n`);
  
  return processosEnriquecidos;
}

// ============================================
// FUNÇÕES AUXILIARES
// ============================================

function parseValorMonetario(str) {
  if (!str) return 0;
  
  // Remove tudo exceto números, vírgulas e pontos
  const limpo = str.replace(/[^\d,\.]/g, '');
  
  // Formato brasileiro: 1.234.567,89
  if (limpo.includes(',')) {
    return parseFloat(limpo.replace(/\./g, '').replace(',', '.')) || 0;
  }
  
  // Formato americano: 1,234,567.89
  return parseFloat(limpo.replace(/,/g, '')) || 0;
}

function extrairDataDoNumero(numero) {
  // Formato CNJ: NNNNNNN-DD.AAAA.J.TR.OOOO
  const ano = numero.substring(11, 15);
  return ano ? `${ano}-01-01` : new Date().toISOString().split('T')[0];
}

function extrairVaraDoNumero(numero) {
  // Extrair código da vara do número CNJ
  const origem = numero.substring(18, 22);
  return `Vara de origem: ${origem}`;
}

function mapearNatureza(naturezaDEPRE) {
  const nat = (naturezaDEPRE || '').toLowerCase();
  
  if (nat.includes('alimentar') || nat.includes('aliment')) return 'Alimentar';
  if (nat.includes('tributár') || nat.includes('tribut') || nat.includes('fiscal')) return 'Tributária';
  if (nat.includes('previdenciár') || nat.includes('previd')) return 'Previdenciária';
  
  return 'Comum';
}

function mapearStatus(statusDEPRE) {
  const status = (statusDEPRE || '').toLowerCase();
  
  if (status.includes('pago') || status.includes('quitado')) return 'Pago';
  if (status.includes('pendente') || status.includes('aguardando')) return 'Pendente';
  if (status.includes('requisitado') || status.includes('expedido')) return 'Pendente';
  
  return 'Em Análise';
}

function processarDadosDEPREAPI(dados) {
  return {
    numero: dados.numeroProcesso || dados.numero,
    tribunal: 'TJ-SP',
    credor: dados.nomeCredor || dados.credor || 'Não informado',
    valor: dados.valorRequisicao || dados.valor || 0,
    classe: 'Precatório',
    assunto: 'Requisição de Pagamento',
    dataDistribuicao: dados.dataDistribuicao || extrairDataDoNumero(dados.numeroProcesso),
    comarca: dados.comarca || 'São Paulo',
    vara: dados.vara || 'Não informado',
    natureza: mapearNatureza(dados.natureza),
    anoLOA: dados.anoLOA || new Date().getFullYear() + 1,
    status: mapearStatus(dados.status),
    fonte: '✅ Portal DEPRE TJ-SP API (OFICIAL)',
    fonteOriginal: 'Portal DEPRE TJ-SP API',
    tipoFonte: '🟢 OFICIAL'
  };
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ============================================
// EXPORTAR
// ============================================

module.exports = {
  scrapeDEPRE,
  enriquecerComESAJ,
  buscarEEnriquecer
};
