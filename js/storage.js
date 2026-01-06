// Módulo de armazenamento local para o TAX MASTER
// Implementa funções para salvar e recuperar dados no localStorage do navegador

TAXMASTER.storage = {
    // Prefixo para chaves no localStorage
    prefix: 'taxmaster_',
    
    // Salvar dados no localStorage
    set: function(key, value) {
        try {
            const fullKey = this.prefix + key;
            const serializedValue = JSON.stringify(value);
            localStorage.setItem(fullKey, serializedValue);
            return true;
        } catch (error) {
            console.error('Erro ao salvar dados no localStorage:', error);
            return false;
        }
    },
    
    // Recuperar dados do localStorage
    get: function(key) {
        try {
            const fullKey = this.prefix + key;
            const serializedValue = localStorage.getItem(fullKey);
            
            if (serializedValue === null) {
                return null;
            }
            
            return JSON.parse(serializedValue);
        } catch (error) {
            console.error('Erro ao recuperar dados do localStorage:', error);
            return null;
        }
    },
    
    // Remover dados do localStorage
    remove: function(key) {
        try {
            const fullKey = this.prefix + key;
            localStorage.removeItem(fullKey);
            return true;
        } catch (error) {
            console.error('Erro ao remover dados do localStorage:', error);
            return false;
        }
    },
    
    // Limpar todos os dados do TAX MASTER no localStorage
    clear: function() {
        try {
            // Obter todas as chaves do localStorage
            const keys = Object.keys(localStorage);
            
            // Filtrar apenas as chaves do TAX MASTER
            const taxMasterKeys = keys.filter(key => key.startsWith(this.prefix));
            
            // Remover cada chave
            taxMasterKeys.forEach(key => localStorage.removeItem(key));
            
            return true;
        } catch (error) {
            console.error('Erro ao limpar dados do localStorage:', error);
            return false;
        }
    },
    
    // Verificar se o localStorage está disponível
    isAvailable: function() {
        try {
            const testKey = this.prefix + 'test';
            localStorage.setItem(testKey, 'test');
            localStorage.removeItem(testKey);
            return true;
        } catch (error) {
            console.error('localStorage não está disponível:', error);
            return false;
        }
    },
    
    // Obter tamanho total utilizado pelo TAX MASTER no localStorage
    getSize: function() {
        try {
            // Obter todas as chaves do localStorage
            const keys = Object.keys(localStorage);
            
            // Filtrar apenas as chaves do TAX MASTER
            const taxMasterKeys = keys.filter(key => key.startsWith(this.prefix));
            
            // Calcular tamanho total
            let totalSize = 0;
            
            taxMasterKeys.forEach(key => {
                const value = localStorage.getItem(key);
                totalSize += (key.length + value.length) * 2; // Aproximação em bytes (2 bytes por caractere em UTF-16)
            });
            
            return totalSize;
        } catch (error) {
            console.error('Erro ao calcular tamanho do localStorage:', error);
            return 0;
        }
    },
    
    // Exportar todos os dados do TAX MASTER
    exportData: function() {
        try {
            // Obter todas as chaves do localStorage
            const keys = Object.keys(localStorage);
            
            // Filtrar apenas as chaves do TAX MASTER
            const taxMasterKeys = keys.filter(key => key.startsWith(this.prefix));
            
            // Criar objeto com todos os dados
            const exportData = {};
            
            taxMasterKeys.forEach(key => {
                const shortKey = key.substring(this.prefix.length);
                exportData[shortKey] = JSON.parse(localStorage.getItem(key));
            });
            
            return {
                success: true,
                data: exportData,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            console.error('Erro ao exportar dados do localStorage:', error);
            return {
                success: false,
                error: error.message
            };
        }
    },
    
    // Importar dados para o TAX MASTER
    importData: function(importData) {
        try {
            // Verificar se os dados são válidos
            if (!importData || !importData.data || typeof importData.data !== 'object') {
                throw new Error('Dados de importação inválidos');
            }
            
            // Importar cada item
            Object.keys(importData.data).forEach(shortKey => {
                const fullKey = this.prefix + shortKey;
                const value = importData.data[shortKey];
                localStorage.setItem(fullKey, JSON.stringify(value));
            });
            
            return {
                success: true,
                keysImported: Object.keys(importData.data).length
            };
        } catch (error) {
            console.error('Erro ao importar dados para o localStorage:', error);
            return {
                success: false,
                error: error.message
            };
        }
    },
    
    // Salvar histórico de simulações para um usuário
    saveSimulation: function(userId, simulation) {
        // Obter histórico de simulações do usuário
        const simulations = this.get(`simulations_${userId}`) || [];
        
        // Adicionar simulação atual ao histórico
        simulations.unshift(simulation);
        
        // Limitar a 20 simulações
        if (simulations.length > 20) {
            simulations.pop();
        }
        
        // Salvar no localStorage
        return this.set(`simulations_${userId}`, simulations);
    },
    
    // Obter histórico de simulações de um usuário
    getSimulations: function(userId) {
        return this.get(`simulations_${userId}`) || [];
    },
    
    // Remover uma simulação específica
    removeSimulation: function(userId, simulationId) {
        // Obter histórico de simulações do usuário
        const simulations = this.get(`simulations_${userId}`) || [];
        
        // Filtrar a simulação a ser removida
        const updatedSimulations = simulations.filter(sim => sim.id !== simulationId);
        
        // Se nenhuma simulação foi removida, retornar falso
        if (updatedSimulations.length === simulations.length) {
            return false;
        }
        
        // Salvar no localStorage
        return this.set(`simulations_${userId}`, updatedSimulations);
    }
};

// Inicializar módulo de armazenamento
(function() {
    // Verificar se o localStorage está disponível
    if (!TAXMASTER.storage.isAvailable()) {
        console.warn('localStorage não está disponível. Funcionalidades de armazenamento serão limitadas.');
    } else {
        console.log('Módulo de armazenamento inicializado com sucesso.');
    }
})();
