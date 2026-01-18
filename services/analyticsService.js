// services/analyticsService.js - Analytics e BI
const logger = require('../config/logger');

class AnalyticsService {
  constructor() {
    this.metricas = new Map();
  }

  calcularEstatisticas(processos) {
    logger.info(`📊 Calculando estatísticas para ${processos.length} processos`);

    const stats = {
      total: processos.length,
      valorTotal: 0,
      valorMedio: 0,
      valorMediano: 0,
      maiorValor: 0,
      menorValor: Infinity,
      porNatureza: {},
      porLOA: {},
      porStatus: {},
      porTribunal: {},
      valorPorNatureza: {},
      valorPorLOA: {},
      distribuicaoValores: {
        ate10k: 0,
        de10ka50k: 0,
        de50ka100k: 0,
        de100ka500k: 0,
        acima500k: 0
      },
      tendencias: {
        crescimentoMensal: 0,
        previsaoProximoMes: 0
      }
    };

    const valores = [];

    processos.forEach(p => {
      const valor = p.valor || 0;
      valores.push(valor);
      
      stats.valorTotal += valor;
      stats.maiorValor = Math.max(stats.maiorValor, valor);
      stats.menorValor = Math.min(stats.menorValor, valor);

      // Distribuição
      if (valor <= 10000) stats.distribuicaoValores.ate10k++;
      else if (valor <= 50000) stats.distribuicaoValores.de10ka50k++;
      else if (valor <= 100000) stats.distribuicaoValores.de50ka100k++;
      else if (valor <= 500000) stats.distribuicaoValores.de100ka500k++;
      else stats.distribuicaoValores.acima500k++;

      // Agrupamentos
      stats.porNatureza[p.natureza] = (stats.porNatureza[p.natureza] || 0) + 1;
      stats.porLOA[p.anoLOA] = (stats.porLOA[p.anoLOA] || 0) + 1;
      stats.porStatus[p.status] = (stats.porStatus[p.status] || 0) + 1;
      stats.porTribunal[p.tribunal] = (stats.porTribunal[p.tribunal] || 0) + 1;
      
      stats.valorPorNatureza[p.natureza] = (stats.valorPorNatureza[p.natureza] || 0) + valor;
      stats.valorPorLOA[p.anoLOA] = (stats.valorPorLOA[p.anoLOA] || 0) + valor;
    });

    // Cálculos finais
    stats.valorMedio = processos.length > 0 ? stats.valorTotal / processos.length : 0;
    stats.valorMediano = this.calcularMediana(valores);
    stats.menorValor = stats.menorValor === Infinity ? 0 : stats.menorValor;

    // Top 10 processos
    stats.top10MaioresValores = processos
      .sort((a, b) => (b.valor || 0) - (a.valor || 0))
      .slice(0, 10)
      .map(p => ({
        numero: p.numero,
        credor: p.credor,
        valor: p.valor,
        natureza: p.natureza
      }));

    logger.info('✅ Estatísticas calculadas');
    return stats;
  }

  calcularMediana(valores) {
    if (valores.length === 0) return 0;
    
    const sorted = valores.sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    
    return sorted.length % 2 !== 0
      ? sorted[mid]
      : (sorted[mid - 1] + sorted[mid]) / 2;
  }

  gerarRelatorioExecutivo(processos, stats) {
    return {
      resumo: {
        totalProcessos: stats.total,
        valorTotal: stats.valorTotal,
        valorMedio: stats.valorMedio,
        periodo: new Date().toLocaleDateString('pt-BR')
      },
      distribuicao: {
        porNatureza: stats.porNatureza,
        porStatus: stats.porStatus,
        porLOA: stats.porLOA
      },
      financeiro: {
        valorPorNatureza: stats.valorPorNatureza,
        maiorProcesso: stats.maiorValor,
        menorProcesso: stats.menorValor,
        distribuicaoFaixas: stats.distribuicaoValores
      },
      destaques: stats.top10MaioresValores,
      metadata: {
        dataGeracao: new Date().toISOString(),
        versao: '3.0.0'
      }
    };
  }

  registrarMetrica(nome, valor) {
    if (!this.metricas.has(nome)) {
      this.metricas.set(nome, []);
    }
    
    this.metricas.get(nome).push({
      valor,
      timestamp: new Date()
    });

    logger.debug(`📈 Métrica registrada: ${nome} = ${valor}`);
  }

  obterMetricas(nome) {
    return this.metricas.get(nome) || [];
  }
}

module.exports = new AnalyticsService();
