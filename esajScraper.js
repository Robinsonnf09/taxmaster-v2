// esajScraper.js - Integração API CNJ + DEPRE + ESAJ
const axios = require('axios');
const { buscarEEnriquecer } = require('./depre-esaj-scraper');

const CNJ_API_URL = process.env.CNJ_API_URL || 'https://api-publica.datajud.cnj.jus.br';
const CNJ_API_KEY = process.env.CNJ_API_KEY || 'cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==';

async function buscarProcessosESAJ(params) {
  const { valorMin, valorMax, natureza, anoLoa, status, quantidade = 30 } = params;

  console.log('\n╔═══════════════════════════════════════════════════════╗');
  console.log('║  🔍 BUSCA HÍBRIDA: API CNJ + DEPRE + ESAJ           ║');
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
    enriquecidos: 0,
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
    
    dadosAPI.forEach(processo => {
      const validacao = validarNumeroProcessoCNJ(processo.numero);
      
      if (validacao.valido) {
        processosReais.push({
          ...processo,
          fonteOriginal: '✅ API CNJ DataJud (OFICIAL)',
          tipoFonte: '🟢 OFICIAL'
        });
        estatisticas.validosAPI++;
      } else {
        console.log(`   ⚠️ Processo inválido descartado: ${processo.numero}`);
        estatisticas.invalidosDescartados++;
      }
    });
    
    estatisticas.apiCNJ = dadosAPI.length;
    
    console.log(`   ✅ Processos válidos: ${estatisticas.validosAPI}`);
    console.log(`   ❌ Processos inválidos: ${estatisticas.invalidosDescartados}\n`);
    
  } catch (error) {
    console.log(`   ❌ Erro na API CNJ: ${error.message}\n`);
  }

  // ============================================
  // ETAPA 2: WEB SCRAPING DEPRE + ESAJ
  // ============================================
  if (processosReais.length < quantidade) {
    try {
      console.log('╔═══════════════════════════════════════════════════════╗');
      console.log('║  🌐 ETAPA 2: Web Scraping DEPRE + ESAJ              ║');
      console.log('╚═══════════════════════════════════════════════════════╝\n');
      
      const qtdNecessaria = quantidade - processosReais.length;
      const dadosDEPRE = await buscarEEnriquecer(qtdNecessaria, params);
      
      console.log(`   📊 Processos do DEPRE: ${dadosDEPRE.length}`);
      
      dadosDEPRE.forEach(processo => {
        const validacao = validarNumeroProcessoCNJ(processo.numero);
        
        if (validacao.valido) {
          processosReais.push(processo);
          estatisticas.validosDEPRE++;
          
          if (processo.fontesUtilizadas && processo.fontesUtilizadas.includes('ESAJ')) {
            estatisticas.enriquecidos++;
          }
        } else {
          console.log(`   ⚠️ Processo DEPRE inválido: ${processo.numero}`);
          estatisticas.invalidosDescartados++;
        }
      });
      
      estatisticas.depre = dadosDEPRE.length;
      
      console.log(`   ✅ Processos válidos do DEPRE: ${estatisticas.validosDEPRE}`);
      console.log(`   ✅ Enriquecidos com ESAJ: ${estatisticas.enriquecidos}\n`);
      
    } catch (error) {
      console.log(`   ❌ Erro no scraping DEPRE/ESAJ: ${error.message}\n`);
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
    if (valorMin && p.valor > 0 && p.valor < valorMin) return false;
    if (valorMax && p.valor > 0 && p.valor > valorMax) return false;
    if (natureza && natureza !== 'Todas' && p.natureza !== natureza) return false;
    if (anoLoa && anoLoa !== 'Todos' && parseInt(anoLoa) !== p.anoLOA) return false;
    if (status === 'Pendente' && p.status !== 'Pendente') return false;
    if (status && status !== 'Todos' && status !== 'Pendente' && p.status !== status) return false;
    return true;
  });

  const resultado = filtrados.slice(0, quantidade);

  console.log(`   ✅ Processos após filtros: ${filtrados.length}`);
  console.log(`   📤 Retornando: ${resultado.length}\n`);

  // ============================================
  // ESTATÍSTICAS FINAIS
  // ============================================
  console.log('╔═══════════════════════════════════════════════════════╗');
  console.log('║  📊 ESTATÍSTICAS FINAIS                               ║');
  console.log('╚═══════════════════════════════════════════════════════╝\n');
  console.log(`   🟢 API CNJ: ${estatisticas.apiCNJ} processos (${estatisticas.validosAPI} válidos)`);
  console.log(`   🟢 Portal DEPRE: ${estatisticas.depre} processos (${estatisticas.validosDEPRE} válidos)`);
  console.log(`   🟢 Enriquecidos ESAJ: ${estatisticas.enriquecidos} processos`);
  console.log(`   ❌ Descartados (inválidos): ${estatisticas.invalidosDescartados}`);
  console.log(`   📊 Total válido: ${processosReais.length}`);
  console.log(`   🔍 Após filtros: ${filtrados.length}`);
  console.log(`   ✅ RETORNADOS: ${resultado.length}\n`);
  
  if (resultado.length > 0) {
    console.log(`   🎉 ${resultado.length} PROCESSOS REAIS RETORNADOS!\n`);
    
    const porFonte = resultado.reduce((acc, p) => {
      const fonte = p.fontesUtilizadas ? p.fontesUtilizadas.join('+') : 'API CNJ';
      acc[fonte] = (acc[fonte] || 0) + 1;
      return acc;
    }, {});
    
    console.log('   📋 RESUMO POR FONTE:');
    Object.entries(porFonte).forEach(([fonte, qtd]) => {
      console.log(`      ${fonte}: ${qtd} processos`);
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
        esajEnriquecidos: estatisticas.enriquecidos
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
      garantia: '✅ DADOS REAIS (API CNJ + DEPRE + ESAJ)'
    }
  };
}

// Funções auxiliares (mantidas do código anterior)
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

function validarNumeroProcessoCNJ(numero) {
  if (!numero) return { valido: false, motivo: 'Número vazio' };
  
  const regex = /^\d{7}-?\d{2}\.?\d{4}\.?\d\.?\d{2}\.?\d{4}$/;
  if (!regex.test(numero.replace(/\s/g, ''))) {
    return { valido: false, motivo: 'Formato inválido' };
  }
  
  const limpo = numero.replace(/\D/g, '');
  const ano = parseInt(limpo.substring(9, 13));
  const segmento = limpo.substring(13, 14);
  const tribunal = limpo.substring(14, 16);
  
  const anoAtual = new Date().getFullYear();
  if (ano < 1988 || ano > anoAtual + 1) {
    return { valido: false, motivo: `Ano inválido: ${ano}` };
  }
  
  if (segmento !== '8') {
    return { valido: false, motivo: 'Não é Justiça Estadual' };
  }
  
  if (tribunal !== '26') {
    return { valido: false, motivo: 'Não é TJ-SP' };
  }
  
  return { valido: true };
}

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

module.exports = { buscarProcessosESAJ };
