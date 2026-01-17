// datajudOficialAdapter.js
const axios = require('axios');

const BASE_URL = 'https://datajud-wiki.cnj.jus.br/api-publica/v1/processos';

// Mapeamento J.TR → Tribunal (do número CNJ)
const MAPA_TRIBUNAIS = {
  '8.26': 'TJ-SP',
  '8.19': 'TJ-RJ',
  '8.13': 'TJ-MG',
  '8.21': 'TJ-RS',
  '8.16': 'TJ-PR',
  '8.05': 'TJ-BA',
  '8.24': 'TJ-SC',
  '8.17': 'TJ-PE'
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

  console.log('\n🔍 BUSCA OFICIAL DATAJUD CNJ');
  console.log('   Endpoint:', BASE_URL);
  console.log('   Período:', dataInicio, 'até', dataFim);
  console.log('   Tribunal desejado:', tribunalDesejado || 'TODOS');

  const tamanhoPagina = 100;
  let pagina = 0;
  let resultados = [];
  let terminou = false;

  while (!terminou) {
    try {
      const url = `${BASE_URL}?dataInicio=${encodeURIComponent(
        dataInicio
      )}&dataFim=${encodeURIComponent(
        dataFim
      )}&pagina=${pagina}&tamanhoPagina=${tamanhoPagina}`;

      console.log(`   📄 Página ${pagina + 1}...`);

      const { data } = await axios.get(url, { 
        timeout: 30000,
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'TaxMaster/3.0'
        }
      });

      const processos = data?.conteudo || data?.content || data || [];

      console.log(`      API retornou: ${processos.length} processos`);

      if (!processos.length) {
        terminou = true;
        break;
      }

      // ✅ FILTROS
      const filtrados = processos.filter((proc) => {
        const valorCausa = Number(proc.valorCausa || 0);
        const classe = (proc.classe || '').toString().toLowerCase();
        const assunto = (proc.assunto || '').toString().toLowerCase();
        const dataAjuizamento = proc.dataAjuizamento || proc.dataDistribuicao;
        const numeroProcesso = proc.numeroProcesso || '';

        // ✅ Inferir tribunal pelo número (NNNNNNN-DD.AAAA.J.TR.OOOO)
        const tribunalInferido = inferirTribunal(numeroProcesso);

        // Filtro opcional por tribunal (se especificado)
        if (tribunalDesejado && tribunalInferido !== tribunalDesejado) {
          return false;
        }

        // ✅ Filtro por valor
        if (valorMin != null && !Number.isNaN(valorMin) && valorCausa < valorMin) {
          return false;
        }
        if (valorMax != null && !Number.isNaN(valorMax) && valorCausa > valorMax) {
          return false;
        }

        // ✅ Filtro por natureza
        if (natureza) {
          const nat = natureza.toString().toLowerCase();
          if (!classe.includes(nat) && !assunto.includes(nat)) {
            return false;
          }
        }

        // ✅ Filtro por ANO LOA
        if (anoLoa && dataAjuizamento) {
          const anoProc = new Date(dataAjuizamento).getFullYear();
          const loaProc = anoProc + 2;
          if (loaProc !== Number(anoLoa)) {
            return false;
          }
        }

        return true;
      });

      console.log(`      Após filtros: ${filtrados.length} processos`);

      const processosFormatados = filtrados.map(proc => {
        const numeroProcesso = proc.numeroProcesso || 'N/A';
        const tribunalInferido = inferirTribunal(numeroProcesso);

        return {
          numero: numeroProcesso,
          tribunal: tribunalInferido,
          credor: extrairCredor(proc),
          valor: Number(proc.valorCausa || 0),
          status: determinarStatus(proc),
          natureza: extrairNatureza(proc),
          anoLOA: calcularAnoLOA(proc),
          dataDistribuicao: formatarData(proc.dataAjuizamento || proc.dataDistribuicao),
          classe: proc.classe || 'N/A',
          assunto: proc.assunto || 'N/A',
          fonte: 'DataJud CNJ (API Oficial v1)'
        };
      });

      resultados = resultados.concat(processosFormatados);

      if (processos.length < tamanhoPagina) {
        terminou = true;
      } else {
        pagina += 1;
      }

      if (pagina > 20 || resultados.length >= 200) {
        console.log('   ⚠️ Limite atingido');
        terminou = true;
      }

    } catch (error) {
      console.error(`   ❌ Erro:`, error.message);
      if (error.response) {
        console.error(`      Status: ${error.response.status}`);
      }
      terminou = true;
    }
  }

  console.log(`\n✅ Total encontrado: ${resultados.length} processos\n`);
  return resultados;
}

// ✅ INFERIR TRIBUNAL PELO NÚMERO CNJ
// Formato: NNNNNNN-DD.AAAA.J.TR.OOOO
// Exemplo: 0001234-56.2024.8.26.0100 → 8.26 → TJ-SP
function inferirTribunal(numeroProcesso) {
  if (!numeroProcesso) return 'Não identificado';
  
  try {
    const partes = numeroProcesso.split('.');
    if (partes.length >= 3) {
      const jtr = `${partes[2]}.${partes[3]}`;
      return MAPA_TRIBUNAIS[jtr] || 'Não identificado';
    }
  } catch (error) {
    console.error('Erro ao inferir tribunal:', error.message);
  }
  
  return 'Não identificado';
}

function extrairCredor(proc) {
  if (proc.partes && Array.isArray(proc.partes)) {
    const autor = proc.partes.find(p => 
      p.polo === 'ATIVO' || 
      p.tipo === 'AUTOR' ||
      p.tipoParte === 'AUTOR'
    );
    if (autor && autor.nome) {
      return autor.nome;
    }
  }
  return 'Consultar processo';
}

function determinarStatus(proc) {
  if (!proc.movimentos || !proc.movimentos.length) {
    return 'Em Análise';
  }
  const ultimo = proc.movimentos[proc.movimentos.length - 1];
  const nome = (ultimo.nome || '').toLowerCase();
  
  if (nome.includes('aprovad') || nome.includes('deferi')) return 'Aprovado';
  if (nome.includes('pendent') || nome.includes('aguard')) return 'Pendente';
  if (nome.includes('arquiv')) return 'Arquivado';
  
  return 'Em Análise';
}

function extrairNatureza(proc) {
  const assunto = (proc.assunto || '').toLowerCase();
  const classe = (proc.classe || '').toLowerCase();
  
  if (assunto.includes('aliment') || classe.includes('aliment')) return 'Alimentar';
  if (assunto.includes('tribut') || classe.includes('tribut')) return 'Tributária';
  if (assunto.includes('previd') || classe.includes('previd')) return 'Previdenciária';
  if (assunto.includes('trabalh') || classe.includes('trabalh')) return 'Trabalhista';
  
  return 'Comum';
}

function calcularAnoLOA(proc) {
  const data = proc.dataAjuizamento || proc.dataDistribuicao;
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
