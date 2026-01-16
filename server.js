const express = require('express');
const compression = require('compression');
const helmet = require('helmet');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware de segurança
app.use(helmet({
  contentSecurityPolicy: false
}));

// CORS
app.use(cors());

// Compressão Gzip
app.use(compression());

// Parse JSON
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Servir arquivos estáticos
app.use(express.static(path.join(__dirname)));
app.use('/public', express.static(path.join(__dirname, 'public')));
app.use('/pages', express.static(path.join(__dirname, 'pages')));

// Rota principal
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Rota de busca de processos
app.get('/busca-processos', (req, res) => {
  res.sendFile(path.join(__dirname, 'pages', 'busca-processos.html'));
});

// Rota de solicitação de token CNJ
app.get('/solicitar-token-cnj', (req, res) => {
  res.sendFile(path.join(__dirname, 'pages', 'solicitar-token-cnj.html'));
});

// API Mock - Processos
app.get('/api/processos', (req, res) => {
  const processosMock = [
    {
      id: 1,
      numero: '0000000-00.2024.8.05.0001',
      tribunal: 'TJ-BA',
      credor: 'JOÃO SILVA',
      valor: 85000.00,
      status: 'Em Análise',
      dataDistribuicao: '2024-03-15'
    },
    {
      id: 2,
      numero: '0000000-01.2024.8.05.0001',
      tribunal: 'TJ-BA',
      credor: 'MARIA SANTOS',
      valor: 120000.00,
      status: 'Pendente',
      dataDistribuicao: '2024-02-20'
    }
  ];
  res.json(processosMock);
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Tratamento 404
app.use((req, res) => {
  res.status(404).sendFile(path.join(__dirname, 'index.html'));
});

// Iniciar servidor
app.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════╗
║     TAX MASTER v2.0 - SERVIDOR ATIVO  ║
╚════════════════════════════════════════╝

🚀 Servidor rodando em: http://localhost:${PORT}
📅 Data/Hora: ${new Date().toLocaleString('pt-BR')}
🌐 Ambiente: ${process.env.NODE_ENV || 'development'}

✅ Pronto para receber requisições!
  `);
});

module.exports = app;
