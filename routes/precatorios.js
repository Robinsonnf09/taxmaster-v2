const express = require('express');
const { pool } = require('../database/config');
const { verificarToken } = require('../middleware/auth');

const router = express.Router();

// Listar precatórios
router.get('/', verificarToken, async (req, res) => {
    try {
        const result = await pool.query(
            'SELECT * FROM precatorios WHERE usuario_id = $1 ORDER BY created_at DESC',
            [req.usuario.id]
        );
        res.json(result.rows);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erro ao buscar precatórios' });
    }
});

// Criar precatório
router.post('/', verificarToken, async (req, res) => {
    try {
        const { 
            numero_processo, tribunal, ente_devedor, natureza, beneficiario, 
            cpf_cnpj, valor_principal, valor_corrigido, data_base, data_formacao, 
            status, observacoes 
        } = req.body;
        
        const result = await pool.query(
            `INSERT INTO precatorios (
                numero_processo, tribunal, ente_devedor, natureza, beneficiario,
                cpf_cnpj, valor_principal, valor_corrigido, data_base, data_formacao,
                status, observacoes, usuario_id
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13) RETURNING *`,
            [numero_processo, tribunal, ente_devedor, natureza, beneficiario,
             cpf_cnpj, valor_principal, valor_corrigido, data_base, data_formacao,
             status, observacoes, req.usuario.id]
        );
        
        res.json({ success: true, precatorio: result.rows[0] });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erro ao criar precatório' });
    }
});

// Atualizar precatório
router.put('/:id', verificarToken, async (req, res) => {
    try {
        const { id } = req.params;
        const campos = req.body;
        
        const setClauses = Object.keys(campos).map((key, i) => `${key} = $${i + 1}`).join(', ');
        const values = [...Object.values(campos), req.usuario.id, id];
        
        const result = await pool.query(
            `UPDATE precatorios SET ${setClauses} WHERE usuario_id = $${values.length - 1} AND id = $${values.length} RETURNING *`,
            values
        );
        
        res.json({ success: true, precatorio: result.rows[0] });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erro ao atualizar precatório' });
    }
});

// Deletar precatório
router.delete('/:id', verificarToken, async (req, res) => {
    try {
        const { id } = req.params;
        
        await pool.query(
            'DELETE FROM precatorios WHERE id = $1 AND usuario_id = $2',
            [id, req.usuario.id]
        );
        
        res.json({ success: true });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erro ao deletar precatório' });
    }
});

module.exports = router;
