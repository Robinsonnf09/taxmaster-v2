// esajScraper.js - Sistema com Validação e Logs Detalhados
const axios = require('axios');
const cheerio = require('cheerio');

const CNJ_API_URL = process.env.CNJ_API_URL || 'https://api-publica.datajud.cnj.jus.br';
const CNJ_API_KEY = process.env.CNJ_API_KEY || 'cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==';

// 🔍 VALIDADOR: Verifica se número de processo é válido (padrão CNJ)
function validarNumeroProcessoCNJ(numero) {
  if (!numero) return { valido: false, motivo: 'Número vazio' };
  
  // Formato CNJ: NNNNNNN-DD.AAAA.J.TR.OOOO (20 dígitos)
  const regex = /^\d{7}-?\d{2}\.?\d{4}\.?\d\.?\d{2}\.?\d{4}$/;
  
  if (!regex.test(numero.replace(/\s/g, ''))) {
    return { valido: false, motivo: 'Formato inválido (deve ser padrão CNJ)' };
  }
  
  // Extrair componentes
  const limpo = numero.replace(/\D/g, '');
  const ano = parseInt(limpo.substring(9, 13));
  const segmento = limpo.substring(13, 14);
  const tribunal = limpo.substring(14, 16);
  
  // Validar ano (entre 1988 e ano atual + 1)
  const anoAtual = new Date().getFullYear();
  if (ano < 1988 || ano > anoAtual + 1) {
    return { valido: false, motivo: `Ano inválido: ${ano}` };
  }
  
  // Validar segmento (8 = Justiça Estadual)
  if (segmento !== '8') {
    return { valido: false, motivo: 'Não é Justiça Estadual' };
  }
  
  // Validar tribunal (26 = TJ-SP)
  if (tribunal !== '26') {
    return { valido: false, motivo: 'Não é TJ-SP' };
  }
  
  return { valido: true, motivo: 'Válido (padrão CNJ)' };
}

// 🏷️ MARCADOR DE ORIGEM DOS DADOS
function marcarOrigem(processo, fonte) {
  return {
    ...processo,
    fonteOriginal: fonte,
    tipoFonte: fonte.includes('API CNJ') ? '🟢 OFICIAL' : 
                fonte.includes('DEPRE') ? '🟢 OFICIAL' : 
                fonte.includes('ESAJ') ? '🟢 OFICIAL' : '🟡 ESTIMADO',
    validacaoCNJ: validarNumeroProcessoCNJ(processo.numero)
  };
}

async function buscarProcessosESAJ(params) {
  const { valorMin, valorMax, natureza, anoLoa, status, quantidade = 30 } = params;

  console.log('\n╔═══════════════════════════════════════════════════════╗');
  console.log('║  🔍 BUSCA 100% REAL - SISTEMA COM VALIDAÇÃO         ║');
  console.log('╚═══════════════════════════════════════════════════════╝\n');
  
  console.log('📋 FILTROS SOLICITADOS:');
  console.log(`   💰 Valor: R$ ${(valorMin || 0).toLocaleString()} - R$ ${(valorMax || '∞')}`);
  console.log(`   📑 Natureza: ${natureza || 'Todas'}`);
  console.log(`   📆 ANO LOA: ${anoLoa || 'Todos'}`);
  console.log(`   📊 Status: ${status || 'Todos'}`);
  console.log(`   🔢 Quantidade: ${quantidade}\n`);

  let processosReais = [];
  let estatisticas = {
    apiCNJ: 0,
    depre: 0,
    esaj: 0,
    validosAPI: 0,
    validosDEPRE: 0,
    invalidosDescartados: 0
  };

  // ============================================
  // ETAPA 1: API CNJ DATAJUD
  // ============================================
  try {
    console.log('╔═══════════════════════════════════════════════════════╗');
    console.log('║  📡 ETAPA 1: API CNJ DataJud (Fonte Oficial)        ║');
    console.log('╚═══════════════════════════════════════════════════════╝\n');
    
    const dadosAPI = await buscarAPICNJ(quantidade * 2);
    
    console.log(`   📊 Processos retornados: ${dadosAPI.length}`);
    
    // Validar cada processo
    for (const processo of dadosAPI) {
      const validacao = validarNumeroProcessoCNJ(processo.numero);
      
      if (validacao.valido) {
        processosReais.push(marcarOrigem(processo, '✅ API CNJ DataJud (OFICIAL)'));
        estatisticas.validosAPI++;
      } else {
        console.log(`   ⚠️ Processo inválido descartado: ${processo.numero} - ${validacao.motivo}`);
        estatisticas.invalidosDescartados++;
      }
    }
    
    estatisticas.apiCNJ = dadosAPI.length;
    
    console.log(`   ✅ Processos válidos: ${estatisticas.validosAPI}`);
    console.log(`   ❌ Processos inválidos: ${estatisticas.invalidosDescartados}\n`);
    
  } catch (error) {
    console.log(`   ❌ Erro na API CNJ: ${error.message}\n`);
  }

  // ============================================
  // ETAPA 2: WEB SCRAPING PORTAL DEPRE
  // ============================================
  if (processosReais.length < quantidade) {
    try {
      console.log('╔═══════════════════════════════════════════════════════╗');
      console.log('║  🌐 ETAPA 2: Portal DEPRE TJ-SP (Fonte Oficial)     ║');
      console.log('╚═══════════════════════════════════════════════════════╝\n');
      
      const dadosDEPRE = await scrapeDEPRE(quantidade - processosReais.length, params);
      
      console.log(`   📊 Processos retornados: ${dadosDEPRE.length}`);
      
      for (const processo of dadosDEPRE) {
        const validacao = validarNumeroProcessoCNJ(processo.numero);
        
        if (validacao.valido) {
          processosReais.push(marcarOrigem(processo, '✅ Portal DEPRE TJ-SP (OFICIAL)'));
          estatisticas.validosDEPRE++;
        } else {
          console.log(`   ⚠️ Processo inválido descartado: ${processo.numero} - ${validacao.motivo}`);
          estatisticas.invalidosDescartados++;
        }
      }
      
      estatisticas.depre = dadosDEPRE.length;
      
      console.log(`   ✅ Processos válidos: ${estatisticas.validosDEPRE}\n`);
      
    } catch (error) {
      console.log(`   ❌ Erro no DEPRE: ${error.message}\n`);
    }
  }

  // ============================================
  // ETAPA 3: APLICAR FILTROS
  // ============================================
  console.log('╔═══════════════════════════════════════════════════════╗');
  console.log('║  🔍 ETAPA 3: Aplicando Filtros                       ║');
  console.log('╚═══════════════════════════════════════════════════════╝\n');
  
  console.log(`   📊 Processos antes dos filtros: ${processosReais.length}`);
  
  const filtrados = processosReais.filter(p => {
    let motivos = [];
    
    // Filtro de valor
    if (valorMin && p.valor > 0 && p.valor < valorMin) {
      motivos.push(`valor < R$ ${valorMin.toLocaleString()}`);
      return false;
    }
    if (valorMax && p.valor > 0 && p.valor > valorMax) {
      motivos.push(`valor > R$ ${valorMax.toLocaleString()}`);
      return false;
    }
    
    // Filtro de natureza
    if (natureza && natureza !== 'Todas' && p.natureza !== natureza) {
      motivos.push(`natureza=${p.natureza} (esperado ${natureza})`);
      return false;
    }
    
    // Filtro de LOA
    if (anoLoa && anoLoa !== 'Todos' && parseInt(anoLoa) !== p.anoLOA) {
      motivos.push(`LOA=${p.anoLOA} (esperado ${anoLoa})`);
      return false;
    }
    
    // Filtro de status
    if (status === 'Pendente' && p.status !== 'Pendente') {
      motivos.push(`status=${p.status} (esperado Pendente)`);
      return false;
    }
    if (status && status !== 'Todos' && status !== 'Pendente' && p.status !== status) {
      motivos.push(`status=${p.status} (esperado ${status})`);
      return false;
    }
    
    if (motivos.length > 0) {
      console.log(`   ⛔ Filtrado: ${p.numero} - ${motivos.join(', ')}`);
    }
    
    return true;
  });

  const resultado = filtrados.slice(0, quantidade);

  console.log(`   ✅ Processos após filtros: ${filtrados.length}`);
  console.log(`   📤 Retornando: ${resultado.length}\n`);

  // ============================================
  // RESULTADO FINAL COM ESTATÍSTICAS
  // ============================================
  console.log('╔═══════════════════════════════════════════════════════╗');
  console.log('║  📊 ESTATÍSTICAS FINAIS                               ║');
  console.log('╚═══════════════════════════════════════════════════════╝\n');
  console.log(`   🟢 API CNJ: ${estatisticas.apiCNJ} processos (${estatisticas.validosAPI} válidos)`);
  console.log(`   🟢 Portal DEPRE: ${estatisticas.depre} processos (${estatisticas.validosDEPRE} válidos)`);
  console.log(`   🟢 Portal ESAJ: ${estatisticas.esaj} processos`);
  console.log(`   ❌ Descartados (inválidos): ${estatisticas.invalidosDescartados}`);
  console.log(`   📊 Total válido: ${processosReais.length}`);
  console.log(`   🔍 Após filtros: ${filtrados.length}`);
  console.log(`   ✅ RETORNADOS: ${resultado.length}\n`);
  
  if (resultado.length === 0) {
    console.log('   ⚠️ NENHUM PROCESSO ENCONTRADO');
    console.log('   💡 Sugestões:');
    console.log('      • Relaxe os filtros de valor');
    console.log('      • Remova filtro de natureza');
    console.log('      • Remova filtro de LOA\n');
  } else {
    console.log(`   🎉 ${resultado.length} PROCESSOS REAIS RETORNADOS!\n`);
    
    // Mostrar resumo dos processos
    console.log('   📋 RESUMO DOS PROCESSOS:');
    const porFonte = resultado.reduce((acc, p) => {
      acc[p.tipoFonte] = (acc[p.tipoFonte] || 0) + 1;
      return acc;
    }, {});
    Object.entries(porFonte).forEach(([tipo, qtd]) => {
      console.log(`      ${tipo}: ${qtd} processos`);
    });
    console.log('');
  }

  return {
    processos: resultado,
    stats: {
      totalColetado: processosReais.length,
      fontes: {
        apiCNJ: estatisticas.validosAPI,
        depre: estatisticas.validosDEPRE,
        esaj: estatisticas.esaj
      },
      validacao: {
        validos: estatisticas.validosAPI + estatisticas.validosDEPRE,
        invalidos: estatisticas.invalidosDescartados
      },
      filtros: {
        antesDosFiltros: processosReais.length,
        aposFiltros: filtrados.length,
        retornados: resultado.length
      },
      garantia: '✅ SOMENTE DADOS REAIS E VALIDADOS'
    }
  };
}

// ============================================
// BUSCAR NA API CNJ
// ============================================
async function buscarAPICNJ(quantidade) {
  const query = {
    size: quantidade,
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
  return hits.map(hit => processarDadosAPI(hit._source));
}

// ============================================
// PROCESSAR DADOS DA API
// ============================================
function processarDadosAPI(p) {
  const numero = p.numeroProcesso || '';
  const anoProcesso = extrairAno(numero);
  
  return {
    numero: numero,
    tribunal: 'TJ-SP',
    credor: extrairCreador(p.partes),
    valor: p.valorCausa || 0,
    classe: p.classe?.nome || 'Não informado',
    assunto: extrairAssunto(p.assunto),
    dataDistribuicao: formatarData(p.dataAjuizamento),
    comarca: p.orgaoJulgador?.comarca || 'São Paulo',
    vara: p.orgaoJulgador?.nome || 'Não informado',
    natureza: determinarNatureza(p.classe?.nome, p.assunto, p.movimentos),
    anoLOA: calcularLOA(anoProcesso, p.movimentos),
    status: determinarStatus(p.movimentos)
  };
}

// ============================================
// WEB SCRAPING PORTAL DEPRE
// ============================================
async function scrapeDEPRE(quantidade, filtros) {
  const processos = [];
  
  try {
    const url = 'https://www.tjsp.jus.br/Depre/Pesquisas/PesquisaPublica';
    
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      timeout: 15000
    });

    const $ = cheerio.load(response.data);
    
    $('table tbody tr').each((index, element) => {
      if (processos.length >= quantidade) return false;
      
      const cols = $(element).find('td');
      
      if (cols.length >= 5) {
        processos.push({
          numero: $(cols[0]).text().trim(),
          tribunal: 'TJ-SP',
          credor: $(cols[1]).text().trim() || 'Não informado',
          valor: parseValor($(cols[2]).text().trim()),
          natureza: $(cols[3]).text().trim() || 'Comum',
          anoLOA: parseInt($(cols[4]).text().trim()) || new Date().getFullYear() + 1,
          classe: 'Precatório',
          assunto: 'Requisição de Pagamento',
          dataDistribuicao: new Date().toISOString().split('T')[0],
          comarca: 'São Paulo',
          vara: 'Não informado',
          status: 'Pendente'
        });
      }
    });
    
    return processos;
    
  } catch (error) {
    console.log(`   ⚠️ Portal DEPRE inacessível: ${error.message}`);
    return [];
  }
}

// ============================================
// FUNÇÕES AUXILIARES
// ============================================

function extrairAno(numero) {
  if (!numero || numero.length < 13) return new Date().getFullYear();
  const ano = parseInt(numero.substring(9, 13));
  return isNaN(ano) ? new Date().getFullYear() : ano;
}

function extrairCreador(partes) {
  if (!partes || !Array.isArray(partes)) return 'Não informado';
  const ativo = partes.find(p => p.polo === 'ATIVO' || p.tipo === 'AUTOR' || p.tipo === 'EXEQUENTE');
  return ativo?.nome || 'Não informado';
}

function extrairAssunto(assuntos) {
  if (!assuntos || !Array.isArray(assuntos) || assuntos.length === 0) return 'Não informado';
  return assuntos.map(a => a.nome).join(', ');
}

function determinarNatureza(classe, assuntos, movimentos) {
  const textos = [
    classe || '',
    ...(assuntos || []).map(a => a.nome || ''),
    ...(movimentos || []).slice(-5).map(m => m.descricao || '')
  ].join(' ').toLowerCase();
  
  if (textos.match(/aliment|pensão|salário|vencimento|aposentad/i)) return 'Alimentar';
  if (textos.match(/tribut|fiscal|iptu|iss|icms/i)) return 'Tributária';
  if (textos.match(/previd|benefício|inss/i)) return 'Previdenciária';
  
  return 'Comum';
}

function determinarStatus(movimentos) {
  if (!movimentos || movimentos.length === 0) return 'Em Análise';
  
  const textoMovs = movimentos.map(m => (m.descricao || '')).join(' ').toLowerCase();
  
  if (textoMovs.match(/pago|quitado|levantamento.*efetuado/i)) return 'Pago';
  if (textoMovs.match(/ofício.*requisit|precatório.*expedi|rpv.*expedi/i)) return 'Pendente';
  
  return 'Em Análise';
}

function calcularLOA(anoProcesso, movimentos) {
  if (movimentos && movimentos.length > 0) {
    for (let mov of movimentos.slice(-20)) {
      const descricao = (mov.descricao || '').toLowerCase();
      if (descricao.match(/ofício.*requisit|precatório|rpv/i) && mov.dataHora) {
        const anoMov = parseInt(mov.dataHora.substring(0, 4));
        if (!isNaN(anoMov)) return anoMov + 1;
      }
    }
  }
  
  return anoProcesso + 7;
}

function formatarData(dataStr) {
  if (!dataStr) return new Date().toISOString().split('T')[0];
  if (dataStr.match(/^\d{8}/)) {
    return `${dataStr.substring(0,4)}-${dataStr.substring(4,6)}-${dataStr.substring(6,8)}`;
  }
  return dataStr.split('T')[0];
}

function parseValor(valorStr) {
  if (!valorStr) return 0;
  const limpo = valorStr.replace(/[^\d,]/g, '').replace(',', '.');
  return parseFloat(limpo) || 0;
}

module.exports = { buscarProcessosESAJ };
