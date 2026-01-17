// datajudOficialAdapter.js
const axios = require('axios');

const BASE_URL = 'https://api-publica.datajud.cnj.jus.br';

const ENDPOINTS_TRIBUNAIS = {
  'TJ-SP': '/api_publica_tjsp/_search',
  'TJ-RJ': '/api_publica_tjrj/_search',
  'TJ-MG': '/api_publica_tjmg/_search',
  'TJ-RS': '/api_publica_tjrs/_search',
  'TJ-PR': '/api_publica_tjpr/_search',
  'TJ-BA': '/api_publica_tjba/_search',
  'TJ-SC': '/api_publica_tjsc/_search',
  'TJ-PE': '/api_publica_tjpe/_search'
};

const MAPA_TRIBUNAIS = {
  '8.26': 'TJ-SP', '8.19': 'TJ-RJ', '8.13': 'TJ-MG', '8.21': 'TJ-RS',
  '8.16': 'TJ-PR', '8.05': 'TJ-BA', '8.24': 'TJ-SC', '8.17': 'TJ-PE'
};

// ✅ CREDENCIAIS (configurar no Railway)
const AUTH = {
  username: process.env.DATAJUD_USER || '',
  password: process.env.DATAJUD_PASS || ''
};

async function buscarProcessosOficial(params) {
  const {
    tribunalDesejado,
    valorMin,
    valorMax,
    natureza,
    anoLoa,
    dataInicio,
    dataFim,
  } = params;

  const stats = {
    totalAPI: 0,
    final: 0,
    filtrosAplicados: []
  };

  console.log('\n🔍 BUSCA OFICIAL DATAJUD CNJ');
  console.log('   Base URL:', BASE_URL);
  console.log('   Autenticação:', AUTH.username ? 'CONFIGURADA ✅' : 'NÃO CONFIGURADA ❌');

  if (!AUTH.username || !AUTH.password) {
    console.log('\n❌ CREDENCIAIS NÃO CONFIGURADAS!');
    console.log('   Configure no Railway:');
    console.log('   • DATAJUD_USER');
    console.log('   • DATAJUD_PASS\n');
    
    return {
      processos: [],
      stats: stats,
      erro: 'Credenciais não configuradas'
    };
  }

  const tribunaisParaConsultar = tribunalDesejado && tribunalDesejado !== '' 
    ? [tribunalDesejado] 
    : ['TJ-SP']; // Por padrão, apenas TJ-SP

  let resultados = [];

  for (const tribunal of tribunaisParaConsultar) {
    const endpoint = ENDPOINTS_TRIBUNAIS[tribunal];
    if (!endpoint) continue;

    const url = `${BASE_URL}${endpoint}`;

    console.log(`\n   📍 Buscando em ${tribunal}...`);

    try {
      // Query Elasticsearch
      const query = {
        size: 100,
        query: {
          bool: {
            must: [],
            filter: []
          }
        }
      };

      // Filtro de valor
      if (valorMin || valorMax) {
        const rangeQuery = { range: { valorCausa: {} } };
        if (valorMin) rangeQuery.range.valorCausa.gte = valorMin;
        if (valorMax) rangeQuery.range.valorCausa.lte = valorMax;
        query.query.bool.filter.push(rangeQuery);
      }

      const response = await axios.post(url, query, {
        auth: AUTH,
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      const hits = response.data?.hits?.hits || [];
      stats.totalAPI += hits.length;

      console.log(`      API retornou: ${hits.length} processos`);

      if (hits.length > 0) {
        const processosFormatados = hits.map(hit => {
          const proc = hit._source;
          
          return {
            numero: proc.numeroProcesso || 'N/A',
            tribunal: tribunal,
            credor: extrairCredor(proc),
            valor: Number(proc.valorCausa || 0),
            status: determinarStatus(proc),
            natureza: extrairNatureza(proc),
            anoLOA: calcularAnoLOA(proc),
            dataDistribuicao: formatarData(proc.dataAjuizamento),
            classe: proc.classe?.nome || 'N/A',
            assunto: proc.assuntos?.[0]?.nome || 'N/A',
            fonte: 'DataJud CNJ (API Oficial)'
          };
        });

        resultados = resultados.concat(processosFormatados);
      }

    } catch (error) {
      console.error(`      ❌ Erro em ${tribunal}:`, error.message);
      if (error.response?.status === 401) {
        console.error('      ⚠️ ERRO DE AUTENTICAÇÃO - Verifique credenciais!');
      }
    }
  }

  stats.final = resultados.length;

  console.log(`\n📊 ESTATÍSTICAS:`);
  console.log(`   Total API: ${stats.totalAPI}`);
  console.log(`   ✅ RESULTADO FINAL: ${stats.final} processos\n`);

  return {
    processos: resultados,
    stats: stats
  };
}

function extrairCredor(proc) {
  if (proc.polo && Array.isArray(proc.polo)) {
    const poloAtivo = proc.polo.find(p => p.polo === 'Ativo');
    if (poloAtivo?.partes?.[0]?.nome) {
      return poloAtivo.partes[0].nome;
    }
  }
  return 'Consultar processo';
}

function determinarStatus(proc) {
  if (!proc.movimentos?.length) return 'Em Análise';
  
  const ultimo = proc.movimentos[proc.movimentos.length - 1];
  const nome = (ultimo.nome || '').toLowerCase();
  
  if (nome.includes('aprovad') || nome.includes('deferi')) return 'Aprovado';
  if (nome.includes('pendent') || nome.includes('aguard')) return 'Pendente';
  if (nome.includes('arquiv')) return 'Arquivado';
  
  return 'Em Análise';
}

function extrairNatureza(proc) {
  const assuntos = proc.assuntos || [];
  const classe = proc.classe?.nome || '';
  
  const assuntoTexto = assuntos.map(a => a.nome).join(' ').toLowerCase();
  const classeTexto = classe.toLowerCase();
  
  if (assuntoTexto.includes('aliment') || classeTexto.includes('aliment')) return 'Alimentar';
  if (assuntoTexto.includes('tribut') || classeTexto.includes('tribut')) return 'Tributária';
  if (assuntoTexto.includes('previd') || classeTexto.includes('previd')) return 'Previdenciária';
  
  return 'Comum';
}

function calcularAnoLOA(proc) {
  const data = proc.dataAjuizamento;
  if (!data) return new Date().getFullYear() + 1;
  
  try {
    return new Date(data).getFullYear() + 2;
  } catch {
    return new Date().getFullYear() + 1;
  }
}

function formatarData(dataISO) {
  if (!dataISO) return 'N/A';
  try {
    return new Date(dataISO).toLocaleDateString('pt-BR');
  } catch {
    return 'N/A';
  }
}

module.exports = { buscarProcessosOficial };
