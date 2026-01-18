// ============================================
// CONFIGURAÇÃO API PÚBLICA DATAJUD - CNJ
// ============================================

const API_CONFIG = {
    // Base URL da API Pública
    baseURL: 'https://api-publica.datajud.cnj.jus.br/api_publica',
    
    // Chave Pública (disponível para todos)
    apiKey: 'cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==',
    
    // Headers padrão
    headers: {
        'Authorization': 'APIKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    },
    
    // Endpoints disponíveis
    endpoints: {
        tribunais: '/tribunais',
        processo: '/processos/{numeroProcesso}',
        movimentacoes: '/processos/{numeroProcesso}/movimentacoes',
        busca: '/processos/busca'
    }
};

// Função auxiliar para fazer requisições
async function apiRequest(endpoint, options = {}) {
    const url = `${API_CONFIG.baseURL}${endpoint}`;
    
    const config = {
        method: options.method || 'GET',
        headers: {
            ...API_CONFIG.headers,
            ...options.headers
        }
    };
    
    if (options.body) {
        config.body = JSON.stringify(options.body);
    }
    
    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Erro na requisição:', error);
        throw error;
    }
}

// Exportar configuração
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { API_CONFIG, apiRequest };
}
