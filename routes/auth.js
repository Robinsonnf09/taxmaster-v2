const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { pool } = require('../database/config');
const { JWT_SECRET } = require('../middleware/auth');

const router = express.Router();

// Registrar usuário
router.post('/registrar', async (req, res) => {
    try {
        const { nome, email, senha } = req.body;
        
        const senhaCriptografada = await bcrypt.hash(senha, 10);
        
        const result = await pool.query(
            'INSERT INTO usuarios (nome, email, senha) VALUES ($1, $2, $3) RETURNING id, nome, email',
            [nome, email, senhaCriptografada]
        );
        
        res.json({ success: true, usuario: result.rows[0] });
    } catch (error) {
        console.error(error);
        res.status(400).json({ error: 'Erro ao registrar usuário' });
    }
});

// Login
router.post('/login', async (req, res) => {
    try {
        const { email, senha } = req.body;
        
        const result = await pool.query('SELECT * FROM usuarios WHERE email = $1', [email]);
        
        if (result.rows.length === 0) {
            return res.status(401).json({ error: 'Credenciais inválidas' });
        }
        
        const usuario = result.rows[0];
        const senhaValida = await bcrypt.compare(senha, usuario.senha);
        
        if (!senhaValida) {
            return res.status(401).json({ error: 'Credenciais inválidas' });
        }
        
        const token = jwt.sign(
            { id: usuario.id, email: usuario.email, nome: usuario.nome },
            JWT_SECRET,
            { expiresIn: '7d' }
        );
        
        res.json({ 
            success: true, 
            token,
            usuario: { id: usuario.id, nome: usuario.nome, email: usuario.email }
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erro ao fazer login' });
    }
});

module.exports = router;
