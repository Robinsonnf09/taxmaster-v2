const express = require('express');
const { pool } = require('../database/config');
const { verificarToken } = require('../middleware/auth');

const router = express.Router();

// Receitas
router.get('/receitas', verificarToken, async (req, res) => {
    try {
        const result = await pool.query(
            'SELECT * FROM receitas WHERE usuario_id = $1 ORDER BY data DESC',
            [req.usuario.id]
        );
        res.json(result.rows);
    } catch (error) {
        res.status(500).json({ error: 'Erro ao buscar receitas' });
    }
});

router.post('/receitas', verificarToken, async (req, res) => {
    try {
        const { data, descricao, categoria, valor } = req.body;
        const result = await pool.query(
            'INSERT INTO receitas (data, descricao, categoria, valor, usuario_id) VALUES ($1, $2, $3, $4, $5) RETURNING *',
            [data, descricao, categoria, valor, req.usuario.id]
        );
        res.json({ success: true, receita: result.rows[0] });
    } catch (error) {
        res.status(500).json({ error: 'Erro ao criar receita' });
    }
});

router.delete('/receitas/:id', verificarToken, async (req, res) => {
    try {
        await pool.query('DELETE FROM receitas WHERE id = $1 AND usuario_id = $2', [req.params.id, req.usuario.id]);
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: 'Erro ao deletar receita' });
    }
});

// Despesas
router.get('/despesas', verificarToken, async (req, res) => {
    try {
        const result = await pool.query(
            'SELECT * FROM despesas WHERE usuario_id = $1 ORDER BY data DESC',
            [req.usuario.id]
        );
        res.json(result.rows);
    } catch (error) {
        res.status(500).json({ error: 'Erro ao buscar despesas' });
    }
});

router.post('/despesas', verificarToken, async (req, res) => {
    try {
        const { data, descricao, categoria, valor } = req.body;
        const result = await pool.query(
            'INSERT INTO despesas (data, descricao, categoria, valor, usuario_id) VALUES ($1, $2, $3, $4, $5) RETURNING *',
            [data, descricao, categoria, valor, req.usuario.id]
        );
        res.json({ success: true, despesa: result.rows[0] });
    } catch (error) {
        res.status(500).json({ error: 'Erro ao criar despesa' });
    }
});

router.delete('/despesas/:id', verificarToken, async (req, res) => {
    try {
        await pool.query('DELETE FROM despesas WHERE id = $1 AND usuario_id = $2', [req.params.id, req.usuario.id]);
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: 'Erro ao deletar despesa' });
    }
});

module.exports = router;
