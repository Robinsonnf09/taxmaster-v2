// server.js - Versão Simples e Funcional
const express = require('express');
const session = require('express-session');
const path = require('path');
const { buscarProcessosESAJ } = require('./esajScraper');

const app = express();
const PORT = process.env.PORT || 8080;

// Middleware básico
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

app.use(session({
  secret: 'tax-master-secret-2024',
  resave: false,
  saveUninitialized: false,
  cookie: { maxAge: 24 * 60 * 60 * 1000 }
}));

// Cache
let processosCache = [];

// Middleware de autenticação simples
function requireAuth(req, res, next) {
  if (req.session && req.session.usuario) {
    return next();
  }
  res.redirect('/');
}

// ============================================
// ROTAS DE AUTENTICAÇÃO
// ============================================

app.post('/api/auth/login', (req, res) => {
  try {
    const { usuario, senha } = req.body;
    
    if (usuario === 'admin' && senha === 'admin123') {
      req.session.usuario = { nome: usuario, role: 'admin' };
      res.json({ success: true, redirect: '/processos' });
    } else {
      res.status(401).json({ success: false, message: 'Credenciais inválidas' });
    }
  } catch (error) {
    console.error('Erro no login:', error);
    res.status(500).json({ success: false, message: 'Erro interno' });
  }
});

app.post('/api/auth/logout', (req, res) => {
  req.session.destroy();
  res.json({ success: true });
});

// ============================================
// ROTA DE BUSCA
// ============================================

app.get('/api/buscar-tjsp', requireAuth, async (req, res) => {
  try {
    const params = {
      valorMin: parseFloat(req.query.valorMin) || undefined,
      valorMax: parseFloat(req.query.valorMax) || undefined,
      natureza: req.query.natureza || 'Todas',
      anoLoa: req.query.anoLoa || 'Todos',
      status: req.query.status || 'Todos',
      quantidade: parseInt(req.query.quantidade) || 30
    };

    console.log(`\n📥 Nova busca:`, params);

    const resultado = await buscarProcessosESAJ(params);
    processosCache = resultado.processos;

    res.json(resultado);
    
  } catch (error) {
    console.error(`❌ Erro na busca:`, error);
    res.status(500).json({ 
      processos: [], 
      stats: { erro: error.message } 
    });
  }
});

// ============================================
// ROTA DE DASHBOARD STATS
// ============================================

app.get('/api/dashboard-stats', requireAuth, (req, res) => {
  try {
    if (processosCache.length === 0) {
      return res.json({
        totalProcessos: 0,
        valorTotal: 0,
        pendentes: 0,
        pagos: 0,
        porNatureza: {},
        porLOA: {},
        valorPorNatureza: {},
        porStatus: {}
      });
    }

    const stats = {
      totalProcessos: processosCache.length,
      valorTotal: processosCache.reduce((sum, p) => sum + (p.valor || 0), 0),
      pendentes: processosCache.filter(p => p.status === 'Pendente').length,
      pagos: processosCache.filter(p => p.status === 'Pago').length,
      porNatureza: {},
      porLOA: {},
      valorPorNatureza: {},
      porStatus: {}
    };

    processosCache.forEach(p => {
      stats.porNatureza[p.natureza] = (stats.porNatureza[p.natureza] || 0) + 1;
      stats.valorPorNatureza[p.natureza] = (stats.valorPorNatureza[p.natureza] || 0) + (p.valor || 0);
      stats.porLOA[p.anoLOA] = (stats.porLOA[p.anoLOA] || 0) + 1;
      stats.porStatus[p.status] = (stats.porStatus[p.status] || 0) + 1;
    });

    res.json(stats);
  } catch (error) {
    console.error('Erro ao calcular stats:', error);
    res.status(500).json({ error: error.message });
  }
});

// ============================================
// ROTAS DE PÁGINAS
// ============================================

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/processos', requireAuth, (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'processos.html'));
});

app.get('/dashboard', requireAuth, (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});

// ============================================
// HEALTH CHECK
// ============================================

app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    cache: processosCache.length
  });
});

// ============================================
// ERROR HANDLER
// ============================================

app.use((err, req, res, next) => {
  console.error('Erro:', err);
  res.status(500).json({
    success: false,
    message: 'Erro interno do servidor'
  });
});

// ============================================
// INICIAR SERVIDOR
// ============================================

app.listen(PORT, () => {
  console.log('\n✅ Tax Master V3 - API CNJ DataJud');
  console.log('🔍 Fonte: API CNJ DataJud (Oficial)');
  console.log('⚠️ Delay de 2s entre requisições');
  console.log(`🚀 Servidor na porta ${PORT}`);
  console.log('\n✅ Sistema pronto com API CNJ DataJud!');
});
