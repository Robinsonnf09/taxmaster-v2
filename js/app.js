// Arquivo principal da aplicaÃ§Ã£o TAX MASTER
// Inicializa todos os mÃ³dulos e configura o ambiente

// Garantir que o namespace global existe
var TAXMASTER = TAXMASTER || {};

// ConfiguraÃ§Ãµes globais
TAXMASTER.config = {
    version: "1.0.0",
    name: "TAX MASTER",
    description: "Plataforma de SimulaÃ§Ã£o TributÃ¡ria Interativa",
    debug: false
};

// InicializaÃ§Ã£o dos mÃ³dulos
TAXMASTER.modules = {
    // ReferÃªncias para os mÃ³dulos especÃ­ficos
    module1: null, // TransaÃ§Ã£o TributÃ¡ria BÃ¡sica
    module2: null, // TransaÃ§Ã£o TributÃ¡ria AvanÃ§ada
    module3: null, // Parcelamento e ReduÃ§Ã£o de DÃ©bitos
    module4: null, // Planejamento TributÃ¡rio EstratÃ©gico
    
    // Inicializar todos os mÃ³dulos
    init: function() {
        console.log("Inicializando mÃ³dulos do TAX MASTER");
        
        // Inicializar cada mÃ³dulo especÃ­fico
        if (TAXMASTER.modules.module1) TAXMASTER.modules.module1.init();
        if (TAXMASTER.modules.module2) TAXMASTER.modules.module2.init();
        if (TAXMASTER.modules.module3) TAXMASTER.modules.module3.init();
        if (TAXMASTER.modules.module4) TAXMASTER.modules.module4.init();
    }
};

// InicializaÃ§Ã£o da aplicaÃ§Ã£o
TAXMASTER.init = function() {
    console.log(`Inicializando ${TAXMASTER.config.name} v${TAXMASTER.config.version}`);
    
    // Verificar compatibilidade do navegador
    // [DESABILITADO]     if (!this.checkBrowserCompatibility()) {
    // [DESABILITADO]         console.error("Navegador incompatÃ­vel");
    // [DESABILITADO]         alert("Seu navegador nÃ£o Ã© compatÃ­vel com esta aplicaÃ§Ã£o. Por favor, utilize um navegador moderno como Chrome, Firefox, Edge ou Safari.");
    // [DESABILITADO]         return;
    }
    
    // Inicializar mÃ³dulos principais
    // Nota: A ordem Ã© importante devido Ã s dependÃªncias
    
    // 1. UtilitÃ¡rios (jÃ¡ inicializado automaticamente)
    
    // 2. UI (jÃ¡ inicializado automaticamente)
    
    // 3. Armazenamento
    if (TAXMASTER.storage) {
        // Verificar se localStorage estÃ¡ disponÃ­vel
        if (!TAXMASTER.storage.isAvailable()) {
            console.warn("localStorage nÃ£o estÃ¡ disponÃ­vel. Funcionalidades de armazenamento serÃ£o limitadas.");
            TAXMASTER.ui.notifications.show("Armazenamento local nÃ£o disponÃ­vel. Suas simulaÃ§Ãµes nÃ£o serÃ£o salvas.", "warning");
        }
    }
    
    // 4. AutenticaÃ§Ã£o (jÃ¡ inicializado automaticamente)
    
    // 5. RelatÃ³rios (jÃ¡ inicializado automaticamente)
    
    // 6. MÃ³dulos especÃ­ficos
    TAXMASTER.modules.init();
    
    // 7. Dashboard (se existir)
    if (TAXMASTER.dashboard) {
        TAXMASTER.dashboard.init();
    }
    
    // Registrar eventos globais
    this.registerGlobalEvents();
    
    console.log(`${TAXMASTER.config.name} inicializado com sucesso!`);
};

// Verificar compatibilidade do navegador
// [DESABILITADO] TAXMASTER.checkBrowserCompatibility = function() {
    // Verificar recursos essenciais
    const requiredFeatures = [
        'localStorage' in window,
        'fetch' in window,
        'Promise' in window,
        'Map' in window,
        'Array.prototype.forEach' in window
    ];
    
    return requiredFeatures.every(feature => feature === true);
};

// Registrar eventos globais
TAXMASTER.registerGlobalEvents = function() {
    // Evento de mudanÃ§a de hash na URL
    window.addEventListener('hashchange', function() {
        const hash = window.location.hash.substring(1);
        if (hash) {
            TAXMASTER.ui.showPage(hash);
        }
    });
    
    // Evento de tecla Escape para fechar modais
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(modal => {
                const modalId = modal.id;
                TAXMASTER.ui.modals.hide(modalId);
            });
        }
    });
    
    // Evento de beforeunload para avisar sobre dados nÃ£o salvos
    window.addEventListener('beforeunload', function(e) {
        // Verificar se hÃ¡ dados nÃ£o salvos
        if (TAXMASTER.hasUnsavedChanges) {
            const message = 'VocÃª tem alteraÃ§Ãµes nÃ£o salvas. Deseja realmente sair?';
            e.returnValue = message;
            return message;
        }
    });
};

// PÃ¡gina inicial
TAXMASTER.home = {
    init: function() {
        console.log("Inicializando pÃ¡gina inicial");
        
        // Registrar eventos da pÃ¡gina inicial
        this.registerEvents();
    },
    
    registerEvents: function() {
        // BotÃµes de "ComeÃ§ar agora" ou similares
        const startButtons = document.querySelectorAll('.start-button');
        startButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Verificar se usuÃ¡rio estÃ¡ autenticado
                if (TAXMASTER.auth.isAuthenticated()) {
                    // Redirecionar para dashboard
                    TAXMASTER.ui.showPage('dashboard');
                } else {
                    // Redirecionar para login
                    TAXMASTER.ui.showPage('login');
                }
            });
        });
    }
};

// Dashboard
TAXMASTER.dashboard = {
    init: function() {
        console.log("Inicializando dashboard");
        
        // Verificar autenticaÃ§Ã£o
        if (!TAXMASTER.auth.isAuthenticated()) {
            console.warn("Tentativa de acesso ao dashboard sem autenticaÃ§Ã£o");
            TAXMASTER.ui.showPage('login');
            return;
        }
        
        // Carregar dados do usuÃ¡rio
        this.loadUserData();
        
        // Carregar histÃ³rico de simulaÃ§Ãµes
        this.loadSimulationHistory();
        
        // Registrar eventos
        this.registerEvents();
    },
    
    loadUserData: function() {
        const user = TAXMASTER.auth.getCurrentUser();
        
        if (user) {
            // Atualizar elementos do dashboard com dados do usuÃ¡rio
            const welcomeMessage = document.getElementById('welcome-message');
            if (welcomeMessage) {
                welcomeMessage.textContent = `Bem-vindo, ${user.nome}!`;
            }
            
            // Atualizar estatÃ­sticas ou outros elementos personalizados
            this.updateUserStats(user);
        }
    },
    
    loadSimulationHistory: function() {
        const user = TAXMASTER.auth.getCurrentUser();
        
        if (user) {
            // Obter histÃ³rico de simulaÃ§Ãµes do usuÃ¡rio
            const simulations = TAXMASTER.storage.getSimulations(user.id);
            
            // Atualizar lista de simulaÃ§Ãµes recentes
            const historyContainer = document.getElementById('simulation-history');
            if (historyContainer && simulations.length > 0) {
                // Limpar conteÃºdo atual
                historyContainer.innerHTML = '';
                
                // Adicionar cada simulaÃ§Ã£o Ã  lista
                simulations.forEach(simulation => {
                    const item = document.createElement('div');
                    item.className = 'simulation-history-item';
                    
                    // Formatar data
                    const date = new Date(simulation.data);
                    const formattedDate = TAXMASTER.utils.formatDateTime(date);
                    
                    // Determinar Ã­cone com base no mÃ³dulo
                    let moduleIcon = 'fa-calculator';
                    let moduleName = 'SimulaÃ§Ã£o';
                    
                    switch (simulation.modulo) {
                        case 'module1':
                            moduleIcon = 'fa-file-invoice-dollar';
                            moduleName = 'TransaÃ§Ã£o TributÃ¡ria BÃ¡sica';
                            break;
                        case 'module2':
                            moduleIcon = 'fa-chart-line';
                            moduleName = 'TransaÃ§Ã£o TributÃ¡ria AvanÃ§ada';
                            break;
                        case 'module3':
                            moduleIcon = 'fa-money-bill-wave';
                            moduleName = 'Parcelamento e ReduÃ§Ã£o de DÃ©bitos';
                            break;
                        case 'module4':
                            moduleIcon = 'fa-chess';
                            moduleName = 'Planejamento TributÃ¡rio EstratÃ©gico';
                            break;
                    }
                    
                    // Criar HTML do item
                    item.innerHTML = `
                        <div class="simulation-history-details">
                            <h4><i class="fas ${moduleIcon}"></i> ${moduleName}</h4>
                            <p>Data: ${formattedDate}</p>
                            <p>Economia: ${TAXMASTER.utils.formatCurrency(simulation.resultados.economiaTotal || 0)}</p>
                        </div>
                        <div class="simulation-history-actions">
                            <button class="btn btn-primary btn-sm view-simulation" data-id="${simulation.id}" data-module="${simulation.modulo}">
                                <i class="fas fa-eye"></i> Ver
                            </button>
                            <button class="btn btn-secondary btn-sm export-simulation" data-id="${simulation.id}" data-module="${simulation.modulo}">
                                <i class="fas fa-file-export"></i> Exportar
                            </button>
                            <button class="btn btn-danger btn-sm delete-simulation" data-id="${simulation.id}">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    `;
                    
                    // Adicionar Ã  lista
                    historyContainer.appendChild(item);
                });
            } else if (historyContainer) {
                // Nenhuma simulaÃ§Ã£o encontrada
                historyContainer.innerHTML = '<p class="text-center">Nenhuma simulaÃ§Ã£o encontrada. Comece agora mesmo!</p>';
            }
        }
    },
    
    updateUserStats: function(user) {
        // Obter estatÃ­sticas do usuÃ¡rio
        const simulations = TAXMASTER.storage.getSimulations(user.id);
        
        // Calcular estatÃ­sticas
        const totalSimulations = simulations.length;
        let totalSavings = 0;
        let bestSaving = 0;
        let lastSimulationDate = null;
        
        simulations.forEach(simulation => {
            const savings = simulation.resultados.economiaTotal || 0;
            totalSavings += savings;
            
            if (savings > bestSaving) {
                bestSaving = savings;
            }
            
            const date = new Date(simulation.data);
            if (!lastSimulationDate || date > lastSimulationDate) {
                lastSimulationDate = date;
            }
        });
        
        // Atualizar elementos de estatÃ­sticas
        const statsElements = {
            'total-simulations': totalSimulations,
            'total-savings': TAXMASTER.utils.formatCurrency(totalSavings),
            'best-saving': TAXMASTER.utils.formatCurrency(bestSaving),
            'last-simulation': lastSimulationDate ? TAXMASTER.utils.formatDate(lastSimulationDate) : 'Nunca'
        };
        
        // Atualizar cada elemento
        Object.keys(statsElements).forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = statsElements[id];
            }
        });
    },
    
    registerEvents: function() {
        // DelegaÃ§Ã£o de eventos para botÃµes de histÃ³rico de simulaÃ§Ãµes
        document.addEventListener('click', function(e) {
            // BotÃ£o de visualizar simulaÃ§Ã£o
            if (e.target.closest('.view-simulation')) {
                const button = e.target.closest('.view-simulation');
                const simulationId = button.getAttribute('data-id');
                const moduleId = button.getAttribute('data-module');
                
                // Navegar para o mÃ³dulo correspondente
                TAXMASTER.ui.showPage(moduleId);
                
                // Carregar simulaÃ§Ã£o (apÃ³s navegaÃ§Ã£o)
                setTimeout(() => {
                    if (TAXMASTER.modules[moduleId] && TAXMASTER.modules[moduleId].loadSimulation) {
                        TAXMASTER.modules[moduleId].loadSimulation(simulationId);
                    }
                }, 500);
            }
            
            // BotÃ£o de exportar simulaÃ§Ã£o
            if (e.target.closest('.export-simulation')) {
                const button = e.target.closest('.export-simulation');
                const simulationId = button.getAttribute('data-id');
                const moduleId = button.getAttribute('data-module');
                
                // Mostrar modal de exportaÃ§Ã£o
                const exportModal = document.getElementById('export-modal');
                if (exportModal) {
                    // Atualizar atributos do modal
                    const exportButtons = exportModal.querySelectorAll('.export-btn');
                    exportButtons.forEach(btn => {
                        btn.setAttribute('data-simulation', simulationId);
                        btn.setAttribute('data-module', moduleId);
                    });
                    
                    // Mostrar modal
                    TAXMASTER.ui.modals.show('export-modal');
                } else {
                    // Fallback se o modal nÃ£o existir
                    TAXMASTER.ui.notifications.show('Funcionalidade de exportaÃ§Ã£o nÃ£o disponÃ­vel', 'error');
                }
            }
            
            // BotÃ£o de excluir simulaÃ§Ã£o
            if (e.target.closest('.delete-simulation')) {
                const button = e.target.closest('.delete-simulation');
                const simulationId = button.getAttribute('data-id');
                
                // Confirmar exclusÃ£o
                if (confirm('Tem certeza que deseja excluir esta simulaÃ§Ã£o? Esta aÃ§Ã£o nÃ£o pode ser desfeita.')) {
                    // Excluir simulaÃ§Ã£o
                    const user = TAXMASTER.auth.getCurrentUser();
                    if (user && TAXMASTER.storage.removeSimulation(user.id, simulationId)) {
                        // Atualizar lista
                        TAXMASTER.dashboard.loadSimulationHistory();
                        // Atualizar estatÃ­sticas
                        TAXMASTER.dashboard.updateUserStats(user);
                        // Notificar usuÃ¡rio
                        TAXMASTER.ui.notifications.show('SimulaÃ§Ã£o excluÃ­da com sucesso', 'success');
                    } else {
                        TAXMASTER.ui.notifications.show('Erro ao excluir simulaÃ§Ã£o', 'error');
                    }
                }
            }
            
            // BotÃµes de mÃ³dulos no dashboard
            if (e.target.closest('.module-card')) {
                const card = e.target.closest('.module-card');
                const moduleId = card.getAttribute('data-module');
                
                if (moduleId) {
                    TAXMASTER.ui.showPage(moduleId);
                }
            }
        });
    }
};

// Inicializar aplicaÃ§Ã£o quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    TAXMASTER.init();
});
