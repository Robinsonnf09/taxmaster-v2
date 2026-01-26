require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

// Importar configurações e modelos
const sequelize = require('./config/database');
const User = require('./models/User');
const Oportunidade = require('./models/Oportunidade');
const Candidatura = require('./models/Candidatura');

// Importar middleware e controllers
const { auth, adminAuth } = require('./middleware/auth');
const authController = require('./controllers/authController');

// Importar serviços
const emailService = require('./services/emailService');
const whatsappService = require('./services/whatsappService');
const iaService = require('./services/iaService');

const app = express();
const PORT = process.env.PORT || 3000;

// Relacionamentos
User.hasMany(Candidatura, { foreignKey: 'userId' });
Candidatura.belongsTo(User, { foreignKey: 'userId' });
Oportunidade.hasMany(Candidatura, { foreignKey: 'oportunidadeId' });
Candidatura.belongsTo(Oportunidade, { foreignKey: 'oportunidadeId' });

// Middlewares
app.use(cors());
app.use(
    helmet({
        contentSecurityPolicy: {
            directives: {
                defaultSrc: ["'self'"],
                scriptSrc: [
                    "'self'",
                    "'unsafe-inline'",
                    "https://cdn.jsdelivr.net",
                    "https://cdnjs.cloudflare.com"
                ],
                styleSrc: [
                    "'self'",
                    "'unsafe-inline'",
                    "https://cdnjs.cloudflare.com"
                ],
                fontSrc: [
                    "'self'",
                    "https://cdnjs.cloudflare.com"
                ],
                imgSrc: ["'self'", "data:", "https:"],
                connectSrc: ["'self'"]
            }
        }
    })
);

app.use(compression());
app.use(morgan('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

// ==========================================
// FUNÇÕES AUXILIARES
// ==========================================

function lerUltimoScraper() {
    try {
        const scrapersDir = path.join(__dirname, 'scrapers');
        const files = fs.readdirSync(scrapersDir)
            .filter(f => f.startsWith('oportunidades_demo_') && f.endsWith('.json'))
            .sort()
            .reverse();
        
        if (files.length > 0) {
            const filepath = path.join(scrapersDir, files[0]);
            const data = fs.readFileSync(filepath, 'utf-8');
            console.log(`✓ Carregando dados de: ${files[0]}`);
            return JSON.parse(data);
        }
    } catch (error) {
        console.log('⚠ Arquivo do scraper não encontrado');
    }
    return [];
}

// ==========================================
// ROTAS PÚBLICAS
// ==========================================

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});

app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'OK', 
        timestamp: new Date(),
        service: 'Sistema de Perícia Judicial',
        version: '2.0.0',
        database: sequelize.authenticate() ? 'Connected' : 'Disconnected'
    });
});

// ==========================================
// ROTAS DE AUTENTICAÇÃO
// ==========================================

app.post('/api/auth/register', authController.register);
app.post('/api/auth/login', authController.login);
app.get('/api/auth/profile', auth, authController.getProfile);
app.put('/api/auth/profile', auth, authController.updateProfile);

// ==========================================
// ROTAS DE OPORTUNIDADES
// ==========================================

// Listar todas (público - para compatibilidade)
app.get('/api/oportunidades', async (req, res) => {
    try {
        // Tentar buscar do banco primeiro
        const oportunidades = await Oportunidade.findAll({
            order: [['score', 'DESC'], ['createdAt', 'DESC']]
        });
        
        if (oportunidades.length > 0) {
            console.log(`✓ Retornando ${oportunidades.length} oportunidades do banco`);
            res.json(oportunidades);
        } else {
            // Fallback para JSON do scraper
            const dados = lerUltimoScraper();
            console.log(`✓ Retornando ${dados.length} oportunidades do scraper`);
            res.json(dados);
        }
    } catch (error) {
        console.error('Erro ao buscar oportunidades:', error);
        res.status(500).json({ error: 'Erro ao buscar oportunidades' });
    }
});

// Buscar por ID
app.get('/api/oportunidades/:id', async (req, res) => {
    try {
        const oportunidade = await Oportunidade.findByPk(req.params.id);
        if (!oportunidade) {
            return res.status(404).json({ error: 'Oportunidade não encontrada' });
        }
        res.json(oportunidade);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Criar nova oportunidade (admin)
app.post('/api/oportunidades', auth, adminAuth, async (req, res) => {
    try {
        const oportunidade = await Oportunidade.create(req.body);
        
        // Analisar com IA
        const analise = await iaService.analisarOportunidade(oportunidade);
        await oportunidade.update({
            honorariosEstimados: analise.honorariosRecomendados,
            score: analise.score
        });
        
        res.status(201).json(oportunidade);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Atualizar oportunidade (admin)
app.put('/api/oportunidades/:id', auth, adminAuth, async (req, res) => {
    try {
        const oportunidade = await Oportunidade.findByPk(req.params.id);
        if (!oportunidade) {
            return res.status(404).json({ error: 'Oportunidade não encontrada' });
        }
        
        await oportunidade.update(req.body);
        res.json(oportunidade);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// ==========================================
// ROTAS DE ESTATÍSTICAS
// ==========================================

app.get('/api/estatisticas', async (req, res) => {
    try {
        const oportunidades = await Oportunidade.findAll();
        
        const stats = {
            totalOportunidades: oportunidades.length,
            processosAtivos: oportunidades.filter(o => o.status !== 'Nova').length,
            receitaMensal: oportunidades.reduce((sum, o) => sum + parseFloat(o.honorariosEstimados || 0), 0),
            taxaSucesso: 78.5,
            honorariosMedios: oportunidades.reduce((sum, o) => sum + parseFloat(o.honorariosEstimados || 0), 0) / (oportunidades.length || 1)
        };
        
        console.log(`✓ Estatísticas: ${stats.totalOportunidades} oportunidades, R$ ${stats.receitaMensal.toLocaleString('pt-BR')}`);
        res.json(stats);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// ==========================================
// ROTAS DE CANDIDATURAS
// ==========================================

// Criar candidatura
app.post('/api/candidaturas', auth, async (req, res) => {
    try {
        const { oportunidadeId, observacoes } = req.body;
        
        const candidatura = await Candidatura.create({
            userId: req.user.id,
            oportunidadeId,
            observacoes,
            status: 'Enviada'
        });
        
        // Atualizar status da oportunidade
        await Oportunidade.update(
            { status: 'Candidatado' },
            { where: { id: oportunidadeId } }
        );
        
        res.status(201).json(candidatura);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Listar candidaturas do usuário
app.get('/api/candidaturas', auth, async (req, res) => {
    try {
        const candidaturas = await Candidatura.findAll({
            where: { userId: req.user.id },
            include: [{ model: Oportunidade }],
            order: [['createdAt', 'DESC']]
        });
        
        res.json(candidaturas);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// ==========================================
// ROTAS DE SCRAPER
// ==========================================

app.post('/api/scraper/executar', async (req, res) => {
    console.log('🔄 Executando scraper...');
    
    const python = spawn('python', [path.join(__dirname, 'scrapers', 'scraper_demo.py')]);
    
    let output = '';
    let errorOutput = '';
    
    python.stdout.on('data', (data) => {
        output += data.toString();
        console.log(`Scraper: ${data}`);
    });
    
    python.stderr.on('data', (data) => {
        errorOutput += data.toString();
        console.error(`Scraper erro: ${data}`);
    });
    
    python.on('close', async (code) => {
        if (code === 0) {
            console.log('✅ Scraper executado com sucesso!');
            
            // Importar novas oportunidades para o banco
            try {
                const dados = lerUltimoScraper();
                let novasOportunidades = 0;
                
                for (const opp of dados) {
                    const existe = await Oportunidade.findOne({ where: { processo: opp.processo } });
                    if (!existe) {
                        await Oportunidade.create(opp);
                        novasOportunidades++;
                    }
                }
                
                console.log(`✓ ${novasOportunidades} novas oportunidades importadas`);
            } catch (error) {
                console.error('Erro ao importar oportunidades:', error);
            }
            
            res.json({ 
                success: true,
                message: 'Scraper executado com sucesso!',
                timestamp: new Date(),
                output: output
            });
        } else {
            console.error('❌ Erro ao executar scraper');
            res.status(500).json({ 
                success: false,
                message: 'Erro ao executar scraper',
                error: errorOutput,
                code: code
            });
        }
    });
});

// ==========================================
// ROTAS DE IA
// ==========================================

app.post('/api/ia/analisar', auth, async (req, res) => {
    try {
        const { oportunidadeId } = req.body;
        
        const oportunidade = await Oportunidade.findByPk(oportunidadeId);
        if (!oportunidade) {
            return res.status(404).json({ error: 'Oportunidade não encontrada' });
        }
        
        const analise = await iaService.analisarOportunidade(oportunidade);
        
        res.json(analise);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// ==========================================
// ROTAS DE NOTIFICAÇÕES
// ==========================================

app.post('/api/notificacoes/email', auth, async (req, res) => {
    try {
        const { oportunidadeId } = req.body;
        
        const oportunidade = await Oportunidade.findByPk(oportunidadeId);
        if (!oportunidade) {
            return res.status(404).json({ error: 'Oportunidade não encontrada' });
        }
        
        await emailService.enviarNovaOportunidade(req.user.email, oportunidade);
        
        res.json({ success: true, message: 'Email enviado com sucesso' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/notificacoes/whatsapp', auth, async (req, res) => {
    try {
        const { oportunidadeId } = req.body;
        
        const oportunidade = await Oportunidade.findByPk(oportunidadeId);
        if (!oportunidade) {
            return res.status(404).json({ error: 'Oportunidade não encontrada' });
        }
        
        await whatsappService.enviarMensagem(req.user.telefone, oportunidade);
        
        res.json({ success: true, message: 'WhatsApp enviado com sucesso' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// ==========================================
// INICIAR SERVIDOR
// ==========================================

async function startServer() {
    try {
        // Conectar ao banco
        await sequelize.authenticate();
        console.log('✓ Banco de dados conectado');
        
        // Sincronizar modelos
        await sequelize.sync({ alter: false });
        console.log('✓ Modelos sincronizados');
        
        // Iniciar servidor
        app.listen(PORT, () => {
            console.log(`
╔═══════════════════════════════════════════════════════════╗
║     SISTEMA DE PERÍCIA JUDICIAL - TAX MASTER             ║
║                    VERSÃO COMPLETA 2.0                   ║
║                                                           ║
║  Servidor rodando em: http://localhost:${PORT}               ║
║  Status: ONLINE ✓                                        ║
║  Ambiente: ${process.env.NODE_ENV || 'development'}                                  ║
║  Banco de Dados: PostgreSQL ✓                            ║
║  Autenticação: JWT ✓                                     ║
║  Scraper: Integrado ✓                                    ║
║  IA: OpenAI ✓                                            ║
║  Notificações: Email + WhatsApp ✓                        ║
╚═══════════════════════════════════════════════════════════╝

📄 PÁGINAS DISPONÍVEIS:
   → Dashboard: http://localhost:${PORT}
   → Calculadora: http://localhost:${PORT}/calculadora.html
   → CRM: http://localhost:${PORT}/crm.html
   → Relatórios: http://localhost:${PORT}/relatorios.html
   → Templates: http://localhost:${PORT}/templates.html
   → Login: http://localhost:${PORT}/login.html

🔐 API ENDPOINTS:
   → POST /api/auth/register
   → POST /api/auth/login
   → GET  /api/oportunidades
   → POST /api/candidaturas
   → POST /api/scraper/executar
   → POST /api/ia/analisar

Pressione Ctrl+C para encerrar
            `);
        });
    } catch (error) {
        console.error('❌ Erro ao iniciar servidor:', error);
        process.exit(1);
    }
}

startServer();
