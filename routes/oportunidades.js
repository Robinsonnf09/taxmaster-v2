const express = require('express');
const { pool } = require('../database/config');
const { verificarToken } = require('../middleware/auth');

const router = express.Router();

// Listar oportunidades
router.get('/', async (req, res) => {
    try {
        const { tribunal, natureza, valor_min, valor_max } = req.query;
        
        let query = 'SELECT * FROM oportunidades WHERE status = $1';
        let params = ['disponivel'];
        let paramIndex = 2;
        
        if (tribunal) {
            query += ` AND tribunal = $${paramIndex}`;
            params.push(tribunal);
            paramIndex++;
        }
        
        if (natureza) {
            query += ` AND natureza = $${paramIndex}`;
            params.push(natureza);
            paramIndex++;
        }
        
        if (valor_min) {
            query += ` AND valor >= $${paramIndex}`;
            params.push(valor_min);
            paramIndex++;
        }
        
        if (valor_max) {
            query += ` AND valor <= $${paramIndex}`;
            params.push(valor_max);
            paramIndex++;
        }
        
        query += ' ORDER BY valor DESC';
        
        const result = await pool.query(query, params);
        res.json(result.rows);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erro ao buscar oportunidades' });
    }
});

// Importar oportunidades (planilha Bahia)
router.post('/importar', verificarToken, async (req, res) => {
    try {
        const oportunidades = req.body.oportunidades;
        
        for (const opp of oportunidades) {
            await pool.query(
                `INSERT INTO oportunidades (numero_precatorio, tribunal, valor, natureza, beneficiario, ano, deságio, rentabilidade)
                 VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                 ON CONFLICT DO NOTHING`,
                [opp.numero_precatorio, opp.tribunal, opp.valor, opp.natureza, 
                 opp.beneficiario, opp.ano, opp.deságio, opp.rentabilidade]
            );
        }
        
        res.json({ success: true, message: `${oportunidades.length} oportunidades importadas` });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Erro ao importar oportunidades' });
    }
});

module.exports = router;
