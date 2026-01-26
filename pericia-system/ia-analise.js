class IAAnaliseViabilidade {
    analisarOportunidade(oportunidade) {
        let score = 0;
        
        // Analise de Honorarios (40%)
        if (oportunidade.honorariosEstimados >= 40000) score += 40;
        else if (oportunidade.honorariosEstimados >= 20000) score += 35;
        else if (oportunidade.honorariosEstimados >= 10000) score += 30;
        else score += 20;
        
        // Analise de Tribunal (30%)
        const tribunaisTop = ['TJ-SP', 'TRF3', 'TJ-RJ'];
        if (tribunaisTop.includes(oportunidade.tribunal)) score += 30;
        else score += 20;
        
        // Urgencia (20%)
        if (oportunidade.urgencia === 'alta') score += 15;
        else if (oportunidade.urgencia === 'media') score += 20;
        else score += 18;
        
        // Especialidade (10%)
        score += 10;
        
        return {
            score: Math.min(100, score),
            classificacao: score >= 85 ? 'Excelente' : score >= 70 ? 'Muito Bom' : score >= 60 ? 'Bom' : 'Regular',
            recomendacao: score >= 85 ? 'FORTEMENTE RECOMENDADO' : score >= 70 ? 'RECOMENDADO' : 'AVALIAR',
            pontos_fortes: this.identificarPontosFortes(oportunidade),
            roi_estimado: {
                honorarios: oportunidade.honorariosEstimados,
                custo_estimado: oportunidade.honorariosEstimados * 0.15,
                lucro_estimado: oportunidade.honorariosEstimados * 0.85
            }
        };
    }
    
    identificarPontosFortes(oportunidade) {
        const pontos = [];
        if (oportunidade.honorariosEstimados >= 30000) pontos.push('Honorarios excelentes');
        if (['TJ-SP', 'TRF3'].includes(oportunidade.tribunal)) pontos.push('Tribunal de alta reputacao');
        if (oportunidade.score >= 80) pontos.push('Score de viabilidade alto');
        return pontos;
    }
    
    analisarLote(oportunidades) {
        return oportunidades.map(o => ({
            ...o,
            analise_ia: this.analisarOportunidade(o)
        })).sort((a, b) => b.analise_ia.score - a.analise_ia.score);
    }
}

module.exports = new IAAnaliseViabilidade();
