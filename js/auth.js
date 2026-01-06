// Módulo de autenticação para o TAX MASTER
// Implementa funções para login, registro e gerenciamento de usuários

TAXMASTER.auth = {
    // Usuário atual
    currentUser: null,
    
    // Inicialização do módulo
    init: function() {
        console.log('Inicializando módulo de autenticação');
        
        // Verificar se há usuário logado
        this.checkLoggedInUser();
        
        // Registrar eventos
        this.registerEvents();
    },
    
    // Verificar se há usuário logado
    checkLoggedInUser: function() {
        try {
            // Verificar se há token de autenticação
            const token = localStorage.getItem('taxmaster_auth_token');
            
            if (token) {
                // Decodificar token (simplificado para versão estática)
                const userData = JSON.parse(atob(token.split('.')[1]));
                
                // Verificar validade do token
                if (userData.exp > Date.now() / 1000) {
                    // Token válido, definir usuário atual
                    this.currentUser = {
                        id: userData.id,
                        nome: userData.nome,
                        email: userData.email,
                        perfil: userData.perfil,
                        token: token
                    };
                    
                    // Atualizar UI
                    this.updateUI();
                    
                    return true;
                } else {
                    // Token expirado, remover
                    localStorage.removeItem('taxmaster_auth_token');
                }
            }
            
            // Nenhum usuário logado
            this.currentUser = null;
            this.updateUI();
            return false;
        } catch (error) {
            console.error('Erro ao verificar usuário logado:', error);
            this.currentUser = null;
            this.updateUI();
            return false;
        }
    },
    
    // Registrar eventos
    registerEvents: function() {
        // Formulário de login
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                
                const email = document.getElementById('login-email').value;
                const senha = document.getElementById('login-senha').value;
                
                this.login(email, senha);
            });
        }
        
        // Formulário de registro
        const registerForm = document.getElementById('register-form');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => {
                e.preventDefault();
                
                const nome = document.getElementById('register-nome').value;
                const email = document.getElementById('register-email').value;
                const senha = document.getElementById('register-senha').value;
                const perfil = document.getElementById('register-perfil').value;
                
                this.register(nome, email, senha, perfil);
            });
        }
        
        // Botão de logout
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.logout();
            });
        }
    },
    
    // Login de usuário
    login: function(email, senha) {
        try {
            // Validar campos
            if (!email || !senha) {
                TAXMASTER.ui.notifications.show('Por favor, preencha todos os campos', 'error');
                return false;
            }
            
            // Verificar usuários cadastrados (simulado para versão estática)
            const users = JSON.parse(localStorage.getItem('taxmaster_users') || '[]');
            
            // Buscar usuário
            const user = users.find(u => u.email === email);
            
            if (!user) {
                TAXMASTER.ui.notifications.show('Usuário não encontrado', 'error');
                return false;
            }
            
            // Verificar senha (simplificado para versão estática)
            if (user.senha !== senha) {
                TAXMASTER.ui.notifications.show('Senha incorreta', 'error');
                return false;
            }
            
            // Gerar token (simplificado para versão estática)
            const now = Math.floor(Date.now() / 1000);
            const payload = {
                id: user.id,
                nome: user.nome,
                email: user.email,
                perfil: user.perfil,
                iat: now,
                exp: now + 86400 // 24 horas
            };
            
            const token = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.${btoa(JSON.stringify(payload))}.signature`;
            
            // Salvar token
            localStorage.setItem('taxmaster_auth_token', token);
            
            // Definir usuário atual
            this.currentUser = {
                id: user.id,
                nome: user.nome,
                email: user.email,
                perfil: user.perfil,
                token: token
            };
            
            // Atualizar UI
            this.updateUI();
            
            // Notificar usuário
            TAXMASTER.ui.notifications.show(`Bem-vindo, ${user.nome}!`, 'success');
            
            // Redirecionar para dashboard
            TAXMASTER.ui.showPage('dashboard');
            
            return true;
        } catch (error) {
            console.error('Erro ao fazer login:', error);
            TAXMASTER.ui.notifications.show('Erro ao fazer login', 'error');
            return false;
        }
    },
    
    // Registro de usuário
    register: function(nome, email, senha, perfil) {
        try {
            // Validar campos
            if (!nome || !email || !senha || !perfil) {
                TAXMASTER.ui.notifications.show('Por favor, preencha todos os campos', 'error');
                return false;
            }
            
            // Verificar usuários cadastrados (simulado para versão estática)
            const users = JSON.parse(localStorage.getItem('taxmaster_users') || '[]');
            
            // Verificar se email já existe
            if (users.some(u => u.email === email)) {
                TAXMASTER.ui.notifications.show('Este email já está cadastrado', 'error');
                return false;
            }
            
            // Gerar ID único
            const id = 'user_' + Date.now();
            
            // Criar novo usuário
            const newUser = {
                id: id,
                nome: nome,
                email: email,
                senha: senha,
                perfil: perfil,
                dataCadastro: new Date().toISOString()
            };
            
            // Adicionar à lista de usuários
            users.push(newUser);
            
            // Salvar lista atualizada
            localStorage.setItem('taxmaster_users', JSON.stringify(users));
            
            // Fazer login automático
            this.login(email, senha);
            
            return true;
        } catch (error) {
            console.error('Erro ao registrar usuário:', error);
            TAXMASTER.ui.notifications.show('Erro ao registrar usuário', 'error');
            return false;
        }
    },
    
    // Logout de usuário
    logout: function() {
        try {
            // Remover token
            localStorage.removeItem('taxmaster_auth_token');
            
            // Limpar usuário atual
            this.currentUser = null;
            
            // Atualizar UI
            this.updateUI();
            
            // Notificar usuário
            TAXMASTER.ui.notifications.show('Logout realizado com sucesso', 'success');
            
            // Redirecionar para página inicial
            TAXMASTER.ui.showPage('home');
            
            return true;
        } catch (error) {
            console.error('Erro ao fazer logout:', error);
            TAXMASTER.ui.notifications.show('Erro ao fazer logout', 'error');
            return false;
        }
    },
    
    // Atualizar UI com base no estado de autenticação
    updateUI: function() {
        try {
            // Elementos de UI
            const loginSection = document.getElementById('login-section');
            const userSection = document.getElementById('user-section');
            const userNameElement = document.getElementById('user-name');
            const userProfileElement = document.getElementById('user-profile');
            const authRequiredElements = document.querySelectorAll('.auth-required');
            const guestOnlyElements = document.querySelectorAll('.guest-only');
            
            if (this.currentUser) {
                // Usuário logado
                if (loginSection) loginSection.style.display = 'none';
                if (userSection) userSection.style.display = 'block';
                if (userNameElement) userNameElement.textContent = this.currentUser.nome;
                if (userProfileElement) userProfileElement.textContent = this.currentUser.perfil;
                
                // Mostrar elementos que requerem autenticação
                authRequiredElements.forEach(el => {
                    el.style.display = '';
                });
                
                // Ocultar elementos apenas para visitantes
                guestOnlyElements.forEach(el => {
                    el.style.display = 'none';
                });
                
                // Verificar elementos específicos para perfil
                const profileElements = document.querySelectorAll(`[data-profile]`);
                profileElements.forEach(el => {
                    const profiles = el.getAttribute('data-profile').split(',');
                    if (profiles.includes(this.currentUser.perfil)) {
                        el.style.display = '';
                    } else {
                        el.style.display = 'none';
                    }
                });
            } else {
                // Usuário não logado
                if (loginSection) loginSection.style.display = 'block';
                if (userSection) userSection.style.display = 'none';
                
                // Ocultar elementos que requerem autenticação
                authRequiredElements.forEach(el => {
                    el.style.display = 'none';
                });
                
                // Mostrar elementos apenas para visitantes
                guestOnlyElements.forEach(el => {
                    el.style.display = '';
                });
                
                // Ocultar elementos específicos para perfil
                const profileElements = document.querySelectorAll(`[data-profile]`);
                profileElements.forEach(el => {
                    el.style.display = 'none';
                });
            }
        } catch (error) {
            console.error('Erro ao atualizar UI de autenticação:', error);
        }
    },
    
    // Verificar se usuário está autenticado
    isAuthenticated: function() {
        return this.currentUser !== null;
    },
    
    // Obter usuário atual
    getCurrentUser: function() {
        return this.currentUser;
    },
    
    // Verificar se usuário tem perfil específico
    hasProfile: function(profile) {
        if (!this.currentUser) return false;
        return this.currentUser.perfil === profile;
    },
    
    // Criar usuários de demonstração
    createDemoUsers: function() {
        try {
            // Verificar se já existem usuários
            const users = JSON.parse(localStorage.getItem('taxmaster_users') || '[]');
            
            if (users.length === 0) {
                // Criar usuários de demonstração
                const demoUsers = [
                    {
                        id: 'user_contador',
                        nome: 'Contador Demonstração',
                        email: 'contador@exemplo.com',
                        senha: 'contador123',
                        perfil: 'contador',
                        dataCadastro: new Date().toISOString()
                    },
                    {
                        id: 'user_advogado',
                        nome: 'Advogado Demonstração',
                        email: 'advogado@exemplo.com',
                        senha: 'advogado123',
                        perfil: 'advogado',
                        dataCadastro: new Date().toISOString()
                    },
                    {
                        id: 'user_gestor',
                        nome: 'Gestor Demonstração',
                        email: 'gestor@exemplo.com',
                        senha: 'gestor123',
                        perfil: 'gestor',
                        dataCadastro: new Date().toISOString()
                    }
                ];
                
                // Salvar usuários de demonstração
                localStorage.setItem('taxmaster_users', JSON.stringify(demoUsers));
                
                console.log('Usuários de demonstração criados com sucesso');
                return true;
            }
            
            return false;
        } catch (error) {
            console.error('Erro ao criar usuários de demonstração:', error);
            return false;
        }
    }
};

// Inicializar módulo de autenticação
(function() {
    // Criar usuários de demonstração
    TAXMASTER.auth.createDemoUsers();
    
    // Inicializar módulo
    TAXMASTER.auth.init();
    
    console.log('Módulo de autenticação inicializado com sucesso');
})();
