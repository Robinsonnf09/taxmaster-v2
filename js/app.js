// Arquivo principal da aplicação TAX MASTER
// Inicializa todos os módulos e configura o ambiente

// Garantir que o namespace global existe
var TAXMASTER = TAXMASTER || {};

// Configurações globais
TAXMASTER.config = {
    version: "1.0.0",
    name: "TAX MASTER",
    description: "Plataforma de Simulação Tributária Interativa",
    debug: false
};

// Inicialização dos módulos
TAXMASTER.modules = {
    // Referências para os módulos específicos
    module1: null, // Transação Tributária Básica
    module2: null, // Transação Tributária Avançada
    module3: null, // Parcelamento e Redução de Débitos
    module4: null, // Planejamento Tributário Estratégico
    
    // Inicializar todos os módulos
    init: function() {
        console.log("Inicializando módulos do TAX MASTER");
        
        // Inicializar cada módulo específico
        if (TAXMASTER.modules.module1) TAXMASTER.modules.module1.init();
        if (TAXMASTER.modules.module2) TAXMASTER.modules.module2.init();
        if (TAXMASTER.modules.module3) TAXMASTER.modules.module3.init();
        if (TAXMASTER.modules.module4) TAXMASTER.modules.module4.init();
    }
};

// Inicialização da aplicação
TAXMASTER.init = function() {
    console.log(`Inicializando ${TAXMASTER.config.name} v${TAXMASTER.config.version}`);
    
    // Verificar compatibilidade do navegador
    if (!this.checkBrowserCompatibility()) {
        console.error("Navegador incompatível");
        alert("Seu navegador não é compatível com esta aplicação. Por favor, utilize um navegador moderno como Chrome, Firefox, Edge ou Safari.");
        return;
    }
    
    // Inicializar módulos principais
    // Nota: A ordem é importante devido às dependências
    
    // 1. Utilitários (já inicializado automaticamente)
    
    // 2. UI (já inicializado automaticamente)
    
    // 3. Armazenamento
    if (TAXMASTER.storage) {
        // Verificar se localStorage está disponível
        if (!TAXMASTER.storage.isAvailable()) {
            console.warn("localStorage não está disponível. Funcionalidades de armazenamento serão limitadas.");
            TAXMASTER.ui.notifications.show("Armazenamento local não disponível. Suas simulações não serão salvas.", "warning");
        }
    }
    
    // 4. Autenticação (já inicializado automaticamente)
    
    // 5. Relatórios (já inicializado automaticamente)
    
    // 6. Módulos específicos
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
TAXMASTER.checkBrowserCompatibility = function() {
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
    // Evento de mudança de hash na URL
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
    
    // Evento de beforeunload para avisar sobre dados não salvos
    window.addEventListener('beforeunload', function(e) {
        // Verificar se há dados não salvos
        if (TAXMASTER.hasUnsavedChanges) {
            const message = 'Você tem alterações não salvas. Deseja realmente sair?';
            e.returnValue = message;
            return message;
        }
    });
};

// Página inicial
TAXMASTER.home = {
    init: function() {
        console.log("Inicializando página inicial");
        
        // Registrar eventos da página inicial
        this.registerEvents();
    },
    
    registerEvents: function() {
        // Botões de "Começar agora" ou similares
        const startButtons = document.querySelectorAll('.start-button');
        startButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Verificar se usuário está autenticado
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
        
        // Verificar autenticação
        if (!TAXMASTER.auth.isAuthenticated()) {
            console.warn("Tentativa de acesso ao dashboard sem autenticação");
            TAXMASTER.ui.showPage('login');
            return;
        }
        
        // Carregar dados do usuário
        this.loadUserData();
        
        // Carregar histórico de simulações
        this.loadSimulationHistory();
        
        // Registrar eventos
        this.registerEvents();
    },
    
    loadUserData: function() {
        const user = TAXMASTER.auth.getCurrentUser();
        
        if (user) {
            // Atualizar elementos do dashboard com dados do usuário
            const welcomeMessage = document.getElementById('welcome-message');
            if (welcomeMessage) {
                welcomeMessage.textContent = `Bem-vindo, ${user.nome}!`;
            }
            
            // Atualizar estatísticas ou outros elementos personalizados
            this.updateUserStats(user);
        }
    },
    
    loadSimulationHistory: function() {
        const user = TAXMASTER.auth.getCurrentUser();
        
        if (user) {
            // Obter histórico de simulações do usuário
            const simulations = TAXMASTER.storage.getSimulations(user.id);
            
            // Atualizar lista de simulações recentes
            const historyContainer = document.getElementById('simulation-history');
            if (historyContainer && simulations.length > 0) {
                // Limpar conteúdo atual
                historyContainer.innerHTML = '';
                
                // Adicionar cada simulação à lista
                simulations.forEach(simulation => {
                    const item = document.createElement('div');
                    item.className = 'simulation-history-item';
                    
                    // Formatar data
                    const date = new Date(simulation.data);
                    const formattedDate = TAXMASTER.utils.formatDateTime(date);
                    
                    // Determinar ícone com base no módulo
                    let moduleIcon = 'fa-calculator';
                    let moduleName = 'Simulação';
                    
                    switch (simulation.modulo) {
                        case 'module1':
                            moduleIcon = 'fa-file-invoice-dollar';
                            moduleName = 'Transação Tributária Básica';
                            break;
                        case 'module2':
                            moduleIcon = 'fa-chart-line';
                            moduleName = 'Transação Tributária Avançada';
                            break;
                        case 'module3':
                            moduleIcon = 'fa-money-bill-wave';
                            moduleName = 'Parcelamento e Redução de Débitos';
                            break;
                        case 'module4':
                            moduleIcon = 'fa-chess';
                            moduleName = 'Planejamento Tributário Estratégico';
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
                    
                    // Adicionar à lista
                    historyContainer.appendChild(item);
                });
            } else if (historyContainer) {
                // Nenhuma simulação encontrada
                historyContainer.innerHTML = '<p class="text-center">Nenhuma simulação encontrada. Comece agora mesmo!</p>';
            }
        }
    },
    
    updateUserStats: function(user) {
        // Obter estatísticas do usuário
        const simulations = TAXMASTER.storage.getSimulations(user.id);
        
        // Calcular estatísticas
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
        
        // Atualizar elementos de estatísticas
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
        // Delegação de eventos para botões de histórico de simulações
        document.addEventListener('click', function(e) {
            // Botão de visualizar simulação
            if (e.target.closest('.view-simulation')) {
                const button = e.target.closest('.view-simulation');
                const simulationId = button.getAttribute('data-id');
                const moduleId = button.getAttribute('data-module');
                
                // Navegar para o módulo correspondente
                TAXMASTER.ui.showPage(moduleId);
                
                // Carregar simulação (após navegação)
                setTimeout(() => {
                    if (TAXMASTER.modules[moduleId] && TAXMASTER.modules[moduleId].loadSimulation) {
                        TAXMASTER.modules[moduleId].loadSimulation(simulationId);
                    }
                }, 500);
            }
            
            // Botão de exportar simulação
            if (e.target.closest('.export-simulation')) {
                const button = e.target.closest('.export-simulation');
                const simulationId = button.getAttribute('data-id');
                const moduleId = button.getAttribute('data-module');
                
                // Mostrar modal de exportação
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
                    // Fallback se o modal não existir
                    TAXMASTER.ui.notifications.show('Funcionalidade de exportação não disponível', 'error');
                }
            }
            
            // Botão de excluir simulação
            if (e.target.closest('.delete-simulation')) {
                const button = e.target.closest('.delete-simulation');
                const simulationId = button.getAttribute('data-id');
                
                // Confirmar exclusão
                if (confirm('Tem certeza que deseja excluir esta simulação? Esta ação não pode ser desfeita.')) {
                    // Excluir simulação
                    const user = TAXMASTER.auth.getCurrentUser();
                    if (user && TAXMASTER.storage.removeSimulation(user.id, simulationId)) {
                        // Atualizar lista
                        TAXMASTER.dashboard.loadSimulationHistory();
                        // Atualizar estatísticas
                        TAXMASTER.dashboard.updateUserStats(user);
                        // Notificar usuário
                        TAXMASTER.ui.notifications.show('Simulação excluída com sucesso', 'success');
                    } else {
                        TAXMASTER.ui.notifications.show('Erro ao excluir simulação', 'error');
                    }
                }
            }
            
            // Botões de módulos no dashboard
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

// Inicializar aplicação quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    TAXMASTER.init();
});
