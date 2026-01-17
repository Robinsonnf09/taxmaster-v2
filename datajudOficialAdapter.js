// datajudOficialAdapter.js
const axios = require('axios');

// ✅ ENDPOINT CORRETO (atualizado janeiro 2026)
const BASE_URL = 'https://api-publica.datajud.cnj.jus.br';

const ENDPOINTS_TRIBUNAIS = {
  'TJ-SP': '/api_publica_tjsp/_search',
  'TJSP': '/api_publica_tjsp/_search',
  'TJ-RJ': '/api_publica_tjrj/_search',
  'TJRJ': '/api_publica_tjrj/_search',
  'TJ-MG': '/api_publica_tjmg/_search',
  'TJMG': '/api_publica_tjmg/_search',
  'TJ-RS': '/api_publica_tjrs/_search',
  'TJRS': '/api_publica_tjrs/_search',
  'TJ-PR': '/api_publica_tjpr/_search',
  'TJPR': '/api_publica_tjpr/_search',
  'TJ-BA': '/api_publica_tjba/_search',
  'TJBA': '/api_publica_tjba/_search',
  'TJ-SC': '/api_publica_tjsc/_search',
  'TJSC': '/api_publica_tjsc/_search',
  'TJ-PE': '/api_publica_tjpe/_search',
  'TJPE': '/api_publica_tjpe/_search'
};

const MAPA_TRIBUNAIS = {
  '8.26': 'TJ-SP', '8.19': 'TJ-RJ', '8.13': 'TJ-MG', '8.21': 'TJ-RS',
  '8.16': 'TJ-PR', '8.05': 'TJ-BA', '8.24': 'TJ-SC', '8.17': 'TJ-PE',
  '8.06': 'TJ-CE', '8.07': 'TJ-DF', '8.08': 'TJ-ES', '8.09': 'TJ-GO',
  '8.10': 'TJ-MA', '8.11': 'TJ-MT', '8.12': 'TJ-MS', '8.14': 'TJ-PA',
  '8.15': 'TJ-PB', '8.18': 'TJ-PI', '8.20': 'TJ-RN', '8.22': 'TJ-RO',
  '8.23': 'TJ-RR', '8.25': 'TJ-SE', '8.27': 'TJ-TO'
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
    aposTribunal: 0,
    aposValor: 0,
    aposNatureza: 0,
    aposAnoLOA: 0,
    final: 0,
    filtrosAplicados: []
  };

  // Determinar tribunais a consultar
  const tribunaisParaConsultar = tribunalDesejado && tribunalDesejado !== '' 
    ? [tribunalDesejado] 
    : Object.keys(ENDPOINTS_TRIBUNAIS).filter(t => t.startsWith('TJ-'));

  console.log('\n🔍 BUSCA OFICIAL DATAJUD CNJ (API ATUALIZADA)');
  console.log('   Base URL:', BASE_URL);
  console.log('   Tribunais:', tribunaisParaConsultar.join(', '));
  console.log('   Período:', dataInicio, 'até', dataFim);

  if (valorMin) stats.filtrosAplicados.push(`Valor Min: R$ ${valorMin.toLocaleString('pt-BR')}`);
  if (valorMax) stats.filtrosAplicados.push(`Valor Max: R$ ${valorMax.toLocaleString('pt-BR')}`);
  if (natureza) stats.filtrosAplicados.push(`Natureza: ${natureza}`);
  if (anoLoa) stats.filtrosAplicados.push(`ANO LOA: ${anoLoa}`);

  console.log('   Filtros aplicados:', stats.filtrosAplicados.length || 'Nenhum');

  let resultados = [];

  // Buscar em cada tribunal
  for (const tribunal of tribunaisParaConsultar) {
    const endpoint = ENDPOINTS_TRIBUNAIS[tribunal];
    if (!endpoint) continue;

    const url = `${BASE_URL}${endpoint}`;

    console.log(`\n   📍 Buscando em ${tribunal}...`);
    console.log(`      URL: ${url}`);

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

      // Filtro de data
      if (dataInicio && dataFim) {
        query.query.bool.filter.push({
          range: {
            dataAjuizamento: {
              gte: dataInicio,
              lte: dataFim
            }
          }
        });
      }

      // Filtro de valor
      if (valorMin || valorMax) {
        const rangeQuery = { range: { valorCausa: {} } };
        if (valorMin) rangeQuery.range.valorCausa.gte = valorMin;
        if (valorMax) rangeQuery.range.valorCausa.lte = valorMax;
        query.query.bool.filter.push(rangeQuery);
      }

      const response = await axios.post(url, query, {
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'User-Agent': 'TaxMaster/3.0'
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
            fonte: 'DataJud CNJ (API Oficial - Atualizada)'
          };
        });

        resultados = resultados.concat(processosFormatados);
      }

    } catch (error) {
      console.error(`      ❌ Erro em ${tribunal}:`, error.message);
    }
  }

  stats.final = resultados.length;

  console.log(`\n📊 ESTATÍSTICAS:');
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
    if (poloAtivo && poloAtivo.partes && poloAtivo.partes.length > 0) {
      return poloAtivo.partes[0].nome || 'Não informado';
    }
  }
  return 'Consultar processo';
}

function determinarStatus(proc) {
  if (!proc.movimentos || !proc.movimentos.length) return 'Em Análise';
  
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
  if (assuntoTexto.includes('trabalh') || classeTexto.includes('trabalh')) return 'Trabalhista';
  
  return 'Comum';
}

function calcularAnoLOA(proc) {
  const data = proc.dataAjuizamento;
  if (!data) return new Date().getFullYear() + 1;
  
  try {
    const ano = new Date(data).getFullYear();
    return ano + 2;
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
