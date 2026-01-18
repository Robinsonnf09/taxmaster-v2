// esajScraper.js - API CNJ DataJud (extração profunda e precisa)
const axios = require('axios');

const CNJ_API_URL = process.env.CNJ_API_URL || 'https://api-publica.datajud.cnj.jus.br';
const CNJ_API_KEY = process.env.CNJ_API_KEY || 'cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==';

// ✅ Termos para detectar OFÍCIO REQUISITÓRIO
const TERMOS_OFICIO = [
  'ofício requisitório',
  'oficio requisitorio',
  'requisição de pagamento',
  'expedição de precatório',
  'expedição de rpv',
  'precatório expedido',
  'rpv expedido',
  'expedido precatório',
  'expedido rpv',
  'remetido ao tribunal',
  'remessa de precatório',
  'encaminhado.*pagamento',
  'requisitar.*pagamento'
];

// ✅ Termos para detectar PAGAMENTO
const TERMOS_PAGAMENTO = [
  'pago',
  'quitado',
  'quitação',
  'pagamento efetuado',
  'pagamento realizado',
  'levantamento',
  'alvará.*levantamento',
  'transferência realizada',
  'depósito efetuado',
  'crédito disponível',
  'baixa definitiva'
];

// ✅ Extrair CPF do credor dos movimentos/documentos
function extrairCPFCreador(movimentos, documentos) {
  const textos = [
    ...(movimentos || []).map(m => m.descricao || m.nome || ''),
    ...(documentos || []).map(d => d.descricao || d.nome || '')
  ].join(' ');
  
  const cpfMatch = textos.match(/\d{3}\.\d{3}\.\d{3}-\d{2}/);
  return cpfMatch ? cpfMatch[0] : null;
}

// ✅ Extrair VALOR da requisição dos movimentos
function extrairValorRequisicao(movimentos, valorCausa) {
  if (valorCausa && valorCausa > 0) return valorCausa;
  
  if (!movimentos || movimentos.length === 0) return 0;
  
  // Procurar por valores em reais nos movimentos
  const textoMovimentos = movimentos.map(m => m.descricao || m.nome || '').join(' ');
  
  // Padrões: R$ 1.234,56 ou R$ 1.234.567,89
  const padroes = [
    /R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)/g,
    /valor.*?(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)/gi,
    /requisição.*?(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)/gi
  ];
  
  const valores = [];
  padroes.forEach(padrao => {
    let match;
    while ((match = padrao.exec(textoMovimentos)) !== null) {
      const valorStr = match[1].replace(/\./g, '').replace(',', '.');
      const valor = parseFloat(valorStr);
      if (!isNaN(valor) && valor > 0) {
        valores.push(valor);
      }
    }
  });
  
  // Retornar o maior valor encontrado
  return valores.length > 0 ? Math.max(...valores) : 0;
}

// ✅ Extrair NATUREZA do crédito (Alimentar, Comum, Tributária)
function extrairNatureza(classe, assuntos, movimentos) {
  const textos = [
    classe || '',
    ...(assuntos || []).map(a => a.nome || ''),
    ...(movimentos || []).slice(-10).map(m => m.descricao || m.nome || '')
  ].join(' ').toLowerCase();
  
  // ALIMENTAR - prioridade máxima
  if (textos.match(/alimentar|aliment\w*|pensão|pensao|salário|salario|vencimento|subsídio|subsidio|aposentadoria|previdenciár/i)) {
    return 'Alimentar';
  }
  
  // TRIBUTÁRIA
  if (textos.match(/tribut\w*|fiscal|iptu|iss|icms|cofins|pis|ipi|imposto|taxa/i)) {
    return 'Tributária';
  }
  
  // PREVIDENCIÁRIA
  if (textos.match(/previd\w*|aposentad\w*|benefício|beneficio|inss/i)) {
    return 'Previdenciária';
  }
  
  return 'Comum';
}

// ✅ Extrair ANO LOA (ano da expedição do ofício)
function extrairAnoLOA(movimentos, numeroProcesso) {
  if (!movimentos || movimentos.length === 0) {
    // Fallback: ano do processo + 2
    const anoProcesso = extrairAnoDoNumero(numeroProcesso);
    return anoProcesso ? anoProcesso + 2 : new Date().getFullYear() + 1;
  }
  
  // Procurar movimento de "ofício requisitório" ou "expedição"
  for (let i = movimentos.length - 1; i >= 0; i--) {
    const mov = movimentos[i];
    const descricao = (mov.descricao || mov.nome || '').toLowerCase();
    
    if (TERMOS_OFICIO.some(termo => descricao.match(new RegExp(termo, 'i')))) {
      // Extrair data do movimento
      if (mov.dataHora) {
        const anoMovimento = parseInt(mov.dataHora.substring(0, 4));
        if (!isNaN(anoMovimento)) {
          return anoMovimento + 1; // LOA é ano seguinte
        }
      }
    }
  }
  
  // Fallback
  const anoProcesso = extrairAnoDoNumero(numeroProcesso);
  return anoProcesso ? anoProcesso + 2 : new Date().getFullYear() + 1;
}

function extrairAnoDoNumero(numeroProcesso) {
  if (!numeroProcesso || numeroProcesso.length < 13) return null;
  const ano = parseInt(numeroProcesso.substring(9, 13));
  return isNaN(ano) ? null : ano;
}

// ✅ Verificar se tem ofício requisitório
function temOficioRequisitorio(movimentos) {
  if (!movimentos || movimentos.length === 0) return false;
  
  return movimentos.some(m => {
    const texto = (m.descricao || m.nome || '').toLowerCase();
    return TERMOS_OFICIO.some(termo => texto.match(new RegExp(termo, 'i')));
  });
}

// ✅ Verificar se foi pago
function foiPago(movimentos) {
  if (!movimentos || movimentos.length === 0) return false;
  
  return movimentos.some(m => {
    const texto = (m.descricao || m.nome || '').toLowerCase();
    return TERMOS_PAGAMENTO.some(termo => texto.match(new RegExp(termo, 'i')));
  });
}

// ✅ Extrair nome do credor
function extrairCreador(partes) {
  if (!partes || !Array.isArray(partes) || partes.length === 0) {
    return 'A definir';
  }
  
  // Procurar por ATIVO, AUTOR, EXEQUENTE
  const credor = partes.find(p => 
    p.polo === 'ATIVO' || 
    p.tipo === 'AUTOR' || 
    p.tipo === 'EXEQUENTE' ||
    p.tipo === 'REQUERENTE'
  );
  
  return credor?.nome || partes[0]?.nome || 'A definir';
}

// ✅ Determinar status
function determinarStatus(movimentos) {
  const temOficio = temOficioRequisitorio(movimentos);
  const pago = foiPago(movimentos);
  
  if (pago) return 'Pago';
  if (temOficio) return 'Pendente';
  return 'Em Análise';
}

function processarHit(hit) {
  const p = hit._source;
  
  const numero = p.numeroProcesso || 'Não informado';
  const classe = p.classe?.nome || 'Não informado';
  const orgao = p.orgaoJulgador?.nome || 'Não informado';
  const movimentos = p.movimentos || [];
  const assuntos = p.assunto || [];
  const partes = p.partes || [];
  const dataAjuizamento = p.dataAjuizamento || p.dataHoraUltimaAtualizacao || 'Não informado';
  
  // ✅ EXTRAÇÕES PROFUNDAS
  const valor = extrairValorRequisicao(movimentos, p.valorCausa);
  const natureza = extrairNatureza(classe, assuntos, movimentos);
  const anoLOA = extrairAnoLOA(movimentos, numero);
  const credor = extrairCreador(partes);
  const status = determinarStatus(movimentos);
  const temOficio = temOficioRequisitorio(movimentos);
  const pago = foiPago(movimentos);
  
  return {
    numero: numero,
    tribunal: 'TJ-SP',
    credor: credor,
    valor: valor,
    classe: classe,
    assunto: assuntos.map(a => a.nome).join(', ') || orgao,
    dataDistribuicao: dataAjuizamento,
    comarca: p.orgaoJulgador?.comarca || 'São Paulo',
    vara: orgao,
    natureza: natureza,
    anoLOA: anoLOA,
    anoAjuizamento: extrairAnoDoNumero(numero),
    status: status,
    temOficioRequisitorio: temOficio,
    foiPago: pago,
    quantidadeMovimentos: movimentos.length,
    fonte: 'API CNJ DataJud'
  };
}

async function buscarProcessosESAJ(params) {
  const { valorMin, valorMax, natureza, anoLoa, status, quantidade = 50 } = params;

  console.log('\n🔍 BUSCA NA API CNJ DATAJUD (EXTRAÇÃO PROFUNDA)');
  console.log(`   URL: ${CNJ_API_URL}`);
  console.log(`   Filtros:`);
  console.log(`     Valor: R$ ${valorMin || 0} - R$ ${valorMax || '∞'}`);
  console.log(`     Natureza: ${natureza || 'Todas'}`);
  console.log(`     ANO LOA: ${anoLoa || 'Todos'}`);
  console.log(`     Status: ${status || 'Todos'}`);

  try {
    const query = {
      size: quantidade * 5,
      query: {
        match_all: {}
      },
      sort: [
        { 'dataHoraUltimaAtualizacao': { order: 'desc' } }
      ]
    };

    console.log(`   📤 Buscando processos...`);

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

    console.log(`   📥 Status HTTP: ${response.status}`);

    if (!response.data?.hits?.hits) {
      console.log('   ⚠️ Resposta vazia\n');
      return { processos: [], stats: { erro: 'Resposta vazia' } };
    }

    const hits = response.data.hits.hits;
    console.log(`   ✅ ${hits.length} processos retornados`);

    const processados = hits.map(hit => processarHit(hit));
    
    console.log(`   🔍 Aplicando filtros...`);

    const filtrados = processados.filter(p => {
      // Filtro de status (principal)
      if (status === 'Pendente') {
        if (!p.temOficioRequisitorio || p.foiPago) return false;
      } else if (status && status !== 'Todos' && p.status !== status) {
        return false;
      }
      
      // Filtro de valor
      if (valorMin && p.valor > 0 && p.valor < valorMin) return false;
      if (valorMax && p.valor > 0 && p.valor > valorMax) return false;
      
      // Filtro de natureza
      if (natureza && natureza !== 'Todas' && p.natureza !== natureza) return false;
      
      // Filtro de ANO LOA
      if (anoLoa && anoLoa !== 'Todos') {
        const anoLoaNum = parseInt(anoLoa);
        if (!isNaN(anoLoaNum) && p.anoLOA !== anoLoaNum) return false;
      }
      
      return true;
    });

    const resultado = filtrados.slice(0, quantidade);

    console.log(`\n📊 ESTATÍSTICAS:`);
    console.log(`   Total da API: ${hits.length}`);
    console.log(`   Com ofício: ${processados.filter(p => p.temOficioRequisitorio).length}`);
    console.log(`   Com valor > 0: ${processados.filter(p => p.valor > 0).length}`);
    console.log(`   Alimentares: ${processados.filter(p => p.natureza === 'Alimentar').length}`);
    console.log(`   Após filtros: ${filtrados.length}`);
    console.log(`   Retornados: ${resultado.length}\n`);

    return {
      processos: resultado,
      stats: {
        total: hits.length,
        comOficio: processados.filter(p => p.temOficioRequisitorio).length,
        comValor: processados.filter(p => p.valor > 0).length,
        alimentares: processados.filter(p => p.natureza === 'Alimentar').length,
        filtrados: filtrados.length,
        retornados: resultado.length
      }
    };

  } catch (error) {
    console.error(`   ❌ ERRO: ${error.message}\n`);
    return { processos: [], stats: { erro: error.message } };
  }
}

module.exports = { buscarProcessosESAJ };
