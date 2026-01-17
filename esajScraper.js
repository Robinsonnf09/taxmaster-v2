// esajScraper.js - API OFICIAL CNJ DataJud com APIKey
const axios = require('axios');

const CNJ_API_URL = process.env.CNJ_API_URL || 'https://api-publica.datajud.cnj.jus.br';
const CNJ_API_KEY = process.env.CNJ_API_KEY;

async function buscarProcessosESAJ(params) {
  const { valorMin, valorMax, natureza, anoLoa, quantidade = 100 } = params;

  console.log('\n🔍 BUSCA NA API CNJ DATAJUD (OFICIAL)');
  console.log(`   URL: ${CNJ_API_URL}`);
  console.log(`   Filtros: Valor ${valorMin || 0}-${valorMax || '∞'}, Natureza: ${natureza || 'Todas'}`);

  // Verificar API Key
  if (!CNJ_API_KEY) {
    console.log('   ❌ CNJ_API_KEY não configurada no Railway');
    console.log('   Configure a variável de ambiente CNJ_API_KEY\n');
    return { 
      processos: [], 
      stats: { 
        erro: 'API Key não configurada',
        solucao: 'Configure CNJ_API_KEY no Railway'
      } 
    };
  }

  try {
    // Montar query ElasticSearch
    const query = {
      size: quantidade,
      query: {
        bool: {
          must: [
            {
              term: {
                'tribunal': 'TJSP'
              }
            }
          ],
          filter: []
        }
      },
      sort: [
        { 'dataAjuizamento': { order: 'desc' } }
      ]
    };

    // Filtro de valor
    if (valorMin || valorMax) {
      query.query.bool.filter.push({
        range: {
          'valorCausa': {
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
          'assunto': {
            query: natureza,
            operator: 'and'
          }
        }
      });
    }

    // Filtro de ano LOA (baseado em data de ajuizamento)
    if (anoLoa && anoLoa !== 'Todos') {
      const anoProcesso = parseInt(anoLoa) - 2; // LOA = ano processo + 2
      query.query.bool.filter.push({
        range: {
          'dataAjuizamento': {
            gte: `${anoProcesso}-01-01`,
            lte: `${anoProcesso}-12-31`
          }
        }
      });
    }

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
        timeout: 30000
      }
    );

    console.log(`   📥 Resposta recebida: ${response.status}`);

    if (!response.data || !response.data.hits) {
      console.log('   ⚠️ Resposta sem dados\n');
      return { processos: [], stats: { erro: 'Resposta vazia da API' } };
    }

    const hits = response.data.hits.hits;
    console.log(`   ✅ ${hits.length} processos encontrados`);

    const processos = hits.map(hit => {
      const p = hit._source;
      
      // Determinar natureza
      let naturezaFinal = 'Comum';
      const assuntoLower = (p.assunto || '').toLowerCase();
      
      if (assuntoLower.includes('tribut') || assuntoLower.includes('fiscal') || 
          assuntoLower.includes('iptu') || assuntoLower.includes('iss')) {
        naturezaFinal = 'Tributária';
      } else if (assuntoLower.includes('aliment')) {
        naturezaFinal = 'Alimentar';
      } else if (assuntoLower.includes('previd')) {
        naturezaFinal = 'Previdenciária';
      }

      // Extrair credor/autor
      let credor = 'Não informado';
      if (p.polo && p.polo.ativo && p.polo.ativo.length > 0) {
        credor = p.polo.ativo[0].nome || 'Não informado';
      } else if (p.partes && p.partes.length > 0) {
        const autor = p.partes.find(parte => 
          parte.polo === 'ATIVO' || 
          parte.tipo === 'AUTOR' || 
          parte.tipo === 'EXEQUENTE'
        );
        if (autor) credor = autor.nome || 'Não informado';
      }

      // Calcular ano LOA
      let anoLOA = new Date().getFullYear() + 1;
      if (p.dataAjuizamento) {
        const match = p.dataAjuizamento.match(/(\d{4})/);
        if (match) anoLOA = parseInt(match[1]) + 2;
      }

      return {
        numero: p.numeroProcesso || 'Não informado',
        tribunal: 'TJ-SP',
        credor: credor,
        valor: p.valorCausa || 0,
        classe: p.classe || 'Não informado',
        assunto: p.assunto || 'Não informado',
        dataDistribuicao: p.dataAjuizamento || 'Não informado',
        comarca: p.orgaoJulgador?.comarca || p.comarca || 'São Paulo',
        vara: p.orgaoJulgador?.nome || 'Não informado',
        natureza: naturezaFinal,
        anoLOA: anoLOA,
        status: 'Em Análise',
        fonte: 'API CNJ DataJud (Dados REAIS)'
      };
    });

    console.log(`\n📊 ESTATÍSTICAS:`);
    console.log(`   Total encontrado: ${processos.length}`);
    console.log(`   Fonte: API CNJ DataJud (OFICIAL)`);
    console.log(`   ✅ DADOS 100% REAIS\n`);

    return {
      processos: processos,
      stats: {
        totalAPI: processos.length,
        final: processos.length,
        modo: 'API OFICIAL CNJ',
        fonte: 'DataJud'
      }
    };

  } catch (error) {
    console.error(`   ❌ ERRO: ${error.message}`);
    
    if (error.response) {
      console.log(`   Status: ${error.response.status}`);
      console.log(`   Mensagem: ${error.response.data?.error?.reason || error.response.statusText}`);
      
      if (error.response.status === 401) {
        console.log(`   ⚠️ API Key inválida - verifique CNJ_API_KEY\n`);
      } else if (error.response.status === 403) {
        console.log(`   ⚠️ Acesso negado - API Key sem permissão\n`);
      } else if (error.response.status === 404) {
        console.log(`   ⚠️ Endpoint não encontrado - verifique CNJ_API_URL\n`);
      }
    }

    return {
      processos: [],
      stats: { 
        erro: error.message,
        status: error.response?.status
      }
    };
  }
}

module.exports = { buscarProcessosESAJ };
