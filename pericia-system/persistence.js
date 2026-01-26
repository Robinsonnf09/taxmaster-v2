const fs = require('fs');
const path = require('path');

class DataPersistence {
    constructor() {
        this.dataDir = path.join(__dirname, 'data');
        this.usuariosFile = path.join(this.dataDir, 'usuarios.json');
        this.candidaturasFile = path.join(this.dataDir, 'candidaturas.json');
        this.notificacoesFile = path.join(this.dataDir, 'notificacoes.json');
        this.configFile = path.join(this.dataDir, 'config.json');
        
        this.ensureDataDir();
        this.initializeFiles();
    }
    
    ensureDataDir() {
        if (!fs.existsSync(this.dataDir)) {
            fs.mkdirSync(this.dataDir, { recursive: true });
            console.log('✓ Diretório de dados criado');
        }
    }
    
    initializeFiles() {
        // Usuários padrão
        if (!fs.existsSync(this.usuariosFile)) {
            const bcrypt = require('bcrypt');
            const usuariosPadrao = [
                {
                    id: 1,
                    nome: 'Admin Tax Master',
                    email: 'admin@taxmaster.com',
                    senha: bcrypt.hashSync('admin123', 10),
                    tipo: 'admin',
                    especialidades: ['Contábil', 'Tributária'],
                    telefone: '+5511999999999',
                    createdAt: new Date().toISOString()
                }
            ];
            this.saveUsuarios(usuariosPadrao);
            console.log('✓ Arquivo de usuários criado com admin padrão');
        }
        
        // Candidaturas
        if (!fs.existsSync(this.candidaturasFile)) {
            this.saveCandidaturas([]);
            console.log('✓ Arquivo de candidaturas criado');
        }
        
        // Notificações
        if (!fs.existsSync(this.notificacoesFile)) {
            this.saveNotificacoes([]);
            console.log('✓ Arquivo de notificações criado');
        }
        
        // Configurações
        if (!fs.existsSync(this.configFile)) {
            const configPadrao = {
                sistemaAtivo: true,
                versao: '2.5.0',
                ultimoScraper: null,
                totalOportunidades: 0,
                createdAt: new Date().toISOString()
            };
            this.saveConfig(configPadrao);
            console.log('✓ Arquivo de configurações criado');
        }
    }
    
    // USUÁRIOS
    loadUsuarios() {
        try {
            const data = fs.readFileSync(this.usuariosFile, 'utf-8');
            return JSON.parse(data);
        } catch (error) {
            console.error('Erro ao carregar usuários:', error.message);
            return [];
        }
    }
    
    saveUsuarios(usuarios) {
        try {
            fs.writeFileSync(this.usuariosFile, JSON.stringify(usuarios, null, 2), 'utf-8');
            return true;
        } catch (error) {
            console.error('Erro ao salvar usuários:', error.message);
            return false;
        }
    }
    
    addUsuario(usuario) {
        const usuarios = this.loadUsuarios();
        usuario.id = usuarios.length > 0 ? Math.max(...usuarios.map(u => u.id)) + 1 : 1;
        usuario.createdAt = new Date().toISOString();
        usuarios.push(usuario);
        this.saveUsuarios(usuarios);
        console.log(`✓ Usuário ${usuario.email} salvo permanentemente`);
        return usuario;
    }
    
    findUsuarioByEmail(email) {
        const usuarios = this.loadUsuarios();
        return usuarios.find(u => u.email === email);
    }
    
    // CANDIDATURAS
    loadCandidaturas() {
        try {
            const data = fs.readFileSync(this.candidaturasFile, 'utf-8');
            return JSON.parse(data);
        } catch (error) {
            console.error('Erro ao carregar candidaturas:', error.message);
            return [];
        }
    }
    
    saveCandidaturas(candidaturas) {
        try {
            fs.writeFileSync(this.candidaturasFile, JSON.stringify(candidaturas, null, 2), 'utf-8');
            return true;
        } catch (error) {
            console.error('Erro ao salvar candidaturas:', error.message);
            return false;
        }
    }
    
    addCandidatura(candidatura) {
        const candidaturas = this.loadCandidaturas();
        candidatura.id = candidaturas.length > 0 ? Math.max(...candidaturas.map(c => c.id)) + 1 : 1;
        candidatura.createdAt = new Date().toISOString();
        candidaturas.push(candidatura);
        this.saveCandidaturas(candidaturas);
        console.log(`✓ Candidatura ${candidatura.id} salva permanentemente`);
        return candidatura;
    }
    
    updateCandidatura(id, updates) {
        const candidaturas = this.loadCandidaturas();
        const index = candidaturas.findIndex(c => c.id === id);
        if (index !== -1) {
            candidaturas[index] = { ...candidaturas[index], ...updates, updatedAt: new Date().toISOString() };
            this.saveCandidaturas(candidaturas);
            console.log(`✓ Candidatura ${id} atualizada`);
            return candidaturas[index];
        }
        return null;
    }
    
    // NOTIFICAÇÕES
    loadNotificacoes() {
        try {
            const data = fs.readFileSync(this.notificacoesFile, 'utf-8');
            return JSON.parse(data);
        } catch (error) {
            console.error('Erro ao carregar notificações:', error.message);
            return [];
        }
    }
    
    saveNotificacoes(notificacoes) {
        try {
            fs.writeFileSync(this.notificacoesFile, JSON.stringify(notificacoes, null, 2), 'utf-8');
            return true;
        } catch (error) {
            console.error('Erro ao salvar notificações:', error.message);
            return false;
        }
    }
    
    addNotificacao(notificacao) {
        const notificacoes = this.loadNotificacoes();
        notificacao.id = notificacoes.length > 0 ? Math.max(...notificacoes.map(n => n.id)) + 1 : 1;
        notificacao.createdAt = new Date().toISOString();
        notificacao.lida = false;
        notificacoes.push(notificacao);
        this.saveNotificacoes(notificacoes);
        return notificacao;
    }
    
    // CONFIGURAÇÕES
    loadConfig() {
        try {
            const data = fs.readFileSync(this.configFile, 'utf-8');
            return JSON.parse(data);
        } catch (error) {
            console.error('Erro ao carregar configurações:', error.message);
            return {};
        }
    }
    
    saveConfig(config) {
        try {
            fs.writeFileSync(this.configFile, JSON.stringify(config, null, 2), 'utf-8');
            return true;
        } catch (error) {
            console.error('Erro ao salvar configurações:', error.message);
            return false;
        }
    }
    
    updateConfig(updates) {
        const config = this.loadConfig();
        const newConfig = { ...config, ...updates, updatedAt: new Date().toISOString() };
        this.saveConfig(newConfig);
        return newConfig;
    }
    
    // ESTATÍSTICAS
    getStats() {
        return {
            totalUsuarios: this.loadUsuarios().length,
            totalCandidaturas: this.loadCandidaturas().length,
            totalNotificacoes: this.loadNotificacoes().length,
            config: this.loadConfig()
        };
    }
}

module.exports = new DataPersistence();
