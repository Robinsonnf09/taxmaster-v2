// datajudOficialAdapter.js
const axios = require('axios');

const BASE_URL = 'https://datajud-wiki.cnj.jus.br/api-publica/v1/processos';

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

  // ✅ ESTATÍSTICAS
  const stats = {
    totalAPI: 0,
    aposTribunal: 0,
    aposValor: 0,
    aposNatureza: 0,
    aposAnoLOA: 0,
    final: 0,
    filtrosAplicados: []
  };

  console.log('\n🔍 BUSCA OFICIAL DATAJUD CNJ');
  console.log('   Endpoint:', BASE_URL);
  console.log('   Período:', dataInicio, 'até', dataFim);

  if (tribunalDesejado) stats.filtrosAplicados.push(`Tribunal: ${tribunalDesejado}`);
  if (valorMin) stats.filtrosAplicados.push(`Valor Min: R$ ${valorMin.toLocaleString('pt-BR')}`);
  if (valorMax) stats.filtrosAplicados.push(`Valor Max: R$ ${valorMax.toLocaleString('pt-BR')}`);
  if (natureza) stats.filtrosAplicados.push(`Natureza: ${natureza}`);
  if (anoLoa) stats.filtrosAplicados.push(`ANO LOA: ${anoLoa}`);

  console.log('   Filtros aplicados:', stats.filtrosAplicados.length || 'Nenhum');

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

      const response = await requestComRetry(url, 3);
      const data = response.data;

      const processos = data?.conteudo || data?.content || data || [];

      stats.totalAPI += processos.length;
      console.log(`      API retornou: ${processos.length} processos (Total acumulado: ${stats.totalAPI})`);

      if (pagina === 0 && processos.length > 0) {
        console.log('\n      📋 AMOSTRA (primeiros 3 processos):');
        processos.slice(0, 3).forEach((proc, i) => {
          const tribunalInf = inferirTribunal(proc.numeroProcesso || '');
          console.log(`      ${i + 1}. Número: ${proc.numeroProcesso || 'N/A'}`);
          console.log(`         Tribunal inferido: ${tribunalInf}`);
          console.log(`         Valor: R$ ${Number(proc.valorCausa || 0).toLocaleString('pt-BR')}`);
          console.log(`         Classe: ${proc.classe || 'N/A'}`);
        });
        console.log('');
      }

      if (!processos.length) {
        terminou = true;
        break;
      }

      // ✅ FILTRAR COM ESTATÍSTICAS
      const filtrados = processos.filter((proc) => {
        const valorCausa = Number(proc.valorCausa || 0);
        const classe = (proc.classe || '').toString().toLowerCase();
        const assunto = (proc.assunto || '').toString().toLowerCase();
        const dataAjuizamento = proc.dataAjuizamento || proc.dataDistribuicao;
        const numeroProcesso = proc.numeroProcesso || '';

        const tribunalInferido = inferirTribunal(numeroProcesso);

        // Filtro tribunal
        if (tribunalDesejado && tribunalInferido !== tribunalDesejado) {
          return false;
        }
        stats.aposTribunal++;

        // Filtro valor
        if (valorMin != null && !Number.isNaN(valorMin) && valorCausa < valorMin) {
          return false;
        }
        if (valorMax != null && !Number.isNaN(valorMax) && valorCausa > valorMax) {
          return false;
        }
        stats.aposValor++;

        // Filtro natureza
        if (natureza) {
          const nat = natureza.toString().toLowerCase();
          if (!classe.includes(nat) && !assunto.includes(nat)) {
            return false;
          }
        }
        stats.aposNatureza++;

        // Filtro ano LOA
        if (anoLoa && dataAjuizamento) {
          const anoProc = new Date(dataAjuizamento).getFullYear();
          const loaProc = anoProc + 2;
          if (loaProc !== Number(anoLoa)) {
            return false;
          }
        }
        stats.aposAnoLOA++;

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
        console.log('   ⚠️ Limite atingido (20 páginas ou 200 processos)');
        terminou = true;
      }

    } catch (error) {
      console.error(`   ❌ Erro na página ${pagina}:`, error.message);
      terminou = true;
    }
  }

  stats.final = resultados.length;

  console.log(`\n📊 ESTATÍSTICAS DA BUSCA:`);
  console.log(`   Total retornado pela API: ${stats.totalAPI}`);
  if (tribunalDesejado) console.log(`   Após filtro Tribunal: ${stats.aposTribunal}`);
  if (valorMin || valorMax) console.log(`   Após filtro Valor: ${stats.aposValor}`);
  if (natureza) console.log(`   Após filtro Natureza: ${stats.aposNatureza}`);
  if (anoLoa) console.log(`   Após filtro ANO LOA: ${stats.aposAnoLOA}`);
  console.log(`   ✅ RESULTADO FINAL: ${stats.final} processos\n`);

  return {
    processos: resultados,
    stats: stats
  };
}

async function requestComRetry(url, maxTentativas = 3) {
  let ultimoErro;
  
  for (let tentativa = 1; tentativa <= maxTentativas; tentativa++) {
    try {
      const response = await axios.get(url, {
        timeout: 30000,
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'TaxMaster/3.0'
        }
      });
      return response;
    } catch (error) {
      ultimoErro = error;
      const status = error.response?.status;
      
      if (status === 502 || status === 503 || status === 504 || error.code === 'ETIMEDOUT') {
        console.log(`      ⚠️ Tentativa ${tentativa}/${maxTentativas} falhou`);
        
        if (tentativa < maxTentativas) {
          const delay = tentativa * 1000;
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      } else {
        throw error;
      }
    }
  }
  throw ultimoErro;
}

function inferirTribunal(numeroProcesso) {
  if (!numeroProcesso) return 'Não identificado';
  
  try {
    const partes = numeroProcesso.split('.');
    
    if (partes.length >= 4) {
      const j = partes[2];
      let tr = partes[3];
      
      if (tr.length > 2) {
        tr = tr.substring(0, 2);
      }
      
      const jtr = `${j}.${tr}`;
      const tribunal = MAPA_TRIBUNAIS[jtr];
      
      if (tribunal) return tribunal;
    }
    
    const somenteNumeros = numeroProcesso.replace(/\D/g, '');
    
    if (somenteNumeros.length === 20) {
      const j = somenteNumeros.substring(13, 14);
      const tr = somenteNumeros.substring(14, 16);
      const jtr = `${j}.${tr}`;
      
      const tribunal = MAPA_TRIBUNAIS[jtr];
      if (tribunal) return tribunal;
    }
    
    const match = numeroProcesso.match(/\.(\d)\.(\d{2})/);
    if (match) {
      const jtr = `${match[1]}.${match[2]}`;
      const tribunal = MAPA_TRIBUNAIS[jtr];
      if (tribunal) return tribunal;
    }
    
  } catch (error) {
    console.error('Erro ao inferir tribunal:', error.message);
  }
  
  return 'Não identificado';
}

function extrairCredor(proc) {
  if (proc.partes && Array.isArray(proc.partes)) {
    const autor = proc.partes.find(p => 
      p.polo === 'ATIVO' || p.tipo === 'AUTOR' || p.tipoParte === 'AUTOR'
    );
    if (autor && autor.nome) return autor.nome;
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
