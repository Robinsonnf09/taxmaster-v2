// cnjAdapter.js - API OFICIAL CNJ DataJud
const axios = require('axios');

const CNJ_API_URL = process.env.CNJ_API_URL || 'https://api-publica.datajud.cnj.jus.br';
const CNJ_USER = process.env.CNJ_USER;
const CNJ_PASS = process.env.CNJ_PASS;

async function buscarProcessosESAJ(params) {
  const { valorMin, valorMax, natureza, quantidade = 100 } = params;

  console.log('\n🔍 BUSCA NA API CNJ DATAJUD (OFICIAL)');
  console.log(`   Filtros: Valor ${valorMin || 0}-${valorMax || '∞'}`);

  if (!CNJ_USER || !CNJ_PASS) {
    console.log('   ⚠️ Credenciais CNJ não configuradas');
    console.log('   Configure CNJ_USER e CNJ_PASS no Railway\n');
    return { processos: [], stats: { erro: 'Credenciais não configuradas' } };
  }

  try {
    const auth = Buffer.from(`${CNJ_USER}:${CNJ_PASS}`).toString('base64');

    const query = {
      size: quantidade,
      query: {
        bool: {
          must: []
        }
      }
    };

    // Filtro de valor
    if (valorMin || valorMax) {
      query.query.bool.must.push({
        range: {
          valorCausa: {
            gte: valorMin || 0,
            lte: valorMax || 999999999
          }
        }
      });
    }

    // Filtro de natureza
    if (natureza && natureza !== 'Todas') {
      query.query.bool.must.push({
        match: {
          assunto: natureza
        }
      });
    }

    const response = await axios.post(
      `${CNJ_API_URL}/api_publica_tjsp/_search`,
      query,
      {
        headers: {
          'Authorization': `Basic ${auth}`,
          'Content-Type': 'application/json'
        },
        timeout: 30000
      }
    );

    const processos = response.data.hits.hits.map(hit => {
      const p = hit._source;
      return {
        numero: p.numeroProcesso,
        tribunal: 'TJ-SP',
        credor: p.polo?.ativo?.[0]?.nome || 'Não informado',
        valor: p.valorCausa || 0,
        classe: p.classe || 'Não informado',
        assunto: p.assunto || 'Não informado',
        dataDistribuicao: p.dataAjuizamento || 'Não informado',
        comarca: p.orgaoJulgador?.comarca || 'São Paulo',
        vara: p.orgaoJulgador?.nome || 'Não informado',
        natureza: p.assunto?.includes('Tribut') ? 'Tributária' : 'Comum',
        anoLOA: new Date().getFullYear() + 1,
        status: 'Em Análise',
        fonte: 'API CNJ DataJud (OFICIAL)'
      };
    });

    console.log(`   ✅ ${processos.length} processos REAIS encontrados\n`);

    return {
      processos: processos,
      stats: {
        totalAPI: processos.length,
        final: processos.length,
        modo: 'API OFICIAL CNJ'
      }
    };

  } catch (error) {
    console.error('   ❌ Erro na API CNJ:', error.message);
    
    if (error.response?.status === 401) {
      console.log('   ⚠️ Credenciais inválidas - verifique CNJ_USER e CNJ_PASS\n');
    }

    return {
      processos: [],
      stats: { erro: error.message }
    };
  }
}

module.exports = { buscarProcessosESAJ };
