// esajScraper.js - API CNJ DataJud (versão otimizada e melhorada)
const axios = require('axios');

const CNJ_API_URL = process.env.CNJ_API_URL || 'https://api-publica.datajud.cnj.jus.br';
const CNJ_API_KEY = process.env.CNJ_API_KEY || 'cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==';

// ✅ Constantes
const NATUREZAS = {
  TRIBUTARIA: ['tribut', 'fiscal', 'iptu', 'iss', 'icms'],
  ALIMENTAR: ['aliment'],
  PREVIDENCIARIA: ['previd', 'aposentad', 'pensão'],
  COMUM: []
};

// ✅ Função auxiliar: Extrair credor/autor
function extrairCreador(partes) {
  if (!partes || !Array.isArray(partes) || partes.length === 0) {
    return 'Não informado';
  }
  
  const autor = partes.find(parte => 
    parte.polo === 'ATIVO' || 
    parte.tipo === 'AUTOR' || 
    parte.tipo === 'EXEQUENTE'
  );
  
  return autor?.nome || partes[0]?.nome || 'Não informado';
}

// ✅ Função auxiliar: Determinar natureza
function determinarNatureza(assuntoNome) {
  if (!assuntoNome) return 'Comum';
  
  const assuntoLower = assuntoNome.toLowerCase();
  
  for (const [natureza, palavrasChave] of Object.entries(NATUREZAS)) {
    if (palavrasChave.some(palavra => assuntoLower.includes(palavra))) {
      return natureza.charAt(0) + natureza.slice(1).toLowerCase().replace('_', ' ');
    }
  }
  
  return 'Comum';
}

// ✅ Função auxiliar: Calcular ano LOA
function calcularAnoLOA(dataAjuizamento) {
  if (!dataAjuizamento) {
    return new Date().getFullYear() + 1;
  }
  
  const match = dataAjuizamento.match(/(\d{4})/);
  return match ? parseInt(match[1]) + 2 : new Date().getFullYear() + 1;
}

// ✅ Função auxiliar: Validar se processo atende aos filtros
function validarFiltros(processo, filtros) {
  const { valorMin, valorMax, natureza } = filtros;
  
  // Filtro de valor
  if (valorMin && processo.valor < valorMin) return false;
  if (valorMax && processo.valor > valorMax) return false;
  
  // Filtro de natureza
  if (natureza && natureza !== 'Todas' && processo.natureza !== natureza) {
    // Verificar se o assunto contém a natureza procurada
    const assuntoLower = (processo.assunto || '').toLowerCase();
    const naturezaLower = natureza.toLowerCase();
    if (!assuntoLower.includes(naturezaLower)) return false;
  }
  
  return true;
}

// ✅ Função auxiliar: Processar hit do ElasticSearch
function processarHit(hit, filtros) {
  const p = hit._source;
  
  // 🔍 LOG DE DEBUG - Ver estrutura real dos dados (só para os 3 primeiros)
  if (hit._id && Math.random() < 0.1) { // 10% dos processos
    console.log(`\n   🔍 DEBUG - Estrutura do processo ${p.numeroProcesso}:`);
    console.log(`      valorCausa: ${p.valorCausa}`);
    console.log(`      partes (${p.partes?.length || 0}): ${JSON.stringify(p.partes?.slice(0, 2))}`);
    console.log(`      assuntos: ${JSON.stringify(p.assunto)}`);
    console.log(`      classe: ${JSON.stringify(p.classe)}`);
    console.log(`      orgaoJulgador: ${JSON.stringify(p.orgaoJulgador)}`);
  }
  
  // Extrair dados básicos
  const valor = p.valorCausa || 0;
  const assuntoNome = p.assunto?.[0]?.nome || '';
  const naturezaFinal = determinarNatureza(assuntoNome);
  const credor = extrairCreador(p.partes);
  const anoLOA = calcularAnoLOA(p.dataAjuizamento);
  
  // Criar objeto processo
  const processo = {
    numero: p.numeroProcesso || 'Não informado',
    tribunal: 'TJ-SP',
    credor: credor,
    valor: valor,
    classe: p.classe?.nome || 'Não informado',
    assunto: assuntoNome || 'Não informado',
    dataDistribuicao: p.dataAjuizamento || 'Não informado',
    comarca: p.orgaoJulgador?.nomeOrgao || p.orgaoJulgador?.comarca || 'São Paulo',
    vara: p.orgaoJulgador?.nomeOrgao || 'Não informado',
    natureza: naturezaFinal,
    anoLOA: anoLOA,
    status: 'Em Análise',
    fonte: 'API CNJ DataJud (Dados REAIS)'
  };
  
  // Validar filtros
  return validarFiltros(processo, filtros) ? processo : null;
}

// ✅ Função principal
async function buscarProcessosESAJ(params) {
  const { valorMin, valorMax, natureza, anoLoa, quantidade = 50 } = params;

  console.log('\n🔍 BUSCA NA API CNJ DATAJUD (OFICIAL)');
  console.log(`   URL: ${CNJ_API_URL}`);
  console.log(`   Quantidade solicitada: ${quantidade}`);
  console.log(`   Filtros: Valor ${valorMin || 0}-${valorMax || '∞'}, Natureza: ${natureza || 'Todas'}, ANO LOA: ${anoLoa || 'Todos'}`);

  // Validação da API Key
  if (!CNJ_API_KEY) {
    console.log('   ❌ CNJ_API_KEY não configurada\n');
    return { 
      processos: [], 
      stats: { erro: 'API Key não configurada' } 
    };
  }

  try {
    // 🔥 Query otimizada - buscar tudo e filtrar localmente
    const query = {
      size: quantidade * 2, // Pegar mais para compensar filtros locais
      query: {
        match_all: {}
      },
      sort: [
        { 'dataHoraUltimaAtualizacao': { order: 'desc' } }
      ],
      _source: [
        'numeroProcesso',
        'classe.nome',
        'assunto',
        'valorCausa',
        'dataAjuizamento',
        'partes',
        'orgaoJulgador'
      ]
    };

    console.log(`   📤 Enviando requisição para CNJ...`);

    const response = await axios.post(
      `${CNJ_API_URL}/api_publica_tjsp/_search`,
      query,
      {
        headers: {
          'Authorization': `APIKey ${CNJ_API_KEY}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        timeout: 30000,
        validateStatus: (status) => status >= 200 && status < 500
      }
    );

    console.log(`   📥 Status: ${response.status}`);

    // Validar resposta
    if (response.status !== 200) {
      console.log(`   ❌ Erro HTTP: ${response.status}`);
      console.log(`   Resposta: ${JSON.stringify(response.data)}\n`);
      return { 
        processos: [], 
        stats: { 
          erro: `HTTP ${response.status}`,
          detalhes: response.data 
        } 
      };
    }

    if (!response.data || !response.data.hits || !response.data.hits.hits) {
      console.log('   ⚠️ Resposta sem dados\n');
      return { processos: [], stats: { erro: 'Resposta vazia' } };
    }

    const hits = response.data.hits.hits;
    const totalEncontrado = response.data.hits.total?.value || hits.length;
    
    console.log(`   ✅ ${hits.length} processos retornados da API`);
    console.log(`   📊 Total disponível no índice: ${totalEncontrado}`);

    // Log de amostra
    if (hits.length > 0) {
      const amostra = hits[0]._source;
      console.log(`   🔍 Amostra do primeiro processo:`);
      console.log(`      Número: ${amostra.numeroProcesso}`);
      console.log(`      Classe: ${amostra.classe?.nome || 'N/A'}`);
      console.log(`      Assunto: ${amostra.assunto?.[0]?.nome || 'N/A'}`);
      console.log(`      Valor: R$ ${(amostra.valorCausa || 0).toLocaleString('pt-BR')}`);
    }

    // 🔎 Processar e filtrar
    const filtros = { valorMin, valorMax, natureza, anoLoa };
    const processos = hits
      .map(hit => processarHit(hit, filtros))
      .filter(p => p !== null)
      .slice(0, quantidade); // Limitar ao número solicitado

    console.log(`\n📊 RESULTADO FINAL:`);
    console.log(`   Recebidos da API: ${hits.length}`);
    console.log(`   Após filtros: ${processos.length}`);
    console.log(`   ✅ Fonte: API CNJ DataJud (OFICIAL)\n`);

    // Estatísticas extras
    if (processos.length > 0) {
      const valores = processos.map(p => p.valor).filter(v => v > 0);
      if (valores.length > 0) {
        const valorMedio = valores.reduce((a, b) => a + b, 0) / valores.length;
        console.log(`   💰 Valor médio: R$ ${valorMedio.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`);
      }
      
      const naturezasCount = processos.reduce((acc, p) => {
        acc[p.natureza] = (acc[p.natureza] || 0) + 1;
        return acc;
      }, {});
      console.log(`   📑 Distribuição por natureza:`, naturezasCount);
      console.log('');
    }

    return {
      processos: processos,
      stats: {
        totalAPI: hits.length,
        totalDisponivel: totalEncontrado,
        final: processos.length,
        modo: 'API OFICIAL CNJ',
        timestamp: new Date().toISOString()
      }
    };

  } catch (error) {
    console.error(`   ❌ ERRO: ${error.message}`);

    if (error.response) {
      console.log(`   Status HTTP: ${error.response.status}`);
      console.log(`   Dados: ${JSON.stringify(error.response.data).substring(0, 200)}...`);
    } else if (error.request) {
      console.log(`   ⚠️ Sem resposta do servidor`);
    } else {
      console.log(`   ⚠️ Erro de configuração: ${error.message}`);
    }

    console.log('');

    return {
      processos: [],
      stats: {
        erro: error.message,
        status: error.response?.status,
        tipo: error.code
      }
    };
  }
}

module.exports = { buscarProcessosESAJ };

