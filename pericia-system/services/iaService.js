const { Configuration, OpenAIApi } = require('openai');

class IAService {
    constructor() {
        const configuration = new Configuration({
            apiKey: process.env.OPENAI_API_KEY
        });
        this.openai = new OpenAIApi(configuration);
    }
    
    async analisarOportunidade(oportunidade) {
        try {
            const prompt = `
Analise esta oportunidade de perícia judicial e forneça:
1. Honorários recomendados (baseado no valor da causa e complexidade)
2. Score de atratividade (0-100)
3. Pontos de atenção
4. Recomendações

Dados:
- Tribunal: ${oportunidade.tribunal}
- Valor da Causa: R$ ${oportunidade.valorCausa}
- Especialidade: ${oportunidade.especialidade}
- Prazo: ${oportunidade.prazo}

Forneça a resposta em formato JSON com as chaves: honorariosRecomendados, score, pontosAtencao (array), recomendacoes (array).
            `;
            
            const response = await this.openai.createChatCompletion({
                model: "gpt-3.5-turbo",
                messages: [{ role: "user", content: prompt }],
                temperature: 0.7,
                max_tokens: 500
            });
            
            const analise = JSON.parse(response.data.choices[0].message.content);
            return analise;
        } catch (error) {
            console.error('Erro na análise IA:', error);
            return this.analiseManual(oportunidade);
        }
    }
    
    analiseManual(oportunidade) {
        // Análise baseada em regras se IA falhar
        const valorCausa = parseFloat(oportunidade.valorCausa);
        const complexidade = parseFloat(oportunidade.complexidade) || 1.5;
        
        const honorariosRecomendados = Math.max(
            valorCausa * 0.01,
            (oportunidade.horasEstimadas || 40) * 450 * complexidade
        );
        
        let score = 50;
        if (honorariosRecomendados > 100000) score += 20;
        if (honorariosRecomendados > 50000) score += 10;
        if (complexidade >= 2) score += 15;
        
        const diasParaPrazo = Math.floor(
            (new Date(oportunidade.prazo) - new Date()) / (1000 * 60 * 60 * 24)
        );
        if (diasParaPrazo < 7) score += 5;
        
        return {
            honorariosRecomendados: Math.round(honorariosRecomendados),
            score: Math.min(100, score),
            pontosAtencao: [
                diasParaPrazo < 7 ? 'Prazo urgente' : null,
                complexidade > 2 ? 'Alta complexidade' : null
            ].filter(Boolean),
            recomendacoes: [
                'Revisar documentação do processo',
                'Verificar especialidade requerida',
                'Preparar orçamento detalhado'
            ]
        };
    }
}

module.exports = new IAService();
