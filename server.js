const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const ExcelJS = require('exceljs');
const PDFDocument = require('pdfkit');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname)));

// Conectar ao banco SQLite
const db = new sqlite3.Database('./taxmaster.db', (err) => {
    if (err) {
        console.error('❌ Erro ao conectar banco:', err);
    } else {
        console.log('✅ Conectado ao taxmaster.db');
    }
});

// Contar processos no banco
db.get('SELECT COUNT(*) as total FROM processos', (err, row) => {
    if (err) {
        console.error('❌ Erro ao contar processos:', err);
    } else {
        console.log(`✅ ${row.total} processos reais carregados do banco!`);
    }
});

// Rotas
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/processos', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'processos.html'), (err) => {
        if (err) res.sendFile(path.join(__dirname, 'index.html'));
    });
});

app.get('/dashboard', (req, res) => {
    res.sendFile(path.join(__dirname, 'pages', 'dashboard.html'));
});

// API: Buscar processos REAIS do banco
app.get('/api/processos', (req, res) => {
    let query = 'SELECT * FROM processos WHERE 1=1';
    const params = [];
    
    if (req.query.tribunal) {
        query += ' AND tribunal = ?';
        params.push(req.query.tribunal);
    }
    
    if (req.query.status) {
        query += ' AND status = ?';
        params.push(req.query.status);
    }
    
    if (req.query.busca) {
        query += ' AND (numero LIKE ? OR credor LIKE ?)';
        const termo = `%${req.query.busca}%`;
        params.push(termo, termo);
    }
    
    db.all(query, params, (err, rows) => {
        if (err) {
            console.error('❌ Erro ao buscar processos:', err);
            res.status(500).json({ error: err.message });
        } else {
            res.json(rows);
        }
    });
});

// API: Exportar para Excel
app.get('/api/export/excel', async (req, res) => {
    try {
        const query = 'SELECT * FROM processos';
        db.all(query, async (err, processos) => {
            if (err) {
                return res.status(500).json({ error: err.message });
            }

            const workbook = new ExcelJS.Workbook();
            const worksheet = workbook.addWorksheet('Processos');

            // Cabeçalhos
            worksheet.columns = [
                { header: 'ID', key: 'id', width: 10 },
                { header: 'Número do Processo', key: 'numero', width: 30 },
                { header: 'Tribunal', key: 'tribunal', width: 15 },
                { header: 'Credor', key: 'credor', width: 30 },
                { header: 'Valor (R$)', key: 'valor', width: 15 },
                { header: 'Status', key: 'status', width: 15 },
                { header: 'Data Distribuição', key: 'dataDistribuicao', width: 20 }
            ];

            // Estilizar cabeçalho
            worksheet.getRow(1).font = { bold: true };
            worksheet.getRow(1).fill = {
                type: 'pattern',
                pattern: 'solid',
                fgColor: { argb: 'FF667eea' }
            };

            // Adicionar dados
            processos.forEach(p => {
                worksheet.addRow(p);
            });

            // Adicionar totais
            const totalRow = worksheet.addRow({
                numero: 'TOTAL',
                valor: processos.reduce((sum, p) => sum + parseFloat(p.valor || 0), 0)
            });
            totalRow.font = { bold: true };

            // Configurar resposta
            res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
            res.setHeader('Content-Disposition', 'attachment; filename=processos_taxmaster.xlsx');

            await workbook.xlsx.write(res);
            res.end();
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// API: Exportar para PDF
app.get('/api/export/pdf', (req, res) => {
    const query = 'SELECT * FROM processos';
    db.all(query, (err, processos) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }

        const doc = new PDFDocument({ margin: 50, size: 'A4' });
        
        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', 'attachment; filename=processos_taxmaster.pdf');
        
        doc.pipe(res);

        // Título
        doc.fontSize(20).text('Tax Master - Relatório de Processos', { align: 'center' });
        doc.moveDown();
        doc.fontSize(12).text(`Data: ${new Date().toLocaleDateString('pt-BR')}`, { align: 'center' });
        doc.moveDown(2);

        // Estatísticas
        const total = processos.length;
        const valorTotal = processos.reduce((sum, p) => sum + parseFloat(p.valor || 0), 0);
        
        doc.fontSize(14).text('Resumo Executivo', { underline: true });
        doc.moveDown();
        doc.fontSize(12);
        doc.text(`Total de Processos: ${total}`);
        doc.text(`Valor Total: R$ ${valorTotal.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);
        doc.moveDown(2);

        // Lista de processos
        doc.fontSize(14).text('Lista de Processos', { underline: true });
        doc.moveDown();

        processos.forEach((p, index) => {
            if (index > 0 && index % 8 === 0) {
                doc.addPage();
            }

            doc.fontSize(10);
            doc.text(`${index + 1}. ${p.numero}`, { continued: true });
            doc.text(` - ${p.tribunal}`, { align: 'right' });
            doc.fontSize(9);
            doc.text(`   Credor: ${p.credor}`);
            doc.text(`   Valor: R$ ${parseFloat(p.valor || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2})} | Status: ${p.status}`);
            doc.moveDown(0.5);
        });

        doc.end();
    });
});

// API: Estatísticas
app.get('/api/estatisticas', (req, res) => {
    db.get('SELECT COUNT(*) as total, SUM(valor) as valorTotal FROM processos', (err, row) => {
        if (err) {
            res.status(500).json({ error: err.message });
        } else {
            res.json({
                total: row.total,
                valorTotal: row.valorTotal || 0
            });
        }
    });
});

// Health check
app.get('/health', (req, res) => {
    db.get('SELECT COUNT(*) as total FROM processos', (err, row) => {
        if (err) {
            res.status(500).json({ status: 'ERROR', error: err.message });
        } else {
            res.json({
                status: 'OK',
                timestamp: new Date().toISOString(),
                processos: row.total,
                fonte: 'taxmaster.db (DADOS REAIS)'
            });
        }
    });
});

// Iniciar servidor
app.listen(PORT, '0.0.0.0', () => {
    console.log(`✅ Tax Master na porta ${PORT}`);
    console.log(`📊 Usando banco de dados REAL: taxmaster.db`);
});
