// server.js - Versão CORRIGIDA
const express = require('express');
const session = require('express-session');
const path = require('path');
const { buscarProcessosESAJ } = require('./esajScraper');
const ExcelJS = require('exceljs');
const PDFDocument = require('pdfkit');

const app = express();
const PORT = process.env.PORT || 8080;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

app.use(session({
  secret: 'tax-master-secret-2024',
  resave: false,
  saveUninitialized: false,
  cookie: { maxAge: 24 * 60 * 60 * 1000 }
}));

// Middleware de autenticação
function requireAuth(req, res, next) {
  if (req.session && req.session.usuario) {
    return next();
  }
  res.redirect('/');
}

// Base de dados em memória
let processosCache = [];
let historicoBuscas = [];  // ✅ CORRIGIDO - SEM ESPAÇO!

// ============================================
// ROTAS DE AUTENTICAÇÃO
// ============================================

app.post('/api/auth/login', (req, res) => {
  const { usuario, senha } = req.body;
  
  if (usuario === 'admin' && senha === 'admin123') {
    req.session.usuario = { nome: usuario, role: 'admin' };
    res.json({ success: true, redirect: '/processos' });
  } else {
    res.status(401).json({ success: false, message: 'Credenciais inválidas' });
  }
});

app.post('/api/auth/logout', (req, res) => {
  req.session.destroy();
  res.json({ success: true });
});

// ============================================
// ROTAS DE BUSCA
// ============================================

app.get('/api/buscar-tjsp', requireAuth, async (req, res) => {
  try {
    const params = {
      valorMin: parseFloat(req.query.valorMin) || undefined,
      valorMax: parseFloat(req.query.valorMax) || undefined,
      natureza: req.query.natureza || 'Todas',
      anoLoa: req.query.anoLoa || 'Todos',
      status: req.query.status || 'Todos',
      quantidade: parseInt(req.query.quantidade) || 30
    };

    console.log(`\n📥 Nova busca REAL no ESAJ:`);
    console.log(`   Valor: ${params.valorMin || 0} - ${params.valorMax || '∞'}`);
    console.log(`   Natureza: ${params.natureza}`);

    const resultado = await buscarProcessosESAJ(params);
    
    processosCache = resultado.processos;
    
    historicoBuscas.push({
      data: new Date(),
      filtros: params,
      resultados: resultado.processos.length
    });

    res.json(resultado);
    
  } catch (error) {
    console.error(`❌ Erro na busca: ${error.message}`);
    res.status(500).json({ 
      processos: [], 
      stats: { erro: error.message } 
    });
  }
});

// ============================================
// ROTA DE DASHBOARD STATS
// ============================================

app.get('/api/dashboard-stats', requireAuth, (req, res) => {
  if (processosCache.length === 0) {
    return res.json({
      totalProcessos: 0,
      valorTotal: 0,
      pendentes: 0,
      pagos: 0,
      porNatureza: {},
      porLOA: {},
      valorPorNatureza: {},
      porStatus: {}
    });
  }

  const stats = {
    totalProcessos: processosCache.length,
    valorTotal: processosCache.reduce((sum, p) => sum + (p.valor || 0), 0),
    pendentes: processosCache.filter(p => p.status === 'Pendente').length,
    pagos: processosCache.filter(p => p.status === 'Pago').length,
    porNatureza: {},
    porLOA: {},
    valorPorNatureza: {},
    porStatus: {}
  };

  processosCache.forEach(p => {
    stats.porNatureza[p.natureza] = (stats.porNatureza[p.natureza] || 0) + 1;
    stats.valorPorNatureza[p.natureza] = (stats.valorPorNatureza[p.natureza] || 0) + (p.valor || 0);
    stats.porLOA[p.anoLOA] = (stats.porLOA[p.anoLOA] || 0) + 1;
    stats.porStatus[p.status] = (stats.porStatus[p.status] || 0) + 1;
  });

  res.json(stats);
});

// ============================================
// EXPORTAÇÃO EXCEL
// ============================================

app.get('/api/exportar/excel', requireAuth, async (req, res) => {
  try {
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Processos');

    worksheet.columns = [
      { header: 'Número do Processo', key: 'numero', width: 30 },
      { header: 'Tribunal', key: 'tribunal', width: 15 },
      { header: 'Credor', key: 'credor', width: 35 },
      { header: 'Valor (R$)', key: 'valor', width: 15 },
      { header: 'Natureza', key: 'natureza', width: 20 },
      { header: 'Ano LOA', key: 'anoLOA', width: 12 },
      { header: 'Status', key: 'status', width: 15 },
      { header: 'Classe', key: 'classe', width: 30 },
      { header: 'Vara', key: 'vara', width: 35 },
      { header: 'Data Distribuição', key: 'dataDistribuicao', width: 18 },
      { header: 'Fonte', key: 'fonte', width: 30 }
    ];

    worksheet.getRow(1).font = { bold: true, color: { argb: 'FFFFFFFF' } };
    worksheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF667eea' }
    };

    processosCache.forEach(p => {
      worksheet.addRow({
        numero: p.numero,
        tribunal: p.tribunal,
        credor: p.credor,
        valor: p.valor,
        natureza: p.natureza,
        anoLOA: p.anoLOA,
        status: p.status,
        classe: p.classe,
        vara: p.vara,
        dataDistribuicao: p.dataDistribuicao,
        fonte: p.fonteOriginal || p.fonte
      });
    });

    worksheet.getColumn('valor').numFmt = 'R$ #,##0.00';

    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    res.setHeader('Content-Disposition', `attachment; filename=processos_${new Date().toISOString().split('T')[0]}.xlsx`);

    await workbook.xlsx.write(res);
    res.end();

  } catch (error) {
    console.error('Erro ao gerar Excel:', error);
    res.status(500).json({ error: 'Erro ao gerar Excel' });
  }
});

// ============================================
// EXPORTAÇÃO PDF
// ============================================

app.get('/api/exportar/pdf', requireAuth, (req, res) => {
  try {
    const doc = new PDFDocument({ margin: 50, size: 'A4' });
    
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename=relatorio_${new Date().toISOString().split('T')[0]}.pdf`);
    
    doc.pipe(res);

    doc.fontSize(20).text('Tax Master V3', { align: 'center' });
    doc.fontSize(14).text('Relatório de Processos', { align: 'center' });
    doc.moveDown();
    doc.fontSize(10).text(`Gerado em: ${new Date().toLocaleString('pt-BR')}`, { align: 'center' });
    doc.moveDown(2);

    doc.fontSize(14).text('Resumo Executivo', { underline: true });
    doc.moveDown();
    doc.fontSize(10);
    doc.text(`Total de Processos: ${processosCache.length}`);
    doc.text(`Valor Total: R$ ${processosCache.reduce((sum, p) => sum + (p.valor || 0), 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`);
    doc.moveDown(2);

    doc.fontSize(14).text('Lista de Processos', { underline: true });
    doc.moveDown();
    
    processosCache.slice(0, 20).forEach((p, index) => {
      doc.fontSize(10);
      doc.text(`${index + 1}. ${p.numero}`, { continued: true });
      doc.text(` - R$ ${(p.valor || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`);
      doc.fontSize(8).text(`   Credor: ${p.credor} | Natureza: ${p.natureza} | Status: ${p.status}`);
      doc.moveDown(0.5);
    });

    doc.end();

  } catch (error) {
    console.error('Erro ao gerar PDF:', error);
    res.status(500).json({ error: 'Erro ao gerar PDF' });
  }
});

// ============================================
// RELATÓRIO EXECUTIVO
// ============================================

app.get('/api/relatorio/executivo', requireAuth, (req, res) => {
  try {
    const doc = new PDFDocument({ margin: 50, size: 'A4' });
    
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename=relatorio_executivo_${new Date().toISOString().split('T')[0]}.pdf`);
    
    doc.pipe(res);

    doc.fontSize(24).text('RELATÓRIO EXECUTIVO', { align: 'center' });
    doc.moveDown();
    doc.fontSize(18).text('Tax Master V3', { align: 'center' });
    doc.moveDown();
    doc.fontSize(12).text(`Período: ${new Date().toLocaleDateString('pt-BR')}`, { align: 'center' });
    doc.moveDown(5);

    const stats = {
      total: processosCache.length,
      valorTotal: processosCache.reduce((sum, p) => sum + (p.valor || 0), 0),
      pendentes: processosCache.filter(p => p.status === 'Pendente').length,
      pagos: processosCache.filter(p => p.status === 'Pago').length
    };

    doc.fontSize(16).text('ESTATÍSTICAS GERAIS', { underline: true });
    doc.moveDown();
    doc.fontSize(12);
    doc.text(`Total de Processos: ${stats.total}`);
    doc.text(`Valor Total: R$ ${stats.valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`);
    doc.text(`Processos Pendentes: ${stats.pendentes}`);
    doc.text(`Processos Pagos: ${stats.pagos}`);
    doc.moveDown(2);

    doc.fontSize(16).text('DISTRIBUIÇÃO POR NATUREZA', { underline: true });
    doc.moveDown();
    doc.fontSize(12);
    
    const porNatureza = {};
    processosCache.forEach(p => {
      porNatureza[p.natureza] = (porNatureza[p.natureza] || 0) + 1;
    });
    
    Object.entries(porNatureza).forEach(([natureza, qtd]) => {
      doc.text(`${natureza}: ${qtd} processos`);
    });
    
    doc.moveDown(2);

    doc.fontSize(16).text('TOP 10 PROCESSOS DE MAIOR VALOR', { underline: true });
    doc.moveDown();
    doc.fontSize(10);
    
    const top10 = [...processosCache]
      .sort((a, b) => (b.valor || 0) - (a.valor || 0))
      .slice(0, 10);
    
    top10.forEach((p, index) => {
      doc.text(`${index + 1}. ${p.numero}`);
      doc.text(`   Valor: R$ ${(p.valor || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })} | Credor: ${p.credor}`);
      doc.moveDown(0.5);
    });

    doc.end();

  } catch (error) {
    console.error('Erro ao gerar relatório:', error);
    res.status(500).json({ error: 'Erro ao gerar relatório' });
  }
});

// ============================================
// ROTAS DE PÁGINAS
// ============================================

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/processos', requireAuth, (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'processos.html'));
});

app.get('/dashboard', requireAuth, (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});

// ============================================
// INICIAR SERVIDOR
// ============================================

app.listen(PORT, () => {
  console.log('\n✅ Tax Master V3 - API CNJ DataJud');
  console.log('🔍 Fonte: API CNJ DataJud (Oficial)');
  console.log('⚠️ Delay de 2s entre requisições');
  console.log(`🚀 Servidor na porta ${PORT}`);
  console.log('\n✅ Sistema pronto com API CNJ DataJud!');
});
