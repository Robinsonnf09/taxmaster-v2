const jwt = require('jsonwebtoken');
const JWT_SECRET = process.env.JWT_SECRET || 'taxmaster-secret-key-2024-v3';

function autenticar(req, res, next) {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (!token) {
        return res.status(401).json({ erro: 'Token não fornecido' });
    }
    
    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        req.usuario = decoded;
        next();
    } catch (error) {
        return res.status(401).json({ erro: 'Token inválido' });
    }
}

function autorizarPerfil(...perfisPermitidos) {
    return (req, res, next) => {
        if (!perfisPermitidos.includes(req.usuario.perfil)) {
            return res.status(403).json({ erro: 'Acesso negado' });
        }
        next();
    };
}

module.exports = { autenticar, autorizarPerfil, JWT_SECRET };
