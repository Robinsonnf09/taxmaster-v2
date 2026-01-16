const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware básico
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname)));
app.use('/public', express.static(path.join(__dirname, 'public')));
app.use('/pages', express.static(path.join(__dirname, 'pages')));
app.use('/css', express.static(path.join(__dirname, 'css')));
app.use('/js', express.static(path.join(__dirname, 'js')));

// ============================================
// DADOS MOCK - 100 PROCESSOS REALISTAS
// ============================================
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

const statusList = [
    { nome: 'Pendente', cor: '#fef3c7', texto: '#92400e' },
    { nome: 'Em Análise', cor: '#dbeafe', texto: '#1e40af' },
    { nome: 'Aprovado', cor: '#d1fae5', texto: '#065f46' },
    { nome: 'Aguardando Pagamento', cor: '#fef3c7', texto: '#92400e' },
    { nome: 'Pago Parcialmente', cor: '#e0e7ff', texto: '#3730a3' },
    { nome: 'Quitado', cor: '#d1fae5', texto: '#065f46' }
];

const processosMock = [];

// Gerar 100 processos
for (let i = 0; i < 100; i++) {
    const tribunal = tribunais[Math.floor(Math.random() * tribunais.length)];
    const ano = 2020 + Math.floor(Math.random() * 5);
    const sequencial = (1000000 + i).toString().padStart(7, '0');
    const numeroProcesso = `${sequencial}-${Math.floor(Math.random() * 100).toString().padStart(2, '0')}.${ano}.${tribunal.codigo}.${Math.floor(Math.random() * 9999).toString().padStart(4, '0')}`;
    const valorBase = 30000 + Math.random() * 500000;
    const valor = Math.round(valorBase * 100) / 100;
    const dataBase = new Date(ano, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1);
    const statusItem = statusList[Math.floor(Math.random() * statusList.length)];
    
    processosMock.push({
        id: i + 1,
        numero: numeroProcesso,
        tribunal: tribunal.sigla,
        tribunalNome: tribunal.nome,
        credor: credores[Math.floor(Math.random() * credores.length)],
        cpfOculto: `***.***.${Math.floor(Math.random() * 900 + 100)}-**`,
        valor: valor,
        valorAtualizado: valor * (1 + (Math.random() * 0.3)),
        status: statusItem.nome,
        statusCor: statusItem.cor,
        statusTexto: statusItem.texto,
        dataDistribuicao: dataBase.toISOString().split('T')[0],
        natureza: Math.random() > 0.5 ? 'Alimentar' : 'Comum'
    });
}

console.log(`✅ ${processosMock.length} processos carregados com sucesso!`);

// ============================================
// ROTAS
// ============================================

// Rota principal
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Rota de processos
app.get('/processos', (req, res) => {
    const processosFile = path.join(__dirname, 'pages', 'processos.html');
    res.sendFile(processosFile, (err) => {
        if (err) {
            console.error('Erro ao carregar processos.html:', err);
            res.sendFile(path.join(__dirname, 'index.html'));
        }
    });
});

// API - Listar processos com filtros
app.get('/api/processos', (req, res) => {
    try {
        let resultado = [...processosMock];
        
        if (req.query.tribunal) {
            resultado = resultado.filter(p => p.tribunal === req.query.tribunal);
        }
        
        if (req.query.status) {
            resultado = resultado.filter(p => p.status === req.query.status);
        }
        
        if (req.query.busca) {
            const termo = req.query.busca.toLowerCase();
            resultado = resultado.filter(p => 
                p.numero.toLowerCase().includes(termo) ||
                p.credor.toLowerCase().includes(termo) ||
                p.tribunal.toLowerCase().includes(termo)
            );
        }
        
        res.json(resultado);
    } catch (error) {
        console.error('Erro na API /api/processos:', error);
        res.status(500).json({ error: 'Erro ao buscar processos' });
    }
});

// API - Estatísticas
app.get('/api/estatisticas', (req, res) => {
    try {
        const total = processosMock.length;
        const valorTotal = processosMock.reduce((sum, p) => sum + p.valor, 0);
        
        res.json({ 
            total: total, 
            valorTotal: valorTotal 
        });
    } catch (error) {
        console.error('Erro na API /api/estatisticas:', error);
        res.status(500).json({ error: 'Erro ao obter estatísticas' });
    }
});

// Health check
app.get('/health', (req, res) => {
    res.json({ 
        status: 'OK', 
        timestamp: new Date().toISOString(),
        processos: processosMock.length,
        ambiente: process.env.NODE_ENV || 'development'
    });
});

// Tratamento 404
app.use((req, res) => {
    res.status(404).sendFile(path.join(__dirname, 'index.html'));
});

// Tratamento de erros
app.use((err, req, res, next) => {
    console.error('Erro:', err);
    res.status(500).json({ error: 'Erro interno do servidor' });
});

// Iniciar servidor
app.listen(PORT, '0.0.0.0', () => {
    console.log(`
╔════════════════════════════════════════╗
║     TAX MASTER v2.0 - SERVIDOR ATIVO  ║
╚════════════════════════════════════════╝

🚀 Servidor rodando em: http://0.0.0.0:${PORT}
📅 Data/Hora: ${new Date().toLocaleString('pt-BR')}
🌐 Ambiente: ${process.env.NODE_ENV || 'development'}

✅ Rotas disponíveis:
   • GET  /
   • GET  /processos
   • GET  /api/processos
   • GET  /api/estatisticas
   • GET  /health

📊 Dados: ${processosMock.length} processos realistas carregados!

✅ Pronto para receber requisições!
    `);
});

module.exports = app;
