// esajScraper.js - API CNJ DataJud (busca especializada em ofícios requisitórios)
const axios = require('axios');

const CNJ_API_URL = process.env.CNJ_API_URL || 'https://api-publica.datajud.cnj.jus.br';
const CNJ_API_KEY = process.env.CNJ_API_KEY || 'cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==';

// ✅ Termos que indicam OFÍCIO REQUISITÓRIO EXPEDIDO
const TERMOS_OFICIO_REQUISITORIO = [
  'ofício requisitório',
  'oficio requisitorio',
  'requisição de pagamento',
  'requisicao de pagamento',
  'expedição de precatório',
  'expedicao de precatorio',
  'expedição de rpv',
  'expedicao de rpv',
  'precatório expedido',
  'precatorio expedido',
  'rpv expedido',
  'rpv expedida',
  'requisitória',
  'requisitoria',
  'remessa de precatório',
  'remessa de precatorio',
  'remessa à contadoria',
  'encaminhado para pagamento',
  'remetido ao tribunal',
  'oficiar',
  'requisitar pagamento'
];

// ✅ Termos que indicam PAGAMENTO REALIZADO
const TERMOS_PAGAMENTO = [
  'pago',
  'quitado',
  'quitação',
  'quitacao',
  'pagamento efetuado',
  'pagamento realizado',
  'pagamento concluído',
  'pagamento concluido',
  'levantamento realizado',
  'levantamento efetuado',
  'alvará de levantamento',
  'alvara de levantamento',
  'transferência realizada',
  'transferencia realizada',
  'depósito efetuado',
  'deposito efetuado',
  'crédito disponível',
  'credito disponivel',
  'baixa definitiva',
  'arquivado definitivamente'
];

function extrairAnoDoNumero(numeroProcesso) {
  if (!numeroProcesso || numeroProcesso.length < 13) return null;
  const ano = parseInt(numeroProcesso.substring(9, 13));
  return isNaN(ano) ? null : ano;
}

function calcularAnoLOA(numeroProcesso) {
  const anoAjuizamento = extrairAnoDoNumero(numeroProcesso);
  if (!anoAjuizamento) return new Date().getFullYear() + 1;
  return anoAjuizamento + 2;
}

function determinarNatureza(classe, assuntos) {
  const texto = (classe + ' ' + (assuntos || '')).toLowerCase();
  
  if (texto.includes('tribut') || texto.includes('fiscal') || texto.includes('iptu') || texto.includes('iss')) {
    return 'Tributária';
  }
  if (texto.includes('aliment')) {
    return 'Alimentar';
  }
  if (texto.includes('previd') || texto.includes('aposentad')) {
    return 'Previdenciária';
  }
  
  return 'Comum';
}

// ✅ Verificar se há OFÍCIO REQUISITÓRIO nos movimentos
function temOficioRequisitorio(movimentos) {
  if (!movimentos || movimentos.length === 0) return false;
  
  const textoMovimentos = movimentos
    .map(m => (m.descricao || m.nome || '').toLowerCase())
    .join(' ');
  
  return TERMOS_OFICIO_REQUISITORIO.some(termo => textoMovimentos.includes(termo));
}

// ✅ Verificar se foi PAGO
function foiPago(movimentos) {
  if (!movimentos || movimentos.length === 0) return false;
  
  const textoMovimentos = movimentos
    .map(m => (m.descricao || m.nome || '').toLowerCase())
    .join(' ');
  
  return TERMOS_PAGAMENTO.some(termo => textoMovimentos.includes(termo));
}

// ✅ Determinar status inteligente
function determinarStatus(movimentos, classe) {
  const temOficio = temOficioRequisitorio(movimentos);
  const pago = foiPago(movimentos);
  
  if (pago) {
    return 'Pago';
  }
  
  if (temOficio) {
    return 'Pendente'; // Ofício expedido mas não pago = PENDENTE
  }
  
  // Sem ofício e sem pagamento
  return 'Em Análise';
}

function processarHit(hit) {
  const p = hit._source;
  
  const numero = p.numeroProcesso || 'Não informado';
  const classe = p.classe?.nome || 'Não informado';
  const orgao = p.orgaoJulgador?.nome || 'Não informado';
  const assuntos = Array.isArray(p.assunto) ? p.assunto.map(a => a.nome).join(', ') : '';
  const dataAjuizamento = p.dataAjuizamento || p.dataHoraUltimaAtualizacao || 'Não informado';
  const movimentos = p.movimentos || [];
  
  const anoLOA = calcularAnoLOA(numero);
  const natureza = determinarNatureza(classe, assuntos);
  const status = determinarStatus(movimentos, classe);
  const valor = p.valorCausa || 0;
  
  const temOficio = temOficioRequisitorio(movimentos);
  const pago = foiPago(movimentos);
  
  return {
    numero: numero,
    tribunal: 'TJ-SP',
    credor: 'A definir',
    valor: valor,
    classe: classe,
    assunto: assuntos || orgao,
    dataDistribuicao: dataAjuizamento,
    comarca: 'São Paulo',
    vara: orgao,
    natureza: natureza,
    anoLOA: anoLOA,
    anoAjuizamento: extrairAnoDoNumero(numero),
    status: status,
    temOficioRequisitorio: temOficio,
    foiPago: pago,
    fonte: 'API CNJ DataJud'
  };
}

async function buscarProcessosESAJ(params) {
  const { valorMin, valorMax, natureza, anoLoa, status, quantidade = 50 } = params;

  console.log('\n🔍 BUSCA NA API CNJ DATAJUD (OFICIAL)');
  console.log(`   🎯 MODO: Ofícios Requisitórios Pendentes`);
  console.log(`   URL: ${CNJ_API_URL}`);
  console.log(`   Filtros solicitados:`);
  console.log(`     Valor: ${valorMin || 0} - ${valorMax || '∞'}`);
  console.log(`     Natureza: ${natureza || 'Todas'}`);
  console.log(`     ANO LOA: ${anoLoa || 'Todos'}`);
  console.log(`     Status: ${status || 'Todos'}`);
  console.log(`     Quantidade: ${quantidade}`);

  try {
    // Buscar muito mais para encontrar processos com ofícios
    const query = {
      size: quantidade * 5,
      query: {
        match_all: {}
      },
      sort: [
        { 'dataHoraUltimaAtualizacao': { order: 'desc' } }
      ]
    };

    console.log(`   📤 Enviando requisição para CNJ...`);

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

    console.log(`   📥 Status: ${response.status}`);

    if (!response.data?.hits?.hits) {
      console.log('   ⚠️ Resposta vazia\n');
      return { processos: [], stats: { erro: 'Resposta vazia' } };
    }

    const hits = response.data.hits.hits;
    console.log(`   ✅ ${hits.length} processos retornados da API`);

    const processados = hits.map(hit => processarHit(hit));
    
    console.log(`   🔍 Aplicando filtros locais...`);

    const filtrados = processados.filter(p => {
      // ✅ FILTRO PRINCIPAL: Apenas com ofício requisitório E pendente
      if (status === 'Pendente') {
        if (!p.temOficioRequisitorio) {
          return false; // Não tem ofício = descarta
        }
        if (p.foiPago) {
          return false; // Foi pago = descarta
        }
      } else if (status && status !== 'Todos') {
        // Outros status
        if (status !== p.status) {
          return false;
        }
      }
      
      // Filtro de valor
      if (valorMin && p.valor > 0 && p.valor < valorMin) {
        return false;
      }
      if (valorMax && p.valor > 0 && p.valor > valorMax) {
        return false;
      }
      
      // Filtro de natureza
      if (natureza && natureza !== 'Todas' && p.natureza !== natureza) {
        return false;
      }
      
      // Filtro de ANO LOA
      if (anoLoa && anoLoa !== 'Todos') {
        const anoLoaNum = parseInt(anoLoa);
        if (!isNaN(anoLoaNum) && p.anoLOA !== anoLoaNum) {
          return false;
        }
      }
      
      return true;
    });

    const resultado = filtrados.slice(0, quantidade);

    console.log(`\n📊 RESULTADO FINAL:`);
    console.log(`   Retornados da API: ${hits.length}`);
    console.log(`   Processados: ${processados.length}`);
    console.log(`   Com ofício requisitório: ${processados.filter(p => p.temOficioRequisitorio).length}`);
    console.log(`   Pendentes (ofício + não pago): ${processados.filter(p => p.temOficioRequisitorio && !p.foiPago).length}`);
    console.log(`   Após todos os filtros: ${filtrados.length}`);
    console.log(`   Retornando: ${resultado.length}`);
    
    if (resultado.length > 0) {
      console.log(`\n   📑 Distribuição por Status:`);
      const porStatus = resultado.reduce((acc, p) => {
        acc[p.status] = (acc[p.status] || 0) + 1;
        return acc;
      }, {});
      Object.entries(porStatus).forEach(([st, qtd]) => {
        console.log(`      ${st}: ${qtd} processos`);
      });
      
      console.log(`\n   📑 Distribuição por Natureza:`);
      const porNatureza = resultado.reduce((acc, p) => {
        acc[p.natureza] = (acc[p.natureza] || 0) + 1;
        return acc;
      }, {});
      Object.entries(porNatureza).forEach(([nat, qtd]) => {
        console.log(`      ${nat}: ${qtd} processos`);
      });
    }
    
    console.log(`   ✅ Fonte: API CNJ DataJud (OFICIAL)\n`);

    return {
      processos: resultado,
      stats: {
        totalAPI: hits.length,
        totalProcessados: processados.length,
        comOficio: processados.filter(p => p.temOficioRequisitorio).length,
        pendentes: processados.filter(p => p.temOficioRequisitorio && !p.foiPago).length,
        totalFiltrados: filtrados.length,
        totalRetornado: resultado.length,
        modo: 'API OFICIAL CNJ - Ofícios Requisitórios'
      }
    };

  } catch (error) {
    console.error(`   ❌ ERRO: ${error.message}\n`);
    return {
      processos: [],
      stats: { erro: error.message }
    };
  }
}

module.exports = { buscarProcessosESAJ };
