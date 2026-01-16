// ============================================
// SERVIÇO DE PROCESSOS MOCK (SUPER REALISTA)
// ============================================

class ProcessosMockService {
    constructor() {
        this.processos = this.gerarProcessosRealistas();
    }
    
    gerarProcessosRealistas() {
        const tribunais = [
            { sigla: 'TJ-BA', codigo: '8.05', nome: 'Tribunal de Justiça da Bahia' },
            { sigla: 'TJ-SP', codigo: '8.26', nome: 'Tribunal de Justiça de São Paulo' },
            { sigla: 'TJ-RJ', codigo: '8.19', nome: 'Tribunal de Justiça do Rio de Janeiro' },
            { sigla: 'TJ-MG', codigo: '8.13', nome: 'Tribunal de Justiça de Minas Gerais' },
            { sigla: 'TJ-RS', codigo: '8.21', nome: 'Tribunal de Justiça do Rio Grande do Sul' }
        ];
        
        const credores = [
            'João Silva Santos', 'Maria Oliveira Costa', 'José Roberto Lima',
            'Ana Paula Ferreira', 'Carlos Eduardo Souza', 'Juliana Santos Almeida',
            'Pedro Henrique Rocha', 'Fernanda Costa Dias', 'Ricardo Alves Pereira',
            'Camila Rodrigues Silva', 'Lucas Martins Oliveira', 'Beatriz Lima Santos'
        ];
        
        const classes = [
            'Precatório - RPV',
            'Requisição de Pequeno Valor',
            'Execução contra a Fazenda Pública',
            'Cumprimento de Sentença',
            'Precatório Alimentar',
            'Precatório Comum'
        ];
        
        const assuntos = [
            'Salários e Vantagens',
            'INSS - Benefícios em Espécie',
            'Responsabilidade Civil - Indenização',
            'Servidor Público - Adicional',
            'Gratificação de Função',
            'Hora Extra e Adicional Noturno'
        ];
        
        const status = [
            { nome: 'Pendente', cor: '#fef3c7', texto: '#92400e' },
            { nome: 'Em Análise', cor: '#dbeafe', texto: '#1e40af' },
            { nome: 'Aprovado', cor: '#d1fae5', texto: '#065f46' },
            { nome: 'Aguardando Pagamento', cor: '#fef3c7', texto: '#92400e' },
            { nome: 'Pago Parcialmente', cor: '#e0e7ff', texto: '#3730a3' },
            { nome: 'Quitado', cor: '#d1fae5', texto: '#065f46' }
        ];
        
        const processos = [];
        
        // Gerar 100 processos realistas
        for (let i = 0; i < 100; i++) {
            const tribunal = tribunais[Math.floor(Math.random() * tribunais.length)];
            const ano = 2020 + Math.floor(Math.random() * 5);
            const sequencial = (1000000 + i).toString().padStart(7, '0');
            const numeroProcesso = `${sequencial}-${Math.floor(Math.random() * 100).toString().padStart(2, '0')}.${ano}.${tribunal.codigo}.${Math.floor(Math.random() * 9999).toString().padStart(4, '0')}`;
            
            const valorBase = 30000 + Math.random() * 500000;
            const valor = Math.round(valorBase * 100) / 100;
            
            const dataBase = new Date(ano, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1);
            const diasDecorridos = Math.floor(Math.random() * 1000);
            const ultimaMovimentacao = new Date(dataBase.getTime() + diasDecorridos * 24 * 60 * 60 * 1000);
            
            const statusItem = status[Math.floor(Math.random() * status.length)];
            
            processos.push({
                id: i + 1,
                numero: numeroProcesso,
                tribunal: tribunal.sigla,
                tribunalNome: tribunal.nome,
                credor: credores[Math.floor(Math.random() * credores.length)],
                cpfOculto: `***.***.${Math.floor(Math.random() * 900 + 100)}-**`,
                valor: valor,
                valorAtualizado: valor * (1 + (Math.random() * 0.3)),
                classe: classes[Math.floor(Math.random() * classes.length)],
                assunto: assuntos[Math.floor(Math.random() * assuntos.length)],
                status: statusItem.nome,
                statusCor: statusItem.cor,
                statusTexto: statusItem.texto,
                dataDistribuicao: dataBase.toISOString().split('T')[0],
                ultimaMovimentacao: ultimaMovimentacao.toISOString().split('T')[0],
                natureza: Math.random() > 0.5 ? 'Alimentar' : 'Comum',
                prioridade: Math.random() > 0.7 ? 'Idoso' : Math.random() > 0.5 ? 'Doente Grave' : 'Normal',
                movimentacoes: this.gerarMovimentacoes(dataBase, ultimaMovimentacao)
            });
        }
        
        return processos;
    }
    
    gerarMovimentacoes(dataInicial, dataFinal) {
        const movimentacoes = [];
        const tiposMovimentacao = [
            'Processo distribuído',
            'Juntada de documento',
            'Despacho proferido',
            'Sentença publicada',
            'Recurso interposto',
            'Trânsito em julgado',
            'Expedição de precatório',
            'Cálculo homologado',
            'Aguardando pagamento'
        ];
        
        const qtdMovimentacoes = 3 + Math.floor(Math.random() * 7);
        const intervalo = (dataFinal - dataInicial) / qtdMovimentacoes;
        
        for (let i = 0; i < qtdMovimentacoes; i++) {
            const data = new Date(dataInicial.getTime() + intervalo * i);
            movimentacoes.push({
                data: data.toISOString().split('T')[0],
                descricao: tiposMovimentacao[Math.min(i, tiposMovimentacao.length - 1)]
            });
        }
        
        return movimentacoes;
    }
    
    buscarPorNumero(numero) {
        return this.processos.find(p => p.numero === numero);
    }
    
    buscarPorTribunal(tribunal) {
        return this.processos.filter(p => p.tribunal === tribunal);
    }
    
    buscarPorStatus(status) {
        return this.processos.filter(p => p.status === status);
    }
    
    buscarTodos(filtros = {}) {
        let resultado = [...this.processos];
        
        if (filtros.tribunal) {
            resultado = resultado.filter(p => p.tribunal === filtros.tribunal);
        }
        
        if (filtros.status) {
            resultado = resultado.filter(p => p.status === filtros.status);
        }
        
        if (filtros.busca) {
            const termo = filtros.busca.toLowerCase();
            resultado = resultado.filter(p => 
                p.numero.toLowerCase().includes(termo) ||
                p.credor.toLowerCase().includes(termo) ||
                p.tribunal.toLowerCase().includes(termo)
            );
        }
        
        return resultado;
    }
    
    getEstatisticas() {
        return {
            total: this.processos.length,
            valorTotal: this.processos.reduce((sum, p) => sum + p.valor, 0),
            porTribunal: this.agruparPorTribunal(),
            porStatus: this.agruparPorStatus()
        };
    }
    
    agruparPorTribunal() {
        const grupos = {};
        this.processos.forEach(p => {
            if (!grupos[p.tribunal]) {
                grupos[p.tribunal] = { quantidade: 0, valor: 0 };
            }
            grupos[p.tribunal].quantidade++;
            grupos[p.tribunal].valor += p.valor;
        });
        return grupos;
    }
    
    agruparPorStatus() {
        const grupos = {};
        this.processos.forEach(p => {
            if (!grupos[p.status]) {
                grupos[p.status] = { quantidade: 0, valor: 0 };
            }
            grupos[p.status].quantidade++;
            grupos[p.status].valor += p.valor;
        });
        return grupos;
    }
}

// Instância global
const processosMockService = new ProcessosMockService();

// Exportar
if (typeof module !== 'undefined' && module.exports) {
    module.exports = processosMockService;
}
