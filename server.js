const express = require('express');
const path = require('path');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { buscarProcessosOficial } = require('./datajudOficialAdapter');

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = 'taxmaster-secret-key-2024-v3';

app.use(express.json());
app.use(express.static('pages'));

const usuarios = [
    { id: 1, nome: 'Administrador', email: 'admin@taxmaster.com', senha: bcrypt.hashSync('admin123', 10), perfil: 'admin' }
];

let processos = [];

console.log('✅ Tax Master V3 - com Estatísticas e Debug');

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'login.html'));
});

app.get('/health', (req, res) => {
    res.json({ status: 'ok', processos: processos.length, versao: '3.0.0-stats', timestamp: new Date().toISOString() });
});

app.post('/api/auth/login', (req, res) => {
    const { email, senha } = req.body;
    const usuario = usuarios.find(u => u.email === email);
    
    if (!usuario || !bcrypt.compareSync(senha, usuario.senha)) {
        return res.status(401).json({ erro: 'Credenciais inválidas' });
    }
    
    const token = jwt.sign({ id: usuario.id, email: usuario.email, perfil: usuario.perfil }, JWT_SECRET, { expiresIn: '24h' });
    
    res.json({ token, usuario: { id: usuario.id, nome: usuario.nome, email: usuario.email, perfil: usuario.perfil } });
});

function autenticar(req, res, next) {
    const token = req.headers.authorization?.replace('Bearer ', '');
    if (!token) return res.status(401).json({ erro: 'Token não fornecido' });
    
    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        req.usuario = decoded;
        next();
    } catch (error) {
        return res.status(401).json({ erro: 'Token inválido' });
    }
}

app.get('/api/buscar-processos-oficiais', autenticar, async (req, res) => {
    try {
        const { tribunal, valorMinimo, valorMaximo, natureza, anoLOA } = req.query;

        const hoje = new Date();
        const dataFim = hoje.toISOString().split('T')[0];
        const umAnoAtras = new Date(hoje.setFullYear(hoje.getFullYear() - 1));
        const dataInicio = umAnoAtras.toISOString().split('T')[0];

        const resultado = await buscarProcessosOficial({
            tribunalDesejado: tribunal || null,
            valorMin: valorMinimo ? Number(valorMinimo) : null,
            valorMax: valorMaximo ? Number(valorMaximo) : null,
            natureza,
            anoLoa: anoLOA ? Number(anoLOA) : null,
            dataInicio,
            dataFim,
        });

        // ✅ SUGESTÕES SE RESULTADO = 0
        let sugestoes = [];
        if (resultado.processos.length === 0 && resultado.stats.totalAPI > 0) {
            sugestoes.push('💡 A API retornou dados, mas os filtros eliminaram tudo');
            
            if (valorMinimo || valorMaximo) {
                sugestoes.push(`Tente relaxar o filtro de valor (atual: R$ ${valorMinimo || 0} - R$ ${valorMaximo || '∞'})`);
            }
            
            if (tribunal) {
                sugestoes.push(`Tente buscar em TODOS os tribunais (não apenas ${tribunal})`);
            }
            
            if (natureza) {
                sugestoes.push(`Tente buscar TODAS as naturezas (não apenas ${natureza})`);
            }
        }

        res.json({
            sucesso: true,
            total: resultado.processos.length,
            processos: resultado.processos,
            stats: resultado.stats,
            sugestoes: sugestoes,
            fonte: 'DataJud CNJ (API Oficial v1)',
            periodo: `${dataInicio} até ${dataFim}`
        });
    } catch (err) {
        console.error(err);
        res.status(500).json({ erro: 'Erro ao consultar DataJud', mensagem: err.message });
    }
});

app.get('/api/buscar-tjsp', autenticar, (req, res) => {
    req.url = '/api/buscar-processos-oficiais';
    app.handle(req, res);
});

app.post('/api/processos/importar', autenticar, (req, res) => {
    const processo = req.body;
    processo.id = processos.length + 1;
    processos.push(processo);
    res.json({ sucesso: true, mensagem: 'Processo importado', id: processo.id });
});

app.get('/api/processos', autenticar, (req, res) => {
    res.json(processos);
});

app.get('/processos', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'processos.html'));
});

app.get('/importar', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'importar.html'));
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Servidor na porta ${PORT}`);
});
