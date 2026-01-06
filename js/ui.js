// Módulo de interface do usuário (UI) para o TAX MASTER
// Gerencia a navegação entre páginas, notificações, modais e atualizações do DOM

TAXMASTER.ui = {
    // Elemento principal onde o conteúdo da página é carregado
    mainContentElement: document.getElementById("main-content"),
    
    // Cache de templates HTML
    templates: {},
    
    // Inicialização do módulo
    init: function() {
        console.log("Inicializando módulo de UI");
        
        // Registrar eventos de navegação
        this.registerNavigationEvents();
        
        // Carregar página inicial
        this.loadInitialPage();
    },
    
    // Registrar eventos de navegação
    registerNavigationEvents: function() {
        document.addEventListener("click", (e) => {
            // Verificar se é um link de navegação interno
            const link = e.target.closest("a[data-page]");
            if (link) {
                e.preventDefault();
                const pageId = link.getAttribute("data-page");
                this.showPage(pageId);
            }
        });
    },
    
    // Carregar página inicial
    loadInitialPage: function() {
        // Verificar se há hash na URL
        const hash = window.location.hash.substring(1);
        
        if (hash) {
            this.showPage(hash);
        } else {
            // Carregar página inicial padrão (home)
            this.showPage("home");
        }
    },
    
    // Mostrar página específica
    showPage: function(pageId) {
        console.log(`Navegando para a página: ${pageId}`);
        
        // Verificar se o usuário tem permissão para acessar a página
        if (!this.checkPagePermissions(pageId)) {
            console.warn(`Acesso negado à página: ${pageId}`);
            this.notifications.show("Você não tem permissão para acessar esta página.", "error");
            // Redirecionar para página de login ou home
            this.showPage(TAXMASTER.auth.isAuthenticated() ? "dashboard" : "login");
            return;
        }
        
        // Carregar template HTML da página
        this.loadTemplate(pageId)
            .then(html => {
                // Inserir HTML no elemento principal
                this.mainContentElement.innerHTML = html;
                
                // Atualizar URL hash
                window.location.hash = pageId;
                
                // Atualizar links ativos na navegação
                this.updateActiveNavLinks(pageId);
                
                // Executar função de inicialização da página (se existir)
                this.initializePage(pageId);
                
                // Aplicar animação
                this.mainContentElement.classList.add("fade-in");
                setTimeout(() => {
                    this.mainContentElement.classList.remove("fade-in");
                }, 500);
            })
            .catch(error => {
                console.error(`Erro ao carregar página ${pageId}:`, error);
                this.mainContentElement.innerHTML = `<div class="alert alert-danger">Erro ao carregar a página. Tente novamente mais tarde.</div>`;
            });
    },
    
    // Verificar permissões da página
    checkPagePermissions: function(pageId) {
        const pageElement = document.querySelector(`a[data-page="${pageId}"]`);
        
        // Se não houver link, permitir acesso (páginas como home)
        if (!pageElement) return true;
        
        const parentLi = pageElement.closest("li");
        
        // Verificar se requer autenticação
        if (parentLi && parentLi.classList.contains("auth-required") && !TAXMASTER.auth.isAuthenticated()) {
            return false;
        }
        
        // Verificar se é apenas para visitantes
        if (parentLi && parentLi.classList.contains("guest-only") && TAXMASTER.auth.isAuthenticated()) {
            return false;
        }
        
        // Verificar permissões de perfil
        const requiredProfile = parentLi ? parentLi.getAttribute("data-profile") : null;
        if (requiredProfile && !TAXMASTER.auth.hasProfile(requiredProfile)) {
            return false;
        }
        
        return true;
    },
    
    // Carregar template HTML da página
    loadTemplate: function(pageId) {
        return new Promise((resolve, reject) => {
            // Verificar cache
            if (this.templates[pageId]) {
                resolve(this.templates[pageId]);
                return;
            }
            
            // Construir caminho do arquivo HTML
            const filePath = `modules/${pageId}.html`;
            
            // Buscar arquivo HTML
            fetch(filePath)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Erro ao buscar ${filePath}: ${response.statusText}`);
                    }
                    return response.text();
                })
                .then(html => {
                    // Armazenar no cache
                    this.templates[pageId] = html;
                    resolve(html);
                })
                .catch(error => {
                    console.error(`Erro ao carregar template ${pageId}:`, error);
                    // Tentar carregar template de erro
                    if (pageId !== "error") {
                        this.loadTemplate("error").then(resolve).catch(reject);
                    } else {
                        reject(error);
                    }
                });
        });
    },
    
    // Atualizar links ativos na navegação
    updateActiveNavLinks: function(pageId) {
        const navLinks = document.querySelectorAll("nav ul li a");
        navLinks.forEach(link => {
            if (link.getAttribute("data-page") === pageId) {
                link.parentElement.classList.add("active");
            } else {
                link.parentElement.classList.remove("active");
            }
        });
    },
    
    // Executar função de inicialização da página
    initializePage: function(pageId) {
        // Mapear pageId para módulo/função de inicialização
        const initFunctions = {
            "home": TAXMASTER.home ? TAXMASTER.home.init : null,
            "login": TAXMASTER.auth ? TAXMASTER.auth.initLoginPage : null,
            "register": TAXMASTER.auth ? TAXMASTER.auth.initRegisterPage : null,
            "dashboard": TAXMASTER.dashboard ? TAXMASTER.dashboard.init : null,
            "module1": TAXMASTER.modules.module1 ? TAXMASTER.modules.module1.init : null,
            "module2": TAXMASTER.modules.module2 ? TAXMASTER.modules.module2.init : null,
            "module3": TAXMASTER.modules.module3 ? TAXMASTER.modules.module3.init : null,
            "module4": TAXMASTER.modules.module4 ? TAXMASTER.modules.module4.init : null,
            // Adicionar outras páginas aqui
        };
        
        // Executar função se existir
        if (initFunctions[pageId] && typeof initFunctions[pageId] === "function") {
            try {
                initFunctions[pageId]();
                console.log(`Página ${pageId} inicializada com sucesso.`);
            } catch (error) {
                console.error(`Erro ao inicializar página ${pageId}:`, error);
            }
        }
    },
    
    // Módulo de notificações
    notifications: {
        container: null,
        
        init: function() {
            // Criar container de notificações se não existir
            if (!this.container) {
                this.container = document.createElement("div");
                this.container.id = "notification-container";
                document.body.appendChild(this.container);
            }
        },
        
        show: function(message, type = "info", duration = 5000) {
            // Inicializar container se necessário
            if (!this.container) this.init();
            
            // Criar elemento de notificação
            const notification = document.createElement("div");
            notification.className = `notification notification-${type}`;
            notification.textContent = message;
            
            // Adicionar ao container
            this.container.appendChild(notification);
            
            // Forçar reflow para aplicar animação
            notification.offsetHeight;
            
            // Mostrar notificação
            notification.classList.add("show");
            
            // Remover após duração
            setTimeout(() => {
                notification.classList.remove("show");
                // Remover do DOM após animação
                setTimeout(() => {
                    if (this.container.contains(notification)) {
                        this.container.removeChild(notification);
                    }
                }, 300);
            }, duration);
        }
    },
    
    // Módulo de modais
    modals: {
        show: function(modalId) {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.add("show");
                // Adicionar listener para fechar
                modal.querySelector(".modal-close").addEventListener("click", () => this.hide(modalId));
                modal.addEventListener("click", (e) => {
                    if (e.target === modal) {
                        this.hide(modalId);
                    }
                });
            }
        },
        
        hide: function(modalId) {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.remove("show");
            }
        }
    },
    
    // Exibir estado de carregamento
    showLoading: function(element) {
        if (element) {
            element.disabled = true;
            element.innerHTML = 
                `<span class="loading-spinner" role="status" aria-hidden="true"></span> Carregando...`;
        }
    },
    
    // Ocultar estado de carregamento
    hideLoading: function(element, originalText) {
        if (element) {
            element.disabled = false;
            element.innerHTML = originalText;
        }
    }
};

// Inicializar módulo de UI
(function() {
    TAXMASTER.ui.init();
    TAXMASTER.ui.notifications.init();
    console.log("Módulo de UI inicializado com sucesso");
})();
