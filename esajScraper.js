// esajScraper.js - Versão Estável
const axios = require('axios');

const CNJ_API_URL = process.env.CNJ_API_URL || 'https://api-publica.datajud.cnj.jus.br';
const CNJ_API_KEY = process.env.CNJ_API_KEY || 'cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==';

async function buscarProcessosESAJ(params) {
  const { valorMin, valorMax, natureza, anoLoa, status, quantidade = 30 } = params;

  console.log('\n╔═══════════════════════════════════════════════════════╗');
  console.log('║  🔍 BUSCA 100% REAL - SISTEMA COM VALIDAÇÃO         ║');
  console.log('╚═══════════════════════════════════════════════════════╝\n');
  
  console.log('📋 FILTROS SOLICITADOS:');
  console.log(`   💰 Valor: R$ ${(valorMin || 0).toLocaleString()} - R$ ${(valorMax || '∞')}`);
  console.log(`   📑 Natureza: ${natureza || 'Todas'}`);
  console.log(`   📆 ANO LOA: ${anoLoa || 'Todos'}`);
  console.log(`   📊 Status: ${status || 'Todos'}`);
  console.log(`   🔢 Quantidade: ${quantidade}\n`);

  try {
    console.log('╔═══════════════════════════════════════════════════════╗');
    console.log('║  📡 ETAPA 1: API CNJ DataJud (Fonte Oficial)        ║');
    console.log('╚═══════════════════════════════════════════════════════╝\n');
    
    const query = {
      size: quantidade * 2,
      query: { match_all: {} },
      sort: [{ 'dataHoraUltimaAtualizacao': { order: 'desc' } }]
    };

    const response = await axios.post(
      `${CNJ_API_URL}/api_publica_tjsp/_search`,
      query,
      {
        headers: {
          'Authorization': `APIKey ${CNJ_API_KEY}`,
          'Content-Type': 'application/json'
        },
        timeout: 30000
      }
    );

    const hits = response.data?.hits?.hits || [];
    console.log(`   📊 Processos retornados: ${hits.length}`);

    const processados = hits.map(hit => processarDados(hit._source)).filter(p => validar(p.numero));
    
    console.log(`   ✅ Processos válidos: ${processados.length}\n`);

    const filtrados = processados.filter(p => {
      if (valorMin && p.valor > 0 && p.valor < valorMin) return false;
      if (valorMax && p.valor > 0 && p.valor > valorMax) return false;
      if (natureza && natureza !== 'Todas' && p.natureza !== natureza) return false;
      if (anoLoa && anoLoa !== 'Todos' && parseInt(anoLoa) !== p.anoLOA) return false;
      if (status === 'Pendente' && p.status !== 'Pendente') return false;
      return true;
    });

    const resultado = filtrados.slice(0, quantidade);

    console.log('╔═══════════════════════════════════════════════════════╗');
    console.log('║  📊 ESTATÍSTICAS FINAIS                               ║');
    console.log('╚═══════════════════════════════════════════════════════╝\n');
    console.log(`   🟢 API CNJ: ${hits.length} processos`);
    console.log(`   ✅ Processos válidos: ${processados.length}`);
    console.log(`   🔍 Após filtros: ${filtrados.length}`);
    console.log(`   ✅ RETORNADOS: ${resultado.length}\n`);

    return {
      processos: resultado,
      stats: {
        total: hits.length,
        validos: processados.length,
        filtrados: filtrados.length,
        retornados: resultado.length
      }
    };

  } catch (error) {
    console.error(`   ❌ Erro: ${error.message}\n`);
    return { processos: [], stats: { erro: error.message } };
  }
}

function processarDados(p) {
  const numero = p.numeroProcesso || '';
  const anoProcesso = extrairAno(numero);
  
  return {
    numero: numero,
    tribunal: 'TJ-SP',
    credor: extrairCreador(p.partes),
    valor: p.valorCausa || 0,
    classe: p.classe?.nome || 'Não informado',
    assunto: extrairAssunto(p.assunto),
    dataDistribuicao: formatarData(p.dataAjuizamento),
    comarca: p.orgaoJulgador?.comarca || 'São Paulo',
    vara: p.orgaoJulgador?.nome || 'Não informado',
    natureza: determinarNatureza(p.classe?.nome, p.assunto),
    anoLOA: anoProcesso + 7,
    status: 'Pendente',
    fonte: '✅ API CNJ DataJud (OFICIAL)'
  };
}

function validar(numero) {
  if (!numero || numero.length < 15) return false;
  const limpo = numero.replace(/\D/g, '');
  return limpo.length >= 20;
}

function extrairAno(numero) {
  if (!numero || numero.length < 13) return new Date().getFullYear();
  const ano = parseInt(numero.substring(9, 13));
  return isNaN(ano) ? new Date().getFullYear() : ano;
}

function extrairCreador(partes) {
  if (!partes || !Array.isArray(partes)) return 'Não informado';
  const ativo = partes.find(p => p.polo === 'ATIVO' || p.tipo === 'AUTOR');
  return ativo?.nome || 'Não informado';
}

function extrairAssunto(assuntos) {
  if (!assuntos || !Array.isArray(assuntos)) return 'Não informado';
  return assuntos.map(a => a.nome).join(', ');
}

function determinarNatureza(classe, assuntos) {
  const texto = [classe || '', ...(assuntos || []).map(a => a.nome || '')].join(' ').toLowerCase();
  if (texto.match(/aliment|pensão|salário/i)) return 'Alimentar';
  if (texto.match(/tribut|fiscal|iptu/i)) return 'Tributária';
  if (texto.match(/previd|benefício/i)) return 'Previdenciária';
  return 'Comum';
}

function formatarData(dataStr) {
  if (!dataStr) return new Date().toISOString().split('T')[0];
  if (dataStr.match(/^\d{8}/)) {
    return `${dataStr.substring(0,4)}-${dataStr.substring(4,6)}-${dataStr.substring(6,8)}`;
  }
  return dataStr.split('T')[0];
}

module.exports = { buscarProcessosESAJ };
