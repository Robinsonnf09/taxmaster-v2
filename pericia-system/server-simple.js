require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

const app = express();
const PORT = process.env.PORT || 3000;

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

// Funções auxiliares
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

// ROTAS PÚBLICAS
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});

app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'OK', 
        timestamp: new Date(),
        service: 'Sistema de Perícia Judicial',
        version: '2.0.0 (JSON Mode)'
    });
});

// ROTAS DE OPORTUNIDADES
app.get('/api/oportunidades', async (req, res) => {
    try {
        const dados = lerUltimoScraper();
        console.log(`✓ Retornando ${dados.length} oportunidades`);
        res.json(dados);
    } catch (error) {
        console.error('Erro ao buscar oportunidades:', error);
        res.status(500).json({ error: 'Erro ao buscar oportunidades' });
    }
});

// ESTATÍSTICAS
app.get('/api/estatisticas', async (req, res) => {
    try {
        const oportunidades = lerUltimoScraper();
        
        const stats = {
            totalOportunidades: oportunidades.length,
            processosAtivos: oportunidades.filter(o => o.status !== 'Nova').length,
            receitaMensal: oportunidades.reduce((sum, o) => sum + (o.honorariosEstimados || 0), 0),
            taxaSucesso: 78.5,
            honorariosMedios: oportunidades.reduce((sum, o) => sum + (o.honorariosEstimados || 0), 0) / (oportunidades.length || 1)
        };
        
        console.log(`✓ Estatísticas: ${stats.totalOportunidades} oportunidades, R$ ${stats.receitaMensal.toLocaleString('pt-BR')}`);
        res.json(stats);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// SCRAPER
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

// INICIAR SERVIDOR
app.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════════════════════╗
║     SISTEMA DE PERÍCIA JUDICIAL - TAX MASTER             ║
║              VERSÃO SIMPLIFICADA (JSON MODE)             ║
║                                                           ║
║  Servidor rodando em: http://localhost:${PORT}               ║
║  Status: ONLINE ✓                                        ║
║  Ambiente: ${process.env.NODE_ENV || 'development'}                                  ║
║  Modo: Sem Banco de Dados (JSON Files)                  ║
║  Scraper: Integrado ✓                                    ║
╚═══════════════════════════════════════════════════════════╝

📄 PÁGINAS DISPONÍVEIS:
   → Dashboard: http://localhost:${PORT}
   → Calculadora: http://localhost:${PORT}/calculadora.html
   → CRM: http://localhost:${PORT}/crm.html
   → Relatórios: http://localhost:${PORT}/relatorios.html
   → Templates: http://localhost:${PORT}/templates.html
   → Login: http://localhost:${PORT}/login.html

⚠️  MODO SIMPLIFICADO ATIVO
   Para usar todas as funcionalidades (login, banco de dados, IA),
   instale o PostgreSQL e use o server-full.js

Pressione Ctrl+C para encerrar
    `);
});
