// DADOS SIMULADOS (LocalStorage)
const STORAGE_KEY = 'taxmaster_financeiro';

function getData() {
    const data = localStorage.getItem(STORAGE_KEY);
    if (data) {
        return JSON.parse(data);
    }
    return {
        receitas: [
            { id: 1, data: '2026-01-15', descricao: 'Venda Precatório BA-2024-0123', categoria: 'precatorios', valor: 150000 },
            { id: 2, data: '2026-01-10', descricao: 'Consultoria Recuperação ICMS', categoria: 'consultoria', valor: 25000 },
            { id: 3, data: '2026-01-08', descricao: 'Honorários Processo 123456', categoria: 'honorarios', valor: 15000 }
        ],
        despesas: [
            { id: 1, data: '2026-01-12', descricao: 'Aluguel Escritório', categoria: 'operacional', valor: 8000 },
            { id: 2, data: '2026-01-05', descricao: 'Salários Equipe', categoria: 'pessoal', valor: 35000 },
            { id: 3, data: '2026-01-18', descricao: 'Marketing Digital', categoria: 'marketing', valor: 5000 }
        ]
    };
}

function saveData(data) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

// FUNÇÕES DE CÁLCULO
function calcularTotais() {
    const data = getData();
    const totalReceitas = data.receitas.reduce((sum, r) => sum + r.valor, 0);
    const totalDespesas = data.despesas.reduce((sum, d) => sum + d.valor, 0);
    const saldoLiquido = totalReceitas - totalDespesas;
    const rentabilidade = totalReceitas > 0 ? ((saldoLiquido / totalReceitas) * 100).toFixed(2) : 0;

    return { totalReceitas, totalDespesas, saldoLiquido, rentabilidade };
}

function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor);
}

function formatarData(data) {
    return new Date(data + 'T00:00:00').toLocaleDateString('pt-BR');
}

// ATUALIZAR DASHBOARD
function atualizarDashboard() {
    const { totalReceitas, totalDespesas, saldoLiquido, rentabilidade } = calcularTotais();

    document.getElementById('totalReceitas').textContent = formatarMoeda(totalReceitas);
    document.getElementById('totalDespesas').textContent = formatarMoeda(totalDespesas);
    document.getElementById('saldoLiquido').textContent = formatarMoeda(saldoLiquido);
    document.getElementById('rentabilidade').textContent = rentabilidade + '%';

    // Atualizar tabela de transações
    const data = getData();
    const transacoes = [
        ...data.receitas.map(r => ({ ...r, tipo: 'receita' })),
        ...data.despesas.map(d => ({ ...d, tipo: 'despesa' }))
    ].sort((a, b) => new Date(b.data) - new Date(a.data)).slice(0, 10);

    const tbody = document.getElementById('transactionsBody');
    tbody.innerHTML = transacoes.map(t => `
        <tr>
            <td>${formatarData(t.data)}</td>
            <td>${t.descricao}</td>
            <td>${t.categoria}</td>
            <td><span class="badge ${t.tipo}">${t.tipo === 'receita' ? 'Receita' : 'Despesa'}</span></td>
            <td style="color: ${t.tipo === 'receita' ? 'var(--success)' : 'var(--danger)'}">${formatarMoeda(t.valor)}</td>
        </tr>
    `).join('');
}

// RECEITAS
function carregarReceitas() {
    const data = getData();
    const tbody = document.getElementById('receitasBody');
    tbody.innerHTML = data.receitas.map(r => `
        <tr>
            <td>${formatarData(r.data)}</td>
            <td>${r.descricao}</td>
            <td>${r.categoria}</td>
            <td style="color: var(--success); font-weight: bold">${formatarMoeda(r.valor)}</td>
            <td>
                <button class="btn btn-danger" onclick="deletarReceita(${r.id})">🗑️ Excluir</button>
            </td>
        </tr>
    `).join('');
}

function abrirModalReceita() {
    document.getElementById('modalReceita').classList.add('active');
    document.getElementById('receitaData').value = new Date().toISOString().split('T')[0];
}

function fecharModalReceita() {
    document.getElementById('modalReceita').classList.remove('active');
    document.getElementById('formReceita').reset();
}

function salvarReceita(event) {
    event.preventDefault();
    const data = getData();
    
    const novaReceita = {
        id: Date.now(),
        data: document.getElementById('receitaData').value,
        descricao: document.getElementById('receitaDescricao').value,
        categoria: document.getElementById('receitaCategoria').value,
        valor: parseFloat(document.getElementById('receitaValor').value)
    };

    data.receitas.push(novaReceita);
    saveData(data);
    
    fecharModalReceita();
    carregarReceitas();
    atualizarDashboard();
    
    alert('✅ Receita cadastrada com sucesso!');
}

function deletarReceita(id) {
    if (confirm('Tem certeza que deseja excluir esta receita?')) {
        const data = getData();
        data.receitas = data.receitas.filter(r => r.id !== id);
        saveData(data);
        carregarReceitas();
        atualizarDashboard();
    }
}

// DESPESAS
function carregarDespesas() {
    const data = getData();
    const tbody = document.getElementById('despesasBody');
    tbody.innerHTML = data.despesas.map(d => `
        <tr>
            <td>${formatarData(d.data)}</td>
            <td>${d.descricao}</td>
            <td>${d.categoria}</td>
            <td style="color: var(--danger); font-weight: bold">${formatarMoeda(d.valor)}</td>
            <td>
                <button class="btn btn-danger" onclick="deletarDespesa(${d.id})">🗑️ Excluir</button>
            </td>
        </tr>
    `).join('');
}

function abrirModalDespesa() {
    document.getElementById('modalDespesa').classList.add('active');
    document.getElementById('despesaData').value = new Date().toISOString().split('T')[0];
}

function fecharModalDespesa() {
    document.getElementById('modalDespesa').classList.remove('active');
    document.getElementById('formDespesa').reset();
}

function salvarDespesa(event) {
    event.preventDefault();
    const data = getData();
    
    const novaDespesa = {
        id: Date.now(),
        data: document.getElementById('despesaData').value,
        descricao: document.getElementById('despesaDescricao').value,
        categoria: document.getElementById('despesaCategoria').value,
        valor: parseFloat(document.getElementById('despesaValor').value)
    };

    data.despesas.push(novaDespesa);
    saveData(data);
    
    fecharModalDespesa();
    carregarDespesas();
    atualizarDashboard();
    
    alert('✅ Despesa cadastrada com sucesso!');
}

function deletarDespesa(id) {
    if (confirm('Tem certeza que deseja excluir esta despesa?')) {
        const data = getData();
        data.despesas = data.despesas.filter(d => d.id !== id);
        saveData(data);
        carregarDespesas();
        atualizarDashboard();
    }
}

// NAVEGAÇÃO SIDEBAR
document.querySelectorAll('.sidebar-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const section = link.getAttribute('data-section');
        
        document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
        document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
        
        link.classList.add('active');
        document.getElementById(section).classList.add('active');
        
        if (section === 'dashboard') atualizarDashboard();
        if (section === 'receitas') carregarReceitas();
        if (section === 'despesas') carregarDespesas();
    });
});

// RELATÓRIOS
function gerarRelatorio() {
    const { totalReceitas, totalDespesas, saldoLiquido, rentabilidade } = calcularTotais();
    
    document.getElementById('reportReceitas').textContent = formatarMoeda(totalReceitas);
    document.getElementById('reportDespesas').textContent = formatarMoeda(totalDespesas);
    document.getElementById('reportResultado').textContent = formatarMoeda(saldoLiquido);
    document.getElementById('reportMargem').textContent = rentabilidade + '%';
}

function exportarRelatorio() {
    alert('📥 Funcionalidade de exportação será implementada em breve!');
}

// INICIALIZAÇÃO
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('dashboard')) {
        atualizarDashboard();
    }
});
