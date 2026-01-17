// esajScraper.js - VERSÃO DEBUG + TESTE
const axios = require('axios');
const cheerio = require('cheerio');

const BASE_URL = 'https://esaj.tjsp.jus.br';

// MODO DE OPERAÇÃO
const MODO_TESTE = true; // Alterar para false quando scraping real funcionar

// Gerar dados de teste REALISTAS
function gerarDadosTeste(params) {
  const { valorMin, valorMax, natureza, quantidade = 50 } = params;
  
  console.log('\n📊 MODO TESTE ATIVO - Gerando dados realistas...');
  console.log(`   Filtros: Valor ${valorMin || 0} - ${valorMax || '∞'}, Natureza: ${natureza || 'Todas'}\n`);
  
  const processos = [];
  const ano = new Date().getFullYear();
  
  // Classes e assuntos por natureza
  const dadosPorNatureza = {
    'Alimentar': {
      classes: ['Execução de Alimentos', 'Ação de Alimentos', 'Revisional de Alimentos'],
      assuntos: [
        'Alimentos - Pensão Alimentícia',
        'Cumprimento de Sentença - Alimentos',
        'Revisão de Alimentos',
        'Execução de Alimentos - Prisão Civil'
      ],
      credores: [
        'MARIA DA SILVA SANTOS',
        'JOSÉ OLIVEIRA SOUZA',
        'ANA PAULA COSTA',
        'CARLOS EDUARDO LIMA'
      ],
      valorMin: 5000,
      valorMax: 100000
    },
    'Tributária': {
      classes: ['Execução Fiscal', 'Ação Anulatória de Débito Fiscal', 'Mandado de Segurança Fiscal'],
      assuntos: [
        'IPTU / Imposto Predial e Territorial Urbano',
        'ISS / Imposto sobre Serviços',
        'ICMS / Imposto sobre Circulação de Mercadorias',
        'Dívida Ativa Municipal',
        'Dívida Ativa Estadual'
      ],
      credores: [
        'MUNICÍPIO DE SÃO PAULO',
        'FAZENDA DO ESTADO DE SÃO PAULO',
        'PREFEITURA MUNICIPAL DE CAMPINAS',
        'FAZENDA PÚBLICA MUNICIPAL'
      ],
      valorMin: 10000,
      valorMax: 5000000
    },
    'Comum': {
      classes: ['Procedimento Comum Cível', 'Ação de Cobrança', 'Ação Ordinária'],
      assuntos: [
        'Cobrança de Aluguéis',
        'Indenização por Danos Materiais',
        'Rescisão de Contrato',
        'Cobrança de Honorários'
      ],
      credores: [
        'EMPRESA XYZ LTDA',
        'CONDOMÍNIO EDIFÍCIO PAULISTA',
        'IMOBILIÁRIA ABC S.A.',
        'CONSTRUTORA DEF LTDA'
      ],
      valorMin: 20000,
      valorMax: 1000000
    },
    'Previdenciária': {
      classes: ['Procedimento Comum Previdenciário', 'Mandado de Segurança Previdenciário'],
      assuntos: [
        'Aposentadoria por Tempo de Contribuição',
        'Auxílio-Doença',
        'Pensão por Morte',
        'Revisão de Benefício'
      ],
      credores: [
        'JOÃO CARLOS PEREIRA',
        'ANTÔNIA MARIA SILVA',
        'PEDRO HENRIQUE SANTOS',
        'LUIZA FERREIRA COSTA'
      ],
      valorMin: 15000,
      valorMax: 200000
    }
  };
  
  // Se natureza não especificada, usar todas
  const naturezas = natureza && natureza !== 'Todas' 
    ? [natureza] 
    : Object.keys(dadosPorNatureza);
  
  for (let i = 0; i < quantidade; i++) {
    // Escolher natureza aleatória
    const natEscolhida = naturezas[Math.floor(Math.random() * naturezas.length)];
    const dados = dadosPorNatureza[natEscolhida];
    
    // Gerar número CNJ realista
    const sequencial = String(Math.floor(Math.random() * 9999999)).padStart(7, '0');
    const digito = String(Math.floor(Math.random() * 99)).padStart(2, '0');
    const anoProcesso = ano - Math.floor(Math.random() * 5);
    const comarca = ['0100', '0106', '0050', '0224'][Math.floor(Math.random() * 4)];
    const numeroProcesso = `${sequencial}-${digito}.${anoProcesso}.8.26.${comarca}`;
    
    // Gerar valor dentro da faixa da natureza
    let valor = Math.floor(Math.random() * (dados.valorMax - dados.valorMin)) + dados.valorMin;
    
    // Aplicar filtros de valor
    if (valorMin && valorMax) {
      // Se está fora da faixa, ajustar
      if (valor < valorMin || valor > valorMax) {
        valor = Math.floor(Math.random() * (valorMax - valorMin)) + valorMin;
      }
    }
    
    // Se ainda está fora da faixa, pular este processo
    if (valorMin && valor < valorMin) continue;
    if (valorMax && valor > valorMax) continue;
    
    const classe = dados.classes[Math.floor(Math.random() * dados.classes.length)];
    const assunto = dados.assuntos[Math.floor(Math.random() * dados.assuntos.length)];
    const credor = dados.credores[Math.floor(Math.random() * dados.credores.length)];
    
    const mes = String(Math.floor(Math.random() * 12) + 1).padStart(2, '0');
    const dia = String(Math.floor(Math.random() * 28) + 1).padStart(2, '0');
    
    processos.push({
      numero: numeroProcesso,
      tribunal: 'TJ-SP',
      credor: credor,
      valor: valor,
      status: ['Em Análise', 'Pendente', 'Aprovado'][Math.floor(Math.random() * 3)],
      natureza: natEscolhida,
      anoLOA: anoProcesso + 2,
      dataDistribuicao: `${dia}/${mes}/${anoProcesso}`,
      classe: classe,
      assunto: assunto,
      fonte: 'ESAJ TJ-SP (MODO TESTE - Dados Simulados)',
      comarca: ['São Paulo - Capital', 'Campinas', 'Santos', 'Santo Amaro'][Math.floor(Math.random() * 4)],
      vara: `${Math.floor(Math.random() * 10) + 1}ª Vara Cível`
    });
  }
  
  console.log(`   ✅ ${processos.length} processos gerados\n`);
  
  return processos;
}

// Scraping REAL (será ativado depois)
async function consultarProcessoESAJReal(numeroCNJ) {
  // TODO: Implementar scraping real
  console.log(`      🔍 Consultando REAL: ${numeroCNJ} (em desenvolvimento)`);
  return null;
}

// Função principal
async function buscarProcessosESAJ(params) {
  const {
    valorMin,
    valorMax,
    natureza,
    anoLoa,
    quantidade = 50
  } = params;

  const stats = {
    totalAPI: 0,
    final: 0,
    modo: MODO_TESTE ? 'TESTE' : 'REAL'
  };

  console.log('\n🔍 BUSCA NO ESAJ TJ-SP');
  console.log(`   Modo: ${stats.modo}`);
  console.log(`   Filtros aplicados:`);
  console.log(`      Valor: ${valorMin || 0} - ${valorMax || '∞'}`);
  console.log(`      Natureza: ${natureza || 'Todas'}`);
  console.log(`      ANO LOA: ${anoLoa || 'Todos'}`);

  let resultados = [];

  if (MODO_TESTE) {
    // MODO TESTE: Retornar dados simulados
    resultados = gerarDadosTeste({ valorMin, valorMax, natureza, quantidade });
    
    // Aplicar filtro de ANO LOA
    if (anoLoa && anoLoa !== 'Todos') {
      resultados = resultados.filter(p => p.anoLOA === parseInt(anoLoa));
    }
    
    stats.totalAPI = resultados.length;
    stats.final = resultados.length;
    
  } else {
    // MODO REAL: Scraping do ESAJ
    console.log('   ⚠️ Modo REAL ainda em desenvolvimento');
    // TODO: Implementar scraping real aqui
  }

  console.log(`\n📊 ESTATÍSTICAS:`);
  console.log(`   Total gerado: ${stats.totalAPI}`);
  console.log(`   ✅ RESULTADO FINAL: ${stats.final} processos\n`);

  return {
    processos: resultados,
    stats: stats
  };
}

module.exports = { buscarProcessosESAJ };
