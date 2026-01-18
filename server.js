// server.js - Tax Master V3 Enterprise Edition
require('dotenv').config();
const express = require('express');
const session = require('express-session');
const RedisStore = require('connect-redis').default;
const helmet = require('helmet');
const cors = require('cors');
const compression = require('compression');
const morgan = require('morgan');
const path = require('path');

// Services
const logger = require('./config/logger');
const { connectRedis, getRedisClient } = require('./config/redis');
const { buscarProcessosESAJ } = require('./esajScraper');
const scraperService = require('./services/scraperService');
const analyticsService = require('./services/analyticsService');
const exportService = require('./services/exportService');
const notificationService = require('./services/notificationService');
const favoritosService = require('./services/favoritosService');
const queueService = require('./services/queueService');
const CacheManager = require('./middleware/cache');

// Middleware
const { apiLimiter, authLimiter, scrapingLimiter } = require('./middleware/rateLimit');
const { generateToken, authMiddleware, optionalAuth } = require('./middleware/auth');
const { validate } = require('./middleware/validator');

const app = express();
const PORT = process.env.PORT || 8080;

// ============================================
// CONFIGURAÇÃO GLOBAL
// ============================================

app.use(helmet({
  contentSecurityPolicy: false,
  crossOriginEmbedderPolicy: false
}));
app.use(cors());
app.use(compression());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(express.static('public'));
app.use(morgan('combined', { stream: { write: msg => logger.info(msg.trim()) } }));

// Cache Manager
let cacheManager;

// Dados em memória
let processosCache = [];
let historicoBuscas = [];

// ============================================
// INICIALIZAÇÃO
// ============================================

async function initialize() {
  try {
    // Conectar Redis
    const redisClient = await connectRedis();
    
    // Configurar Session Store
    if (redisClient) {
      app.use(session({
        store: new RedisStore({ client: redisClient }),
        secret: process.env.JWT_SECRET || 'tax-master-secret-2024',
        resave: false,
        saveUninitialized: false,
        cookie: {
          maxAge: 24 * 60 * 60 * 1000,
          httpOnly: true,
          secure: process.env.NODE_ENV === 'production'
        }
      }));
      logger.info('✅ Redis Session Store configurado');
      
      cacheManager = new CacheManager(redisClient);
    } else {
      app.use(session({
        secret: process.env.JWT_SECRET || 'tax-master-secret-2024',
        resave: false,
        saveUninitialized: false,
        cookie: { maxAge: 24 * 60 * 60 * 1000 }
      }));
      logger.warn('⚠️ Usando MemoryStore (não recomendado para produção)');
      
      cacheManager = new CacheManager(null);
    }

    // Configurar filas
    queueService.processQueue('scraping', async (job) => {
      logger.info(`⚙️ Processando job de scraping: ${job.id}`);
      const { filtros, quantidade } = job.data;
      
      const processos = await scraperService.scrapeDEPRE(filtros, quantidade);
      
      // Enriquecer alguns processos
      const enriquecidos = [];
      for (let i = 0; i < Math.min(processos.length, 5); i++) {
        const enriquecido = await scraperService.enriquecerComESAJ(processos[i]);
        enriquecidos.push(enriquecido);
        await scraperService.delay(2000);
      }
      
      return { processos, enriquecidos: enriquecidos.length };
    });

    logger.info('✅ Inicialização completa');
  } catch (error) {
    logger.error(`❌ Erro na inicialização: ${error.message}`);
  }
}

// ============================================
// ROTAS DE AUTENTICAÇÃO
// ============================================

app.post('/api/auth/login', authLimiter, validate('login'), (req, res) => {
  try {
    const { usuario, senha } = req.validatedData;
    
    // Validação simples (em produção, usar bcrypt e DB)
    if (usuario === 'admin' && senha === 'admin123') {
      const payload = {
        id: 1,
        nome: usuario,
        role: 'admin',
        email: 'admin@taxmaster.com'
      };
      
      const token = generateToken(payload);
      req.session.usuario = payload;
      
      logger.info(`✅ Login bem-sucedido: ${usuario}`);
      
      res.json({
        success: true,
        redirect: '/processos',
        token,
        user: payload
      });
    } else {
      logger.warn(`⚠️ Tentativa de login falhou: ${usuario}`);
      res.status(401).json({
        success: false,
        message: 'Credenciais inválidas'
      });
    }
  } catch (error) {
    logger.error(`Erro no login: ${error.message}`);
    res.status(500).json({ success: false, message: 'Erro interno' });
  }
});

app.post('/api/auth/logout', (req, res) => {
  req.session.destroy();
  res.json({ success: true });
});

// ============================================
// ROTAS DE BUSCA
// ============================================

app.get('/api/buscar-tjsp', 
  authMiddleware,
  apiLimiter,
  validate('buscaProcessos'),
  async (req, res) => {
    try {
      const params = {
        valorMin: parseFloat(req.validatedData.valorMin) || undefined,
        valorMax: parseFloat(req.validatedData.valorMax) || undefined,
        natureza: req.validatedData.natureza || 'Todas',
        anoLoa: req.validatedData.anoLoa || 'Todos',
        status: req.validatedData.status || 'Todos',
        quantidade: parseInt(req.validatedData.quantidade) || 30
      };

      logger.info(`📥 Nova busca: ${JSON.stringify(params)}`);

      const resultado = await buscarProcessosESAJ(params);
      processosCache = resultado.processos;
      
      historicoBuscas.push({
        data: new Date(),
        filtros: params,
        resultados: resultado.processos.length,
        usuario: req.user.nome
      });

      // Calcular estatísticas
      const stats = analyticsService.calcularEstatisticas(resultado.processos);

      res.json({
        ...resultado,
        analytics: stats
      });
      
    } catch (error) {
      logger.error(`❌ Erro na busca: ${error.message}`);
      res.status(500).json({
        processos: [],
        stats: { erro: error.message }
      });
    }
});

// ============================================
// ROTAS DE WEB SCRAPING
// ============================================

app.get('/api/scraping/depre',
  authMiddleware,
  scrapingLimiter,
  async (req, res) => {
    try {
      const filtros = {
        natureza: req.query.natureza,
        anoLoa: req.query.anoLoa
      };
      const quantidade = parseInt(req.query.quantidade) || 30;

      logger.info('🌐 Iniciando scraping DEPRE via API');

      const processos = await scraperService.scrapeDEPRE(filtros, quantidade);

      res.json({
        success: true,
        processos,
        total: processos.length,
        fonte: 'DEPRE Web Scraping'
      });
    } catch (error) {
      logger.error(`Erro no scraping: ${error.message}`);
      res.status(500).json({ success: false, error: error.message });
    }
});

app.post('/api/scraping/queue',
  authMiddleware,
  async (req, res) => {
    try {
      const { filtros, quantidade } = req.body;

      const job = await queueService.addJob('scraping', { filtros, quantidade });

      res.json({
        success: true,
        jobId: job.id,
        message: 'Scraping agendado com sucesso'
      });
    } catch (error) {
      logger.error(`Erro ao agendar scraping: ${error.message}`);
      res.status(500).json({ success: false, error: error.message });
    }
});

// ============================================
// ROTAS DE ANALYTICS
// ============================================

app.get('/api/dashboard-stats',
  authMiddleware,
  cacheManager.cacheMiddleware(req => `stats:${req.user.id}`, 300),
  (req, res) => {
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

      const stats = analyticsService.calcularEstatisticas(processosCache);
      res.json(stats);
    } catch (error) {
      logger.error(`Erro ao calcular stats: ${error.message}`);
      res.status(500).json({ error: error.message });
    }
});

app.get('/api/relatorio/executivo',
  authMiddleware,
  async (req, res) => {
    try {
      const stats = analyticsService.calcularEstatisticas(processosCache);
      const relatorio = analyticsService.gerarRelatorioExecutivo(processosCache, stats);

      res.json({
        success: true,
        relatorio
      });
    } catch (error) {
      logger.error(`Erro ao gerar relatório: ${error.message}`);
      res.status(500).json({ success: false, error: error.message });
    }
});

// ============================================
// ROTAS DE EXPORTAÇÃO
// ============================================

app.get('/api/exportar/excel',
  authMiddleware,
  async (req, res) => {
    try {
      const stats = analyticsService.calcularEstatisticas(processosCache);
      const workbook = await exportService.exportarExcel(processosCache, stats);

      res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
      res.setHeader('Content-Disposition', `attachment; filename=processos_${new Date().toISOString().split('T')[0]}.xlsx`);

      await workbook.xlsx.write(res);
      res.end();

      logger.info(`📥 Excel exportado por ${req.user.nome}`);
    } catch (error) {
      logger.error(`Erro ao exportar Excel: ${error.message}`);
      res.status(500).json({ error: error.message });
    }
});

app.get('/api/exportar/csv',
  authMiddleware,
  async (req, res) => {
    try {
      const csv = await exportService.exportarCSV(processosCache);

      res.setHeader('Content-Type', 'text/csv; charset=utf-8');
      res.setHeader('Content-Disposition', `attachment; filename=processos_${new Date().toISOString().split('T')[0]}.csv`);

      res.send('\uFEFF' + csv);

      logger.info(`📥 CSV exportado por ${req.user.nome}`);
    } catch (error) {
      logger.error(`Erro ao exportar CSV: ${error.message}`);
      res.status(500).json({ error: error.message });
    }
});

app.get('/api/exportar/pdf',
  authMiddleware,
  async (req, res) => {
    try {
      const stats = analyticsService.calcularEstatisticas(processosCache);
      const pdfBuffer = await exportService.gerarPDFRelatorio(processosCache, stats);

      res.setHeader('Content-Type', 'application/pdf');
      res.setHeader('Content-Disposition', `attachment; filename=relatorio_${new Date().toISOString().split('T')[0]}.pdf`);

      res.send(pdfBuffer);

      logger.info(`📄 PDF exportado por ${req.user.nome}`);
    } catch (error) {
      logger.error(`Erro ao exportar PDF: ${error.message}`);
      res.status(500).json({ error: error.message });
    }
});

// ============================================
// ROTAS DE FAVORITOS
// ============================================

app.post('/api/favoritos',
  authMiddleware,
  async (req, res) => {
    try {
      const { numeroProcesso } = req.body;
      const sucesso = favoritosService.adicionarFavorito(req.user.id, numeroProcesso);

      res.json({ success: sucesso });
    } catch (error) {
      logger.error(`Erro ao adicionar favorito: ${error.message}`);
      res.status(500).json({ success: false, error: error.message });
    }
});

app.delete('/api/favoritos/:numero',
  authMiddleware,
  async (req, res) => {
    try {
      const sucesso = favoritosService.removerFavorito(req.user.id, req.params.numero);

      res.json({ success: sucesso });
    } catch (error) {
      logger.error(`Erro ao remover favorito: ${error.message}`);
      res.status(500).json({ success: false, error: error.message });
    }
});

app.get('/api/favoritos',
  authMiddleware,
  async (req, res) => {
    try {
      const favoritos = favoritosService.listarFavoritos(req.user.id);

      res.json({ success: true, favoritos });
    } catch (error) {
      logger.error(`Erro ao listar favoritos: ${error.message}`);
      res.status(500).json({ success: false, error: error.message });
    }
});

// ============================================
// ROTAS DE ANOTAÇÕES
// ============================================

app.post('/api/anotacoes',
  authMiddleware,
  async (req, res) => {
    try {
      const { numeroProcesso, texto } = req.body;
      const sucesso = favoritosService.adicionarAnotacao(req.user.id, numeroProcesso, texto);

      res.json({ success: sucesso });
    } catch (error) {
      logger.error(`Erro ao adicionar anotação: ${error.message}`);
      res.status(500).json({ success: false, error: error.message });
    }
});

app.get('/api/anotacoes',
  authMiddleware,
  async (req, res) => {
    try {
      const anotacoes = favoritosService.listarAnotacoes(req.user.id);

      res.json({ success: true, anotacoes });
    } catch (error) {
      logger.error(`Erro ao listar anotações: ${error.message}`);
      res.status(500).json({ success: false, error: error.message });
    }
});

// ============================================
// ROTAS DE PÁGINAS
// ============================================

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/processos', (req, res) => {
  if (!req.session || !req.session.usuario) {
    return res.redirect('/');
  }
  res.sendFile(path.join(__dirname, 'public', 'processos.html'));
});

app.get('/dashboard', (req, res) => {
  if (!req.session || !req.session.usuario) {
    return res.redirect('/');
  }
  res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});

// ============================================
// HEALTH CHECK
// ============================================

app.get('/health', (req, res) => {
  const redisClient = getRedisClient();
  
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    redis: redisClient && redisClient.isOpen ? 'connected' : 'disconnected',
    cache: processosCache.length,
    uptime: process.uptime()
  });
});

// ============================================
// ERROR HANDLER
// ============================================

app.use((err, req, res, next) => {
  logger.error(`Erro não tratado: ${err.message}`, { stack: err.stack });
  
  res.status(500).json({
    success: false,
    message: 'Erro interno do servidor',
    error: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// ============================================
// INICIAR SERVIDOR
// ============================================

initialize().then(() => {
  app.listen(PORT, () => {
    logger.info('╔═══════════════════════════════════════════════════════╗');
    logger.info('║                                                       ║');
    logger.info('║  🚀 TAX MASTER V3 - ENTERPRISE EDITION               ║');
    logger.info('║                                                       ║');
    logger.info('╚═══════════════════════════════════════════════════════╝');
    logger.info('');
    logger.info('✅ Tax Master V3 - API CNJ DataJud');
    logger.info('🔍 Fonte: API CNJ DataJud (Oficial)');
    logger.info('⚠️ Delay de 2s entre requisições');
    logger.info(`🚀 Servidor na porta ${PORT}`);
    logger.info('');
    logger.info('✅ Sistema pronto com API CNJ DataJud!');
  });
}).catch(error => {
  logger.error(`❌ Falha ao iniciar servidor: ${error.message}`);
  process.exit(1);
});
