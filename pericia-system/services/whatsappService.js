const twilio = require('twilio');

class WhatsAppService {
    constructor() {
        this.client = twilio(
            process.env.TWILIO_ACCOUNT_SID,
            process.env.TWILIO_AUTH_TOKEN
        );
    }
    
    async enviarMensagem(numero, oportunidade) {
        try {
            const mensagem = `
🎯 *Nova Oportunidade Detectada!*

*Tribunal:* ${oportunidade.tribunal}
*Processo:* ${oportunidade.processo}
*Especialidade:* ${oportunidade.especialidade}
*Honorários:* R$ ${oportunidade.honorariosEstimados.toLocaleString('pt-BR')}
*Score:* ${oportunidade.score}/100
*Prazo:* ${new Date(oportunidade.prazo).toLocaleDateString('pt-BR')}

Acesse o sistema para mais detalhes!
            `.trim();
            
            await this.client.messages.create({
                body: mensagem,
                from: `whatsapp:${process.env.TWILIO_WHATSAPP_NUMBER}`,
                to: `whatsapp:${numero}`
            });
            
            console.log(`✓ WhatsApp enviado para ${numero}`);
            return true;
        } catch (error) {
            console.error('Erro ao enviar WhatsApp:', error);
            return false;
        }
    }
}

module.exports = new WhatsAppService();
