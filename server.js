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


// ============================================
// SERVIÇO MOCK DE PROCESSOS
// ============================================
const processosMockService = require('./public/js/api/processos-mock-service.js');

// API Mock - Processos (atualizada com dados realistas)
app.get('/api/processos', (req, res) => {
  const filtros = {
    tribunal: req.query.tribunal,
    status: req.query.status,
    busca: req.query.busca
  };
  
  const processos = processosMockService.buscarTodos(filtros);
  res.json(processos);
});

// API Mock - Processo específico
app.get('/api/processos/:numero', (req, res) => {
  const processo = processosMockService.buscarPorNumero(req.params.numero);
  
  if (processo) {
    res.json(processo);
  } else {
    res.status(404).json({ error: 'Processo não encontrado' });
  }
});

// API Mock - Estatísticas
app.get('/api/processos/estatisticas', (req, res) => {
  const stats = processosMockService.getEstatisticas();
  res.json(stats);
});
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


// ============================================
// PROXY PARA API DATAJUD (evita CORS)
// ============================================
app.get('/api/datajud/*', async (req, res) => {
  const path = req.params[0];
  const apiUrl = `https://api-publica.datajud.cnj.jus.br/api_publica/${path}`;
  
  try {
    const fetch = (await import('node-fetch')).default;
    const response = await fetch(apiUrl, {
      headers: {
        'Authorization': 'APIKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==',
        'Content-Type': 'application/json'
      }
    });
    
    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error('Erro no proxy DataJud:', error);
    res.status(500).json({ error: 'Erro ao consultar API DataJud' });
  }
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


