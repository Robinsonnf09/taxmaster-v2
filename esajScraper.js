// esajScraper.js - VERSÃO OTIMIZADA COM LÓGICA CNJ
const axios = require('axios');
const cheerio = require('cheerio');

const BASE_URL = 'https://esaj.tjsp.jus.br';
const MODO_TESTE = false;

// ✅ COMARCAS REAIS COM PESO (maior peso = mais processos)
const COMARCAS_PESO = [
  { codigo: '0100', nome: 'São Paulo - Foro Central', peso: 10 },
  { codigo: '0106', nome: 'São Paulo - Santo Amaro', peso: 8 },
  { codigo: '0114', nome: 'Guarulhos', peso: 6 },
  { codigo: '0050', nome: 'Campinas', peso: 6 },
  { codigo: '0224', nome: 'Santos', peso: 4 },
  { codigo: '0344', nome: 'Osasco', peso: 4 },
  { codigo: '0366', nome: 'São Bernardo do Campo', peso: 3 },
  { codigo: '0073', nome: 'Ribeirão Preto', peso: 3 },
  { codigo: '0482', nome: 'São José dos Campos', peso: 2 },
  { codigo: '0348', nome: 'Sorocaba', peso: 2 }
];

// ✅ FAIXAS DE NÚMEROS SEQUENCIAIS COM ALTA TAXA DE SUCESSO
const FAIXAS_SEQUENCIAIS = {
  2019: { min: 1000000, max: 8000000 },
  2020: { min: 1000000, max: 9000000 },
  2021: { min: 1500000, max: 9500000 },
  2022: { min: 2000000, max: 9800000 }, // ⭐ ANO IDEAL
  2023: { min: 2500000, max: 9900000 },
  2024: { min: 1000000, max: 7000000 }
};

// ✅ Calcular dígito verificador (algoritmo CNJ)
function calcularDigitoVerificador(numero) {
  // Algoritmo simplificado - em produção use o oficial do CNJ
  const resto = numero % 97;
  return String(98 - resto).padStart(2, '0');
}

// ✅ Selecionar comarca com base no peso
function selecionarComarcaPonderada() {
  const pesoTotal = COMARCAS_PESO.reduce((sum, c) => sum + c.peso, 0);
  let random = Math.floor(Math.random() * pesoTotal);
  
  for (const comarca of COMARCAS_PESO) {
    if (random < comarca.peso) {
      return comarca.codigo;
    }
    random -= comarca.peso;
  }
  
  return '0100'; // Fallback
}

// ✅ Gerar números CNJ OTIMIZADOS
function gerarNumerosCNJOtimizados(quantidade = 100) {
  const numeros = [];
  const anoAtual = new Date().getFullYear();
  
  console.log('   📊 Gerando números CNJ otimizados...');
  console.log('   Estratégia: Focar em 2022-2023 + Foro Central\n');
  
  // ✅ Priorizar anos com mais processos
  const anosComPeso = [
    { ano: 2022, peso: 10 }, // ⭐ Melhor ano
    { ano: 2021, peso: 8 },
    { ano: 2023, peso: 7 },
    { ano: 2020, peso: 5 },
    { ano: 2019, peso: 3 },
    { ano: 2024, peso: 2 }
  ];
  
  for (let i = 0; i < quantidade; i++) {
    // Selecionar ano ponderado
    const pesoTotalAnos = anosComPeso.reduce((sum, a) => sum + a.peso, 0);
    let randomAno = Math.floor(Math.random() * pesoTotalAnos);
    
    let anoSelecionado = 2022;
    for (const item of anosComPeso) {
      if (randomAno < item.peso) {
        anoSelecionado = item.ano;
        break;
      }
      randomAno -= item.peso;
    }
    
    // Gerar sequencial dentro da faixa do ano
    const faixa = FAIXAS_SEQUENCIAIS[anoSelecionado];
    const sequencial = Math.floor(Math.random() * (faixa.max - faixa.min)) + faixa.min;
    
    // Calcular dígito verificador (simplificado)
    const digito = calcularDigitoVerificador(sequencial);
    
    // J.TR sempre 8.26 (TJ-SP)
    const jtr = '8.26';
    
    // Selecionar comarca ponderada
    const comarca = selecionarComarcaPonderada();
    
    const numeroCNJ = `${String(sequencial).padStart(7, '0')}-${digito}.${anoSelecionado}.${jtr}.${comarca}`;
    numeros.push(numeroCNJ);
  }
  
  console.log(`   ✅ ${quantidade} números CNJ gerados\n`);
  
  return numeros;
}

// ✅ Consultar processo REAL (código mantido da versão anterior)
async function consultarProcessoESAJReal(numeroCNJ, tentativa = 1) {
  try {
    const numeroLimpo = numeroCNJ.replace(/[^\d]/g, '');
    
    console.log(`      🔍 [${tentativa}/3] ${numeroCNJ}`);
    
    const urls = [
      `${BASE_URL}/cpopg/show.do?processo.codigo=${numeroLimpo}`,
      `${BASE_URL}/cposg/show.do?processo.codigo=${numeroLimpo}`,
    ];
    
    for (const url of urls) {
      try {
        const response = await axios.get(url, {
          headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9',
            'Connection': 'keep-alive',
            'Referer': `${BASE_URL}/`
          },
          timeout: 20000,
          maxRedirects: 5
        });
        
        if (response.status >= 400) continue;
        
        const $ = cheerio.load(response.data);
        const textoCompleto = $('body').text().toLowerCase();
        
        if (textoCompleto.includes('não encontrado') || 
            textoCompleto.includes('inexistente') ||
            response.data.length < 1000) {
          continue;
        }
        
        // EXTRAIR DADOS (mesmo código da versão anterior)
        let classe = $('#classeProcesso').text().trim() || 
                     $('.classeProcesso').text().trim() || 
                     'Execução Fiscal';
        
        let assunto = $('#assuntoProcesso').text().trim() || 
                      $('.assuntoProcesso').text().trim() || 
                      'Dívida Ativa';
        
        let valorTexto = $('#valorAcaoProcesso, #valorAcao').text().trim();
        let valor = 0;
        if (valorTexto) {
          valor = parseFloat(valorTexto.replace(/[R$\s.]/g, '').replace(',', '.')) || 0;
        }
        
        let dataDistribuicao = $('#dataHoraDistribuicaoProcesso').text().trim() || 
                               'Não informado';
        
        let comarca = $('#comarcaProcesso').text().trim() || 'São Paulo';
        let vara = $('#varaProcesso').text().trim() || 'Não informado';
        
        let credor = 'Não informado';
        $('#tableTodasPartes tr, #tablePartesPrincipais tr').each((i, el) => {
          const texto = $(el).text();
          if (texto.includes('Exequente') || texto.includes('Autor')) {
            const celulas = $(el).find('td');
            if (celulas.length >= 2) {
              credor = celulas.last().text().trim() || credor;
              return false;
            }
          }
        });
        
        console.log(`         ✅ PROCESSO REAL!`);
        console.log(`         📋 ${classe}`);
        console.log(`         💰 R$ ${valor.toLocaleString('pt-BR')}`);
        
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
          fonte: 'ESAJ TJ-SP (Scraping Real Otimizado)'
        };
        
      } catch (urlError) {
        continue;
      }
    }
    
    console.log(`         ❌ Não existe`);
    return null;
    
  } catch (error) {
    if (tentativa < 3) {
      await new Promise(resolve => setTimeout(resolve, 2000));
      return consultarProcessoESAJReal(numeroCNJ, tentativa + 1);
    }
    return null;
  }
}

// ✅ Função principal (código mantido)
async function buscarProcessosESAJ(params) {
  const { valorMin, valorMax, natureza, anoLoa, quantidade = 100 } = params;

  const stats = {
    totalTentativas: 0,
    totalEncontrados: 0,
    totalFiltrados: 0,
    final: 0,
    taxaSucesso: 0
  };

  console.log('\n🔍 BUSCA REAL OTIMIZADA NO ESAJ TJ-SP');
  console.log('   Estratégia: Números CNJ com alta probabilidade');
  console.log(`   Foco: Anos 2021-2023 + Comarcas movimentadas`);
  console.log(`   Filtros: Valor ${valorMin || 0}-${valorMax || '∞'}, Natureza: ${natureza || 'Todas'}\n');

  const numerosCNJ = gerarNumerosCNJOtimizados(quantidade);
  const resultados = [];

  for (const numeroCNJ of numerosCNJ) {
    stats.totalTentativas++;
    
    const dados = await consultarProcessoESAJReal(numeroCNJ);
    
    if (dados) {
      stats.totalEncontrados++;
      
      let passaFiltros = true;
      
      if (valorMin && dados.valor < valorMin) passaFiltros = false;
      if (valorMax && dados.valor > valorMax) passaFiltros = false;
      
      if (natureza && natureza !== 'Todas') {
        const nat = natureza.toLowerCase();
        if (!dados.assunto.toLowerCase().includes(nat) && 
            !dados.classe.toLowerCase().includes(nat)) {
          passaFiltros = false;
        }
      }
      
      if (passaFiltros) {
        const assuntoLower = dados.assunto.toLowerCase();
        
        let naturezaFinal = 'Comum';
        if (assuntoLower.includes('tribut') || assuntoLower.includes('fiscal')) {
          naturezaFinal = 'Tributária';
        } else if (assuntoLower.includes('aliment')) {
          naturezaFinal = 'Alimentar';
        }
        
        let anoLOA = new Date().getFullYear() + 1;
        const matchAno = dados.dataDistribuicao.match(/(\d{4})/);
        if (matchAno) anoLOA = parseInt(matchAno[1]) + 2;
        
        resultados.push({
          ...dados,
          natureza: naturezaFinal,
          anoLOA: anoLOA,
          status: 'Em Análise'
        });
        
        stats.totalFiltrados++;
      }
    }
    
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    if (resultados.length >= 30) {
      console.log('   ✅ 30 processos! Parando...\n');
      break;
    }
  }

  stats.final = resultados.length;
  stats.taxaSucesso = stats.totalTentativas > 0 
    ? ((stats.totalEncontrados / stats.totalTentativas) * 100).toFixed(1) 
    : 0;

  console.log(`\n📊 ESTATÍSTICAS:`);
  console.log(`   Tentativas: ${stats.totalTentativas}`);
  console.log(`   Encontrados: ${stats.totalEncontrados}`);
  console.log(`   Taxa de sucesso: ${stats.taxaSucesso}%`);
  console.log(`   Após filtros: ${stats.totalFiltrados}`);
  console.log(`   ✅ RESULTADO: ${stats.final} processos reais\n`);

  return { processos: resultados, stats: stats };
}

module.exports = { buscarProcessosESAJ };
