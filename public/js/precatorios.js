const API_URL = window.location.origin;
const token = localStorage.getItem('token');
const usuario = JSON.parse(localStorage.getItem('usuario') || '{}');

// Verificar autenticação
if (!token) {
    document.getElementById('userInfo').innerHTML = '<a href="/login.html" style="color: white; text-decoration: none;">Fazer Login</a>';
} else {
    document.getElementById('userInfo').textContent = `👤 ${usuario.nome}`;
    carregarPrecatorios();
}

// Carregar precatórios
async function carregarPrecatorios() {
    try {
        const response = await fetch(`${API_URL}/api/precatorios`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const precatorios = await response.json();
        
        const tbody = document.getElementById('precatoriosBody');
        
        if (precatorios.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--gray-700);">Nenhum precatório cadastrado. Clique em "+ Novo Precatório" para adicionar.</td></tr>';
            return;
        }
        
        tbody.innerHTML = precatorios.map(p => `
            <tr>
                <td>${p.numero_processo}</td>
                <td>${p.tribunal}</td>
                <td>${p.beneficiario}</td>
                <td><span class="badge ${p.natureza === 'alimentar' ? 'receita' : 'despesa'}">${p.natureza}</span></td>
                <td style="font-weight: bold; color: var(--success);">R$ ${parseFloat(p.valor_corrigido).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                <td>${formatarStatus(p.status)}</td>
                <td>
                    <button class="btn btn-secondary" onclick="editarPrecatorio(${p.id})" style="padding: 0.5rem 1rem; font-size: 0.9rem;">✏️</button>
                    <button class="btn btn-danger" onclick="deletarPrecatorio(${p.id})" style="padding: 0.5rem 1rem; font-size: 0.9rem;">🗑️</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar precatórios:', error);
        document.getElementById('precatoriosBody').innerHTML = '<tr><td colspan="7" style="text-align: center; color: red; padding: 2rem;">❌ Erro ao carregar. Configure o banco de dados no Railway.</td></tr>';
    }
}

function formatarStatus(status) {
    const statusMap = {
        'em_formacao': '⏳ Em Formação',
        'formado': '✅ Formado',
        'em_pagamento': '💰 Em Pagamento',
        'pago': '✅ Pago',
        'vendido': '🤝 Vendido'
    };
    return statusMap[status] || status;
}

function abrirModalPrecatorio() {
    if (!token) {
        alert('⚠️ Faça login para cadastrar precatórios');
        window.location.href = '/login.html';
        return;
    }
    document.getElementById('modalPrecatorio').classList.add('active');
}

function fecharModalPrecatorio() {
    document.getElementById('modalPrecatorio').classList.remove('active');
    document.getElementById('formPrecatorio').reset();
}

async function salvarPrecatorio(event) {
    event.preventDefault();
    
    const dados = {
        numero_processo: document.getElementById('numero_processo').value,
        tribunal: document.getElementById('tribunal').value,
        ente_devedor: document.getElementById('ente_devedor').value,
        natureza: document.getElementById('natureza').value,
        beneficiario: document.getElementById('beneficiario').value,
        cpf_cnpj: document.getElementById('cpf_cnpj').value,
        valor_principal: parseFloat(document.getElementById('valor_principal').value),
        valor_corrigido: parseFloat(document.getElementById('valor_corrigido').value),
        data_base: document.getElementById('data_base').value,
        data_formacao: document.getElementById('data_formacao').value || null,
        status: document.getElementById('status').value,
        observacoes: document.getElementById('observacoes').value
    };
    
    try {
        const response = await fetch(`${API_URL}/api/precatorios`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(dados)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('✅ Precatório cadastrado com sucesso!');
            fecharModalPrecatorio();
            carregarPrecatorios();
        } else {
            alert('❌ Erro: ' + (result.error || 'Erro ao salvar'));
        }
    } catch (error) {
        alert('❌ Erro de conexão. Verifique se o banco está configurado.');
    }
}

async function deletarPrecatorio(id) {
    if (!confirm('Tem certeza que deseja excluir este precatório?')) return;
    
    try {
        const response = await fetch(`${API_URL}/api/precatorios/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('✅ Precatório excluído!');
            carregarPrecatorios();
        }
    } catch (error) {
        alert('❌ Erro ao excluir');
    }
}
