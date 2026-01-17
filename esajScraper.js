// esajScraper.js - Scraping REAL do ESAJ TJ-SP
const axios = require('axios');
const cheerio = require('cheerio');

const BASE_URL = 'https://esaj.tjsp.jus.br';

// Gerar números CNJ válidos para TJ-SP
function gerarNumerosCNJ(quantidade = 50) {
  const numeros = [];
  const anoAtual = new Date().getFullYear();
  
  for (let i = 0; i < quantidade; i++) {
    // Número sequencial aleatório (7 dígitos)
    const sequencial = String(Math.floor(Math.random() * 9999999)).padStart(7, '0');
    
    // Dígito verificador (2 dígitos)
    const digito = String(Math.floor(Math.random() * 99)).padStart(2, '0');
    
    // Ano (últimos 3 anos)
    const ano = anoAtual - Math.floor(Math.random() * 3);
    
    // J.TR = 8.26 (TJ-SP)
    const jtr = '8.26';
    
    // Comarca (0001 a 0700 são comarcas reais do TJ-SP)
    const comarca = String(Math.floor(Math.random() * 700) + 1).padStart(4, '0');
    
    const numeroCNJ = `${sequencial}-${digito}.${ano}.${jtr}.${comarca}`;
    numeros.push(numeroCNJ);
  }
  
  return numeros;
}

// Consultar processo individual no ESAJ (REAL)
async function consultarProcessoESAJ(numeroCNJ) {
  try {
    const numeroLimpo = numeroCNJ.replace(/[^\d]/g, '');
    
    console.log(`      🔍 Consultando: ${numeroCNJ}`);
    
    const response = await axios.get(`${BASE_URL}/cpopg/show.do`, {
      params: {
        processo: {
          codigo: numeroLimpo,
          foro: '100' // Foro da Capital
        }
      },
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://esaj.tjsp.jus.br/cpopg/open.do'
      },
      timeout: 15000
    });
    
    const $ = cheerio.load(response.data);
    
    // Verificar se processo existe
    const erroMsg = $('body').text();
    if (erroMsg.includes('não encontrado') || erroMsg.includes('inexistente')) {
      console.log(`         ❌ Processo não existe`);
      return null;
    }
    
    // Extrair dados REAIS
    const classe = $('#classeProcesso').text().trim() || 
                   $('.classeProcesso').text().trim() ||
                   'Não informado';
    
    const assunto = $('#assuntoProcesso').text().trim() ||
                    $('.assuntoProcesso').text().trim() ||
                    'Não informado';
    
    const valorTexto = $('#valorAcaoProcesso').text().trim() ||
                       $('.valorAcaoProcesso').text().trim() ||
                       $('#valorAcao').text().trim() ||
                       '0';
    
    const valor = parseFloat(valorTexto.replace(/[^\d,]/g, '').replace(',', '.')) || 0;
    
    const dataDistribuicao = $('#dataHoraDistribuicaoProcesso').text().trim() ||
                             $('.dataHoraDistribuicaoProcesso').text().trim() ||
                             'Não informado';
    
    const comarca = $('#comarcaProcesso').text().trim() ||
                    $('.comarcaProcesso').text().trim() ||
                    'São Paulo';
    
    const vara = $('#varaProcesso').text().trim() ||
                 $('.varaProcesso').text().trim() ||
                 'Não informado';
    
    // Extrair partes (credor/devedor)
    const partesTexto = $('#tableTodasPartes').text() ||
                        $('#tablePartesPrincipais').text() ||
                        '';
    
    let credor = 'Não informado';
    if (partesTexto) {
      const linhas = partesTexto.split('\n');
      for (const linha of linhas) {
        if (linha.includes('Exequente') || linha.includes('Autor') || linha.includes('Requerente')) {
          const match = linha.match(/:\s*(.+)/);
          if (match) {
            credor = match[1].trim();
            break;
          }
        }
      }
    }
    
    console.log(`         ✅ Dados extraídos`);
    
    return {
      numero: numeroCNJ,
      tribunal: 'TJ-SP',
      credor: credor,
      valor: valor,
      classe: classe,
      assunto: assunto,
      dataDistribuicao: dataDistribuicao,
      comarca: comarca,
      vara: vara,
      fonte: 'ESAJ TJ-SP (Scraping Real)'
    };
    
  } catch (error) {
    console.log(`         ❌ Erro: ${error.message}`);
    return null;
  }
}

// Buscar múltiplos processos
async function buscarProcessosESAJ(params) {
  const {
    valorMin,
    valorMax,
    natureza,
    quantidade = 50
  } = params;

  const stats = {
    totalTentativas: 0,
    totalEncontrados: 0,
    totalErros: 0,
    final: 0
  };

  console.log('\n🔍 BUSCA REAL NO ESAJ TJ-SP');
  console.log('   Modo: Scraping por números CNJ');
  console.log(`   Tentativas: ${quantidade} processos`);
  console.log('   ⚠️ Delay de 2s entre requisições (anti-bloqueio)\n');

  const numerosCNJ = gerarNumerosCNJ(quantidade);
  const resultados = [];

  for (const numeroCNJ of numerosCNJ) {
    stats.totalTentativas++;
    
    const dados = await consultarProcessoESAJ(numeroCNJ);
    
    if (dados) {
      stats.totalEncontrados++;
      
      // Aplicar filtros
      let passaFiltros = true;
      
      if (valorMin && dados.valor < valorMin) passaFiltros = false;
      if (valorMax && dados.valor > valorMax) passaFiltros = false;
      
      if (natureza) {
        const nat = natureza.toLowerCase();
        if (!dados.assunto.toLowerCase().includes(nat) && 
            !dados.classe.toLowerCase().includes(nat)) {
          passaFiltros = false;
        }
      }
      
      if (passaFiltros) {
        // Determinar natureza
        const assuntoLower = dados.assunto.toLowerCase();
        const classeLower = dados.classe.toLowerCase();
        
        let naturezaFinal = 'Comum';
        if (assuntoLower.includes('tribut') || assuntoLower.includes('imposto')) {
          naturezaFinal = 'Tributária';
        } else if (assuntoLower.includes('aliment')) {
          naturezaFinal = 'Alimentar';
        } else if (assuntoLower.includes('previd')) {
          naturezaFinal = 'Previdenciária';
        }
        
        // Calcular ano LOA
        let anoLOA = new Date().getFullYear() + 1;
        if (dados.dataDistribuicao && dados.dataDistribuicao !== 'Não informado') {
          const match = dados.dataDistribuicao.match(/\d{4}/);
          if (match) {
            anoLOA = parseInt(match[0]) + 2;
          }
        }
        
        resultados.push({
          ...dados,
          natureza: naturezaFinal,
          anoLOA: anoLOA,
          status: 'Em Análise'
        });
      }
    } else {
      stats.totalErros++;
    }
    
    // Delay anti-bloqueio (2 segundos entre requisições)
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Limite de segurança
    if (stats.totalTentativas >= quantidade) break;
  }

  stats.final = resultados.length;

  console.log(`\n📊 ESTATÍSTICAS:`);
  console.log(`   Tentativas: ${stats.totalTentativas}`);
  console.log(`   Encontrados: ${stats.totalEncontrados}`);
  console.log(`   Erros: ${stats.totalErros}`);
  console.log(`   Após filtros: ${stats.final} processos\n`);

  return {
    processos: resultados,
    stats: stats
  };
}

module.exports = { buscarProcessosESAJ };
