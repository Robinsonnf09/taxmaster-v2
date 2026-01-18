const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'taxmaster_secret_key_2026';

function verificarToken(req, res, next) {
    const token = req.headers['authorization']?.split(' ')[1];
    
    if (!token) {
        return res.status(401).json({ error: 'Token não fornecido' });
    }
    
    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        req.usuario = decoded;
        next();
    } catch (error) {
        return res.status(401).json({ error: 'Token inválido' });
    }
}

module.exports = { verificarToken, JWT_SECRET };
