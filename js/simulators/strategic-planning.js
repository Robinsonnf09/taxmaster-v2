// Simulador de Planejamento Tributário Estratégico para o TAX MASTER - Módulo IV
// Implementa projeções de longo prazo e análise de cenários econômicos

TAXMASTER.modules.module4 = {
    // Inicialização do módulo
    init: function() {
        console.log('Inicializando Módulo IV - Planejamento Tributário Estratégico');
        
        // Inicializar simulador
        this.simulator.init();
        
        // Configurar formulário de simulação
        this.setupForm();
        
        // Configurar tabs
        this.setupTabs();
        
        // Disparar evento de módulo inicializado
        TAXMASTER.events.trigger('module:initialized', { module: 'module4' });
    },
    
    // Configurar formulário de simulação
    setupForm: function() {
        const form = document.getElementById('strategic-planning-form');
        if (!form) return;
        
        // Configurar evento de submit
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            // Validar formulário
            if (!TAXMASTER.ui.forms.validate(form)) {
                return;
            }
            
            // Obter dados do formulário
            const formData = TAXMASTER.ui.forms.serialize(form);
            
            // Executar simulação
            try {
                const results = this.simulator.simulate(formData);
                this.displayResults(results);
            } catch (error) {
                TAXMASTER.ui.notifications.show(error.message, 'error');
            }
        });
        
        // Configurar evento de reset
        form.addEventListener('reset', () => {
            this.hideResults();
        });
        
        // Configurar seleção de cenário econômico
        const scenarioSelect = form.querySelector('#cenario_economico');
        if (scenarioSelect) {
            scenarioSelect.addEventListener('change', () => {
                this.updateFormFields(scenarioSelect.value);
            });
            
            // Inicializar campos com cenário padrão
            this.updateFormFields(scenarioSelect.value);
        }
        
        // Configurar seleção de horizonte de planejamento
        const horizonSelect = form.querySelector('#horizonte_planejamento');
        if (horizonSelect) {
            horizonSelect.addEventListener('change', () => {
                this.updateHorizonFields(horizonSelect.value);
            });
            
            // Inicializar campos com horizonte padrão
            this.updateHorizonFields(horizonSelect.value);
        }
    },
    
    // Atualizar campos do formulário com base no cenário econômico selecionado
    updateFormFields: function(scenario) {
        const config = this.simulator.getScenarioConfig(scenario);
        if (!config) return;
        
        // Atualizar campos com valores do cenário
        const form = document.getElementById('strategic-planning-form');
        
        // Atualizar taxa de crescimento
        const taxaCrescimentoField = form.querySelector('#taxa_crescimento');
        if (taxaCrescimentoField) {
            taxaCrescimentoField.value = config.taxaCrescimento * 100;
        }
        
        // Atualizar taxa de inflação
        const taxaInflacaoField = form.querySelector('#taxa_inflacao');
        if (taxaInflacaoField) {
            taxaInflacaoField.value = config.taxaInflacao * 100;
        }
        
        // Atualizar taxa de juros
        const taxaJurosField = form.querySelector('#taxa_juros');
        if (taxaJurosField) {
            taxaJurosField.value = config.taxaJuros * 100;
        }
        
        // Atualizar informações do cenário
        const scenarioInfo = document.getElementById('scenario-info');
        if (scenarioInfo) {
            scenarioInfo.innerHTML = `
                <p>Parâmetros para cenário <strong>${scenario}</strong>:</p>
                <ul>
                    <li>Taxa de crescimento anual: ${(config.taxaCrescimento * 100).toFixed(2)}%</li>
                    <li>Taxa de inflação anual: ${(config.taxaInflacao * 100).toFixed(2)}%</li>
                    <li>Taxa de juros anual: ${(config.taxaJuros * 100).toFixed(2)}%</li>
                    <li>Risco econômico: ${config.riscoEconomico}</li>
                </ul>
                <p><small>${config.descricao}</small></p>
            `;
        }
    },
    
    // Atualizar campos do formulário com base no horizonte de planejamento
    updateHorizonFields: function(horizon) {
        const horizonYears = parseInt(horizon);
        
        // Atualizar informações do horizonte
        const horizonInfo = document.getElementById('horizon-info');
        if (horizonInfo) {
            horizonInfo.innerHTML = `
                <p>Horizonte de planejamento: <strong>${horizonYears} anos</strong></p>
                <p><small>As projeções serão calculadas para um período de ${horizonYears} anos, com detalhamento anual.</small></p>
            `;
        }
    },
    
    // Configurar tabs
    setupTabs: function() {
        const tabsContainer = document.querySelector('.tabs');
        if (!tabsContainer) return;
        
        const tabs = tabsContainer.querySelectorAll('.tab');
        const tabContents = document.querySelectorAll('.tab-content');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Remover classe active de todas as tabs
                tabs.forEach(t => t.classList.remove('active'));
                
                // Adicionar classe active à tab clicada
                tab.classList.add('active');
                
                // Mostrar conteúdo correspondente
                const target = tab.getAttribute('data-target');
                tabContents.forEach(content => {
                    content.classList.remove('active');
                    if (content.id === target) {
                        content.classList.add('active');
                    }
                });
            });
        });
    },
    
    // Exibir resultados da simulação
    displayResults: function(results) {
        const resultsContainer = document.getElementById('simulation-results');
        if (!resultsContainer) return;
        
        // Mostrar container de resultados
        resultsContainer.classList.add('active');
        
        // Preencher resultados básicos
        const summaryContainer = document.getElementById('results-summary');
        if (summaryContainer) {
            summaryContainer.innerHTML = `
                <div class="result-item">
                    <span class="result-label">Cenário Econômico:</span>
                    <span class="result-value">${results.cenarioEconomico}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Horizonte de Planejamento:</span>
                    <span class="result-value">${results.horizontePlanejamento} anos</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Faturamento Anual Inicial:</span>
                    <span class="result-value">${TAXMASTER.utils.formatCurrency(results.faturamentoAnual)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Regime Tributário Atual:</span>
                    <span class="result-value">${results.regimeTributarioAtual}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Regime Tributário Recomendado:</span>
                    <span class="result-value">${results.regimeTributarioRecomendado}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Economia Tributária Projetada (${results.horizontePlanejamento} anos):</span>
                    <span class="result-value">${TAXMASTER.utils.formatCurrency(results.economiaTributariaTotal)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Percentual de Economia:</span>
                    <span class="result-value">${(results.percentualEconomia * 100).toFixed(2)}%</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Valor Presente da Economia:</span>
                    <span class="result-value">${TAXMASTER.utils.formatCurrency(results.valorPresenteEconomia)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">ROI do Planejamento Tributário:</span>
                    <span class="result-value">${(results.roiPlanejamentoTributario * 100).toFixed(2)}%</span>
                </div>
            `;
        }
        
        // Preencher projeções anuais
        const projecoesContainer = document.getElementById('projecoes-anuais');
        if (projecoesContainer && results.projecoesAnuais) {
            let projecoesHtml = `
                <h3>Projeções Anuais</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Ano</th>
                            <th>Faturamento Projetado</th>
                            <th>Tributos (Regime Atual)</th>
                            <th>Tributos (Regime Recomendado)</th>
                            <th>Economia Anual</th>
                            <th>Economia Acumulada</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            let economiaAcumulada = 0;
            
            results.projecoesAnuais.forEach(ano => {
                economiaAcumulada += ano.economiaTributaria;
                
                projecoesHtml += `
                    <tr>
                        <td>${ano.ano}</td>
                        <td>${TAXMASTER.utils.formatCurrency(ano.faturamentoProjetado)}</td>
                        <td>${TAXMASTER.utils.formatCurrency(ano.tributosRegimeAtual)}</td>
                        <td>${TAXMASTER.utils.formatCurrency(ano.tributosRegimeRecomendado)}</td>
                        <td>${TAXMASTER.utils.formatCurrency(ano.economiaTributaria)}</td>
                        <td>${TAXMASTER.utils.formatCurrency(economiaAcumulada)}</td>
                    </tr>
                `;
            });
            
            projecoesHtml += `
                    </tbody>
                </table>
            `;
            
            projecoesContainer.innerHTML = projecoesHtml;
        }
        
        // Preencher análise de sensibilidade
        const sensibilidadeContainer = document.getElementById('analise-sensibilidade');
        if (sensibilidadeContainer && results.analiseSensibilidade) {
            let sensibilidadeHtml = `
                <h3>Análise de Sensibilidade</h3>
                <p>Impacto de variações nos parâmetros econômicos na economia tributária projetada:</p>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Parâmetro</th>
                            <th>Variação</th>
                            <th>Economia Tributária</th>
                            <th>Diferença</th>
                            <th>Impacto</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            results.analiseSensibilidade.forEach(analise => {
                const diferenca = analise.economiaTributaria - results.economiaTributariaTotal;
                const impactoPercentual = diferenca / results.economiaTributariaTotal;
                const impactoClass = impactoPercentual > 0 ? 'positive' : (impactoPercentual < 0 ? 'negative' : 'neutral');
                
                sensibilidadeHtml += `
                    <tr class="${impactoClass}">
                        <td>${analise.parametro}</td>
                        <td>${analise.variacao}</td>
                        <td>${TAXMASTER.utils.formatCurrency(analise.economiaTributaria)}</td>
                        <td>${TAXMASTER.utils.formatCurrency(diferenca)}</td>
                        <td>${(impactoPercentual * 100).toFixed(2)}%</td>
                    </tr>
                `;
            });
            
            sensibilidadeHtml += `
                    </tbody>
                </table>
            `;
            
            sensibilidadeContainer.innerHTML = sensibilidadeHtml;
        }
        
        // Preencher recomendações estratégicas
        const recomendacoesContainer = document.getElementById('recomendacoes-estrategicas');
        if (recomendacoesContainer && results.recomendacoesEstrategicas) {
            let recomendacoesHtml = `
                <h3>Recomendações Estratégicas</h3>
                <div class="recommendations-list">
            `;
            
            results.recomendacoesEstrategicas.forEach(recomendacao => {
                recomendacoesHtml += `
                    <div class="recommendation-item">
                        <h4>${recomendacao.titulo}</h4>
                        <p>${recomendacao.descricao}</p>
                        <div class="recommendation-details">
                            <span class="recommendation-priority">Prioridade: ${recomendacao.prioridade}</span>
                            <span class="recommendation-impact">Impacto: ${recomendacao.impacto}</span>
                            <span class="recommendation-complexity">Complexidade: ${recomendacao.complexidade}</span>
                        </div>
                    </div>
                `;
            });
            
            recomendacoesHtml += `
                </div>
            `;
            
            recomendacoesContainer.innerHTML = recomendacoesHtml;
        }
        
        // Gerar gráfico de projeção de faturamento
        this.generateRevenueProjectionChart(results);
        
        // Gerar gráfico de economia tributária
        this.generateTaxSavingsChart(results);
        
        // Gerar gráfico de comparativo entre regimes
        this.generateTaxRegimeComparisonChart(results);
        
        // Salvar simulação no histórico
        this.saveSimulation(results);
        
        // Configurar botões de exportação
        this.setupExportButtons(results);
    },
    
    // Esconder resultados da simulação
    hideResults: function() {
        const resultsContainer = document.getElementById('simulation-results');
        if (resultsContainer) {
            resultsContainer.classList.remove('active');
        }
    },
    
    // Gerar gráfico de projeção de faturamento
    generateRevenueProjectionChart: function(results) {
        const chartContainer = document.getElementById('revenue-projection-chart');
        if (!chartContainer || !results.projecoesAnuais) return;
        
        // Limpar container
        chartContainer.innerHTML = '';
        
        // Criar canvas para o gráfico
        const canvas = document.createElement('canvas');
        chartContainer.appendChild(canvas);
        
        // Dados para o gráfico
        const anos = results.projecoesAnuais.map(ano => ano.ano);
        const faturamentos = results.projecoesAnuais.map(ano => ano.faturamentoProjetado);
        
        // Criar gráfico usando Chart.js
        if (typeof Chart !== 'undefined') {
            new Chart(canvas, {
                type: 'line',
                data: {
                    labels: anos,
                    datasets: [{
                        label: 'Faturamento Projetado',
                        data: faturamentos,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return 'R$ ' + value.toLocaleString('pt-BR');
                                }
                            }
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Projeção de Faturamento'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return 'Faturamento: ' + TAXMASTER.utils.formatCurrency(context.raw);
                                }
                            }
                        }
                    }
                }
            });
        } else {
            // Fallback se Chart.js não estiver disponível
            chartContainer.innerHTML = '<p>Biblioteca de gráficos não disponível</p>';
        }
    },
    
    // Gerar gráfico de economia tributária
    generateTaxSavingsChart: function(results) {
        const chartContainer = document.getElementById('tax-savings-chart');
        if (!chartContainer || !results.projecoesAnuais) return;
        
        // Limpar container
        chartContainer.innerHTML = '';
        
        // Criar canvas para o gráfico
        const canvas = document.createElement('canvas');
        chartContainer.appendChild(canvas);
        
        // Dados para o gráfico
        const anos = results.projecoesAnuais.map(ano => ano.ano);
        const economiasAnuais = results.projecoesAnuais.map(ano => ano.economiaTributaria);
        
        // Calcular economias acumuladas
        const economiasAcumuladas = [];
        let acumulado = 0;
        economiasAnuais.forEach(economia => {
            acumulado += economia;
            economiasAcumuladas.push(acumulado);
        });
        
        // Criar gráfico usando Chart.js
        if (typeof Chart !== 'undefined') {
            new Chart(canvas, {
                type: 'bar',
                data: {
                    labels: anos,
                    datasets: [
                        {
                            label: 'Economia Anual',
                            data: economiasAnuais,
                            backgroundColor: 'rgba(54, 162, 235, 0.7)',
                            order: 2
                        },
                        {
                            label: 'Economia Acumulada',
                            data: economiasAcumuladas,
                            type: 'line',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            fill: false,
                            order: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return 'R$ ' + value.toLocaleString('pt-BR');
                                }
                            }
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Economia Tributária Projetada'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.dataset.label + ': ' + TAXMASTER.utils.formatCurrency(context.raw);
                                }
                            }
                        }
                    }
                }
            });
        } else {
            // Fallback se Chart.js não estiver disponível
            chartContainer.innerHTML = '<p>Biblioteca de gráficos não disponível</p>';
        }
    },
    
    // Gerar gráfico de comparativo entre regimes
    generateTaxRegimeComparisonChart: function(results) {
        const chartContainer = document.getElementById('tax-regime-comparison-chart');
        if (!chartContainer || !results.projecoesAnuais) return;
        
        // Limpar container
        chartContainer.innerHTML = '';
        
        // Criar canvas para o gráfico
        const canvas = document.createElement('canvas');
        chartContainer.appendChild(canvas);
        
        // Dados para o gráfico
        const anos = results.projecoesAnuais.map(ano => ano.ano);
        const tributosRegimeAtual = results.projecoesAnuais.map(ano => ano.tributosRegimeAtual);
        const tributosRegimeRecomendado = results.projecoesAnuais.map(ano => ano.tributosRegimeRecomendado);
        
        // Criar gráfico usando Chart.js
        if (typeof Chart !== 'undefined') {
            new Chart(canvas, {
                type: 'bar',
                data: {
                    labels: anos,
                    datasets: [
                        {
                            label: `Tributos (${results.regimeTributarioAtual})`,
                            data: tributosRegimeAtual,
                            backgroundColor: 'rgba(255, 99, 132, 0.7)'
                        },
                        {
                            label: `Tributos (${results.regimeTributarioRecomendado})`,
                            data: tributosRegimeRecomendado,
                            backgroundColor: 'rgba(75, 192, 192, 0.7)'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return 'R$ ' + value.toLocaleString('pt-BR');
                                }
                            }
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Comparativo entre Regimes Tributários'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.dataset.label + ': ' + TAXMASTER.utils.formatCurrency(context.raw);
                                }
                            }
                        }
                    }
                }
            });
        } else {
            // Fallback se Chart.js não estiver disponível
            chartContainer.innerHTML = '<p>Biblioteca de gráficos não disponível</p>';
        }
    },
    
    // Salvar simulação no histórico
    saveSimulation: function(results) {
        // Verificar se usuário está autenticado
        if (!TAXMASTER.auth.isAuthenticated()) return;
        
        // Obter histórico de simulações do usuário
        const userId = TAXMASTER.auth.getCurrentUser().id;
        const simulations = TAXMASTER.storage.get(`simulations_${userId}`) || [];
        
        // Adicionar simulação atual ao histórico
        const simulation = {
            id: TAXMASTER.utils.generateId(),
            modulo: 'Módulo IV',
            titulo: 'Planejamento Tributário Estratégico - ' + results.cenarioEconomico,
            data_criacao: new Date().toISOString(),
            faturamento_anual: results.faturamentoAnual,
            regime_atual: results.regimeTributarioAtual,
            regime_recomendado: results.regimeTributarioRecomendado,
            economia_total: results.economiaTributariaTotal,
            horizonte: results.horizontePlanejamento,
            parametros: JSON.stringify({
                cenarioEconomico: results.cenarioEconomico,
                horizontePlanejamento: results.horizontePlanejamento,
                faturamentoAnual: results.faturamentoAnual,
                regimeTributarioAtual: results.regimeTributarioAtual,
                taxaCrescimento: results.taxaCrescimento,
                taxaInflacao: results.taxaInflacao,
                taxaJuros: results.taxaJuros
            }),
            resultados: JSON.stringify(results)
        };
        
        // Adicionar ao início da lista (mais recente primeiro)
        simulations.unshift(simulation);
        
        // Limitar a 20 simulações
        if (simulations.length > 20) {
            simulations.pop();
        }
        
        // Salvar no localStorage
        TAXMASTER.storage.set(`simulations_${userId}`, simulations);
        
        // Disparar evento de simulação salva
        TAXMASTER.events.trigger('simulation:saved', { simulation });
    },
    
    // Configurar botões de exportação
    setupExportButtons: function(results) {
        // Botão de exportar para HTML
        const exportHtmlBtn = document.getElementById('export-html');
        if (exportHtmlBtn) {
            exportHtmlBtn.addEventListener('click', () => {
                this.exportToHtml(results);
            });
        }
        
        // Botão de exportar para CSV
        const exportCsvBtn = document.getElementById('export-csv');
        if (exportCsvBtn) {
            exportCsvBtn.addEventListener('click', () => {
                this.exportToCsv(results);
            });
        }
        
        // Botão de exportar para PDF
        const exportPdfBtn = document.getElementById('export-pdf');
        if (exportPdfBtn) {
            exportPdfBtn.addEventListener('click', () => {
                this.exportToPdf(results);
            });
        }
    },
    
    // Exportar resultados para HTML
    exportToHtml: function(results) {
        // Gerar HTML do relatório
        const html = this.simulator.exportResults(results, 'html');
        
        // Criar blob e link para download
        const blob = new Blob([html], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        
        // Criar link e simular clique
        const a = document.createElement('a');
        a.href = url;
        a.download = `planejamento_tributario_${results.cenarioEconomico}_${new Date().toISOString().split('T')[0]}.html`;
        document.body.appendChild(a);
        a.click();
        
        // Limpar
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);
        
        // Notificar usuário
        TAXMASTER.ui.notifications.show('Relatório HTML exportado com sucesso', 'success');
    },
    
    // Exportar resultados para CSV
    exportToCsv: function(results) {
        // Gerar CSV do relatório
        const csv = this.simulator.exportResults(results, 'csv');
        
        // Criar blob e link para download
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        
        // Criar link e simular clique
        const a = document.createElement('a');
        a.href = url;
        a.download = `planejamento_tributario_${results.cenarioEconomico}_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        
        // Limpar
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);
        
        // Notificar usuário
        TAXMASTER.ui.notifications.show('Relatório CSV exportado com sucesso', 'success');
    },
    
    // Exportar resultados para PDF
    exportToPdf: function(results) {
        // Notificar usuário que a exportação está em andamento
        TAXMASTER.ui.notifications.show('Gerando PDF, aguarde...', 'info');
        
        // Gerar HTML do relatório
        const html = this.simulator.exportResults(results, 'html');
        
        // Usar biblioteca html2pdf.js para converter HTML para PDF
        if (typeof html2pdf !== 'undefined') {
            const element = document.createElement('div');
            element.innerHTML = html;
            document.body.appendChild(element);
            
            const options = {
                margin: 10,
                filename: `planejamento_tributario_${results.cenarioEconomico}_${new Date().toISOString().split('T')[0]}.pdf`,
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2 },
                jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
            };
            
            html2pdf().from(element).set(options).save().then(() => {
                // Remover elemento temporário
                document.body.removeChild(element);
                
                // Notificar usuário
                TAXMASTER.ui.notifications.show('Relatório PDF exportado com sucesso', 'success');
            });
        } else {
            // Fallback se html2pdf.js não estiver disponível
            TAXMASTER.ui.notifications.show('Biblioteca de exportação PDF não disponível', 'error');
        }
    },
    
    // Simulador de Planejamento Tributário Estratégico
    simulator: {
        // Configurações dos cenários econômicos
        cenarios: {
            // Cenário Conservador
            conservador: {
                taxaCrescimento: 0.03, // 3% ao ano
                taxaInflacao: 0.04,    // 4% ao ano
                taxaJuros: 0.06,       // 6% ao ano
                riscoEconomico: 'Baixo',
                descricao: 'Cenário com crescimento moderado, inflação controlada e juros estáveis.'
            },
            // Cenário Moderado
            moderado: {
                taxaCrescimento: 0.05, // 5% ao ano
                taxaInflacao: 0.05,    // 5% ao ano
                taxaJuros: 0.08,       // 8% ao ano
                riscoEconomico: 'Médio',
                descricao: 'Cenário com crescimento médio, inflação moderada e juros em elevação gradual.'
            },
            // Cenário Otimista
            otimista: {
                taxaCrescimento: 0.08, // 8% ao ano
                taxaInflacao: 0.03,    // 3% ao ano
                taxaJuros: 0.05,       // 5% ao ano
                riscoEconomico: 'Baixo-Médio',
                descricao: 'Cenário com crescimento acelerado, inflação controlada e juros favoráveis.'
            },
            // Cenário Pessimista
            pessimista: {
                taxaCrescimento: 0.01, // 1% ao ano
                taxaInflacao: 0.08,    // 8% ao ano
                taxaJuros: 0.12,       // 12% ao ano
                riscoEconomico: 'Alto',
                descricao: 'Cenário com crescimento mínimo, inflação elevada e juros altos.'
            },
            // Cenário de Recuperação
            recuperacao: {
                taxaCrescimento: 0.06, // 6% ao ano
                taxaInflacao: 0.06,    // 6% ao ano
                taxaJuros: 0.09,       // 9% ao ano
                riscoEconomico: 'Médio-Alto',
                descricao: 'Cenário de recuperação econômica, com crescimento acima da média, inflação em controle gradual e juros em ajuste.'
            }
        },
        
        // Configurações dos regimes tributários
        regimes: {
            // Simples Nacional
            simples_nacional: {
                faixasFaturamento: [
                    { limite: 180000, aliquota: 0.04 },
                    { limite: 360000, aliquota: 0.073 },
                    { limite: 720000, aliquota: 0.095 },
                    { limite: 1800000, aliquota: 0.107 },
                    { limite: 3600000, aliquota: 0.143 },
                    { limite: 4800000, aliquota: 0.19 }
                ],
                limiteFaturamento: 4800000,
                descricao: 'Regime simplificado para micro e pequenas empresas, com alíquotas progressivas baseadas no faturamento anual.'
            },
            // Lucro Presumido
            lucro_presumido: {
                presuncaoLucro: {
                    comercio: 0.08,
                    industria: 0.08,
                    servicos: 0.32,
                    transporte: 0.16
                },
                aliquotaIRPJ: 0.15,
                adicionalIRPJ: {
                    limite: 20000 * 12, // R$ 20.000 por mês
                    aliquota: 0.10
                },
                aliquotaCSLL: 0.09,
                aliquotaPIS: 0.0065,
                aliquotaCOFINS: 0.03,
                limiteFaturamento: 78000000,
                descricao: 'Regime com base de cálculo presumida para IRPJ e CSLL, adequado para empresas com margem de lucro superior à presunção.'
            },
            // Lucro Real
            lucro_real: {
                aliquotaIRPJ: 0.15,
                adicionalIRPJ: {
                    limite: 20000 * 12, // R$ 20.000 por mês
                    aliquota: 0.10
                },
                aliquotaCSLL: 0.09,
                aliquotaPIS: 0.0165,
                aliquotaCOFINS: 0.076,
                limiteFaturamento: null, // Sem limite
                descricao: 'Regime baseado no lucro contábil real, com possibilidade de compensação de prejuízos e aproveitamento integral de créditos.'
            }
        },
        
        // Inicialização do simulador
        init: function() {
            console.log('Inicializando simulador de planejamento tributário estratégico');
        },
        
        // Obter configuração de um cenário econômico
        getScenarioConfig: function(cenario) {
            return this.cenarios[cenario];
        },
        
        // Calcular valor presente líquido
        calcularVPL: function(fluxoCaixa, taxaDesconto) {
            let vpl = 0;
            
            fluxoCaixa.forEach((valor, index) => {
                vpl += valor / Math.pow(1 + taxaDesconto, index + 1);
            });
            
            return vpl;
        },
        
        // Calcular alíquota do Simples Nacional
        calcularAliquotaSimples: function(faturamentoAnual) {
            const faixas = this.regimes.simples_nacional.faixasFaturamento;
            
            // Verificar se está dentro do limite
            if (faturamentoAnual > this.regimes.simples_nacional.limiteFaturamento) {
                return null; // Acima do limite
            }
            
            // Encontrar faixa correspondente
            for (let i = 0; i < faixas.length; i++) {
                if (faturamentoAnual <= faixas[i].limite) {
                    return faixas[i].aliquota;
                }
            }
            
            // Se chegou aqui, está na última faixa
            return faixas[faixas.length - 1].aliquota;
        },
        
        // Calcular tributos no Lucro Presumido
        calcularTributosLucroPresumido: function(faturamentoAnual, atividadePrincipal) {
            // Verificar se está dentro do limite
            if (faturamentoAnual > this.regimes.lucro_presumido.limiteFaturamento) {
                return null; // Acima do limite
            }
            
            // Obter percentual de presunção
            const percentualPresuncao = this.regimes.lucro_presumido.presuncaoLucro[atividadePrincipal];
            if (!percentualPresuncao) {
                throw new Error(`Atividade principal '${atividadePrincipal}' não reconhecida`);
            }
            
            // Calcular lucro presumido
            const lucroPremido = faturamentoAnual * percentualPresuncao;
            
            // Calcular IRPJ
            let irpj = lucroPremido * this.regimes.lucro_presumido.aliquotaIRPJ;
            
            // Adicional de IRPJ se aplicável
            if (lucroPremido > this.regimes.lucro_presumido.adicionalIRPJ.limite) {
                irpj += (lucroPremido - this.regimes.lucro_presumido.adicionalIRPJ.limite) * this.regimes.lucro_presumido.adicionalIRPJ.aliquota;
            }
            
            // Calcular CSLL
            const csll = lucroPremido * this.regimes.lucro_presumido.aliquotaCSLL;
            
            // Calcular PIS e COFINS
            const pis = faturamentoAnual * this.regimes.lucro_presumido.aliquotaPIS;
            const cofins = faturamentoAnual * this.regimes.lucro_presumido.aliquotaCOFINS;
            
            // Total de tributos
            const totalTributos = irpj + csll + pis + cofins;
            
            return {
                irpj,
                csll,
                pis,
                cofins,
                totalTributos,
                aliquotaEfetiva: totalTributos / faturamentoAnual
            };
        },
        
        // Calcular tributos no Lucro Real
        calcularTributosLucroReal: function(faturamentoAnual, margemLucro) {
            // Calcular lucro real
            const lucroReal = faturamentoAnual * margemLucro;
            
            // Calcular IRPJ
            let irpj = lucroReal * this.regimes.lucro_real.aliquotaIRPJ;
            
            // Adicional de IRPJ se aplicável
            if (lucroReal > this.regimes.lucro_real.adicionalIRPJ.limite) {
                irpj += (lucroReal - this.regimes.lucro_real.adicionalIRPJ.limite) * this.regimes.lucro_real.adicionalIRPJ.aliquota;
            }
            
            // Calcular CSLL
            const csll = lucroReal * this.regimes.lucro_real.aliquotaCSLL;
            
            // Calcular PIS e COFINS (considerando créditos médios de 30%)
            const pis = faturamentoAnual * this.regimes.lucro_real.aliquotaPIS * 0.7;
            const cofins = faturamentoAnual * this.regimes.lucro_real.aliquotaCOFINS * 0.7;
            
            // Total de tributos
            const totalTributos = irpj + csll + pis + cofins;
            
            return {
                irpj,
                csll,
                pis,
                cofins,
                totalTributos,
                aliquotaEfetiva: totalTributos / faturamentoAnual
            };
        },
        
        // Recomendar regime tributário
        recomendarRegimeTributario: function(faturamentoAnual, margemLucro, atividadePrincipal) {
            // Verificar elegibilidade para cada regime
            const elegibilidadeSimples = faturamentoAnual <= this.regimes.simples_nacional.limiteFaturamento;
            const elegibilidadePresumido = faturamentoAnual <= this.regimes.lucro_presumido.limiteFaturamento;
            
            // Calcular tributos em cada regime
            let tributosSimples = null;
            let tributosPresumido = null;
            let tributosReal = null;
            
            if (elegibilidadeSimples) {
                const aliquotaSimples = this.calcularAliquotaSimples(faturamentoAnual);
                tributosSimples = {
                    totalTributos: faturamentoAnual * aliquotaSimples,
                    aliquotaEfetiva: aliquotaSimples
                };
            }
            
            if (elegibilidadePresumido) {
                tributosPresumido = this.calcularTributosLucroPresumido(faturamentoAnual, atividadePrincipal);
            }
            
            tributosReal = this.calcularTributosLucroReal(faturamentoAnual, margemLucro);
            
            // Comparar regimes elegíveis
            const regimes = [];
            
            if (tributosSimples) {
                regimes.push({
                    regime: 'simples_nacional',
                    tributos: tributosSimples.totalTributos,
                    aliquotaEfetiva: tributosSimples.aliquotaEfetiva
                });
            }
            
            if (tributosPresumido) {
                regimes.push({
                    regime: 'lucro_presumido',
                    tributos: tributosPresumido.totalTributos,
                    aliquotaEfetiva: tributosPresumido.aliquotaEfetiva
                });
            }
            
            regimes.push({
                regime: 'lucro_real',
                tributos: tributosReal.totalTributos,
                aliquotaEfetiva: tributosReal.aliquotaEfetiva
            });
            
            // Ordenar por menor carga tributária
            regimes.sort((a, b) => a.tributos - b.tributos);
            
            // Retornar regime recomendado (menor carga tributária)
            return regimes[0].regime;
        },
        
        // Gerar recomendações estratégicas
        gerarRecomendacoesEstrategicas: function(params, results) {
            const recomendacoes = [];
            
            // Recomendação de regime tributário
            recomendacoes.push({
                titulo: `Migração para Regime ${results.regimeTributarioRecomendado}`,
                descricao: `Recomendamos a migração para o regime de ${results.regimeTributarioRecomendado} com base nas projeções de faturamento e lucratividade. Esta mudança pode gerar uma economia tributária de aproximadamente ${TAXMASTER.utils.formatCurrency(results.economiaTributariaTotal)} ao longo de ${results.horizontePlanejamento} anos.`,
                prioridade: 'Alta',
                impacto: 'Alto',
                complexidade: 'Média'
            });
            
            // Recomendações específicas por regime
            if (results.regimeTributarioRecomendado === 'simples_nacional') {
                recomendacoes.push({
                    titulo: 'Monitoramento do Faturamento',
                    descricao: 'Monitore cuidadosamente o faturamento para evitar ultrapassar o limite do Simples Nacional. Considere estratégias de diferimento de receitas próximo ao final do ano fiscal se necessário.',
                    prioridade: 'Alta',
                    impacto: 'Alto',
                    complexidade: 'Baixa'
                });
                
                recomendacoes.push({
                    titulo: 'Planejamento de Anexos do Simples',
                    descricao: 'Avalie a distribuição de receitas entre diferentes atividades para otimizar o enquadramento nos anexos do Simples Nacional com alíquotas mais favoráveis.',
                    prioridade: 'Média',
                    impacto: 'Médio',
                    complexidade: 'Média'
                });
            } else if (results.regimeTributarioRecomendado === 'lucro_presumido') {
                recomendacoes.push({
                    titulo: 'Segregação de Atividades',
                    descricao: 'Considere a segregação de atividades em empresas distintas para otimizar as bases de presunção do lucro, especialmente separando atividades com percentuais de presunção diferentes.',
                    prioridade: 'Média',
                    impacto: 'Alto',
                    complexidade: 'Alta'
                });
                
                recomendacoes.push({
                    titulo: 'Distribuição de Lucros',
                    descricao: 'Implemente uma política de distribuição de lucros eficiente, aproveitando a isenção de tributação sobre lucros distribuídos até o limite da presunção.',
                    prioridade: 'Alta',
                    impacto: 'Alto',
                    complexidade: 'Baixa'
                });
            } else if (results.regimeTributarioRecomendado === 'lucro_real') {
                recomendacoes.push({
                    titulo: 'Gestão de Créditos Tributários',
                    descricao: 'Implemente um sistema rigoroso de controle e aproveitamento de créditos de PIS e COFINS, maximizando o aproveitamento de créditos em toda a cadeia produtiva.',
                    prioridade: 'Alta',
                    impacto: 'Alto',
                    complexidade: 'Média'
                });
                
                recomendacoes.push({
                    titulo: 'Planejamento de Investimentos',
                    descricao: 'Estruture um plano de investimentos que aproveite os benefícios fiscais de depreciação acelerada e incentivos fiscais para inovação tecnológica.',
                    prioridade: 'Média',
                    impacto: 'Médio',
                    complexidade: 'Alta'
                });
                
                recomendacoes.push({
                    titulo: 'Compensação de Prejuízos Fiscais',
                    descricao: 'Desenvolva estratégias para otimizar a compensação de prejuízos fiscais acumulados, respeitando o limite de 30% do lucro líquido ajustado.',
                    prioridade: 'Média',
                    impacto: 'Médio',
                    complexidade: 'Média'
                });
            }
            
            // Recomendações gerais
            recomendacoes.push({
                titulo: 'Revisão Periódica do Planejamento',
                descricao: 'Estabeleça um calendário de revisões trimestrais do planejamento tributário para ajustar estratégias conforme mudanças na legislação e no desempenho do negócio.',
                prioridade: 'Média',
                impacto: 'Médio',
                complexidade: 'Baixa'
            });
            
            recomendacoes.push({
                titulo: 'Capacitação da Equipe Contábil',
                descricao: 'Invista na capacitação contínua da equipe contábil e fiscal para garantir a correta aplicação das estratégias de planejamento tributário e acompanhamento de mudanças legislativas.',
                prioridade: 'Média',
                impacto: 'Médio',
                complexidade: 'Baixa'
            });
            
            // Recomendações específicas para o cenário econômico
            if (params.cenarioEconomico === 'otimista' || params.cenarioEconomico === 'recuperacao') {
                recomendacoes.push({
                    titulo: 'Antecipação de Investimentos',
                    descricao: 'Aproveite o cenário favorável para antecipar investimentos em expansão e modernização, maximizando benefícios fiscais e preparando a empresa para o crescimento projetado.',
                    prioridade: 'Alta',
                    impacto: 'Alto',
                    complexidade: 'Média'
                });
            } else if (params.cenarioEconomico === 'pessimista') {
                recomendacoes.push({
                    titulo: 'Gestão de Caixa e Parcelamentos',
                    descricao: 'Implemente controles rigorosos de fluxo de caixa e avalie a viabilidade de adesão a programas de parcelamento de débitos tributários para preservar liquidez em cenário adverso.',
                    prioridade: 'Alta',
                    impacto: 'Alto',
                    complexidade: 'Média'
                });
            }
            
            return recomendacoes;
        },
        
        // Simular planejamento tributário estratégico com base nos parâmetros fornecidos
        simulate: function(params) {
            const {
                cenario_economico,
                horizonte_planejamento,
                faturamento_anual,
                margem_lucro,
                atividade_principal,
                regime_tributario_atual,
                taxa_crescimento,
                taxa_inflacao,
                taxa_juros,
                custo_implementacao
            } = params;
            
            // Converter valores para números
            const faturamentoAnual = parseFloat(faturamento_anual);
            const margemLucro = parseFloat(margem_lucro) / 100; // Converter de percentual para decimal
            const horizontePlanejamento = parseInt(horizonte_planejamento);
            const custoImplementacao = parseFloat(custo_implementacao);
            
            // Verificar se o cenário existe
            if (!this.cenarios[cenario_economico]) {
                throw new Error(`Cenário econômico '${cenario_economico}' não reconhecido`);
            }
            
            // Obter configuração do cenário
            const configCenario = this.cenarios[cenario_economico];
            
            // Usar taxas fornecidas ou do cenário
            const taxaCrescimento = taxa_crescimento ? parseFloat(taxa_crescimento) / 100 : configCenario.taxaCrescimento;
            const taxaInflacao = taxa_inflacao ? parseFloat(taxa_inflacao) / 100 : configCenario.taxaInflacao;
            const taxaJuros = taxa_juros ? parseFloat(taxa_juros) / 100 : configCenario.taxaJuros;
            
            // Recomendar regime tributário
            const regimeTributarioRecomendado = this.recomendarRegimeTributario(faturamentoAnual, margemLucro, atividade_principal);
            
            // Gerar projeções anuais
            const projecoesAnuais = [];
            let faturamentoProjetado = faturamentoAnual;
            let economiaTributariaTotal = 0;
            
            for (let ano = 1; ano <= horizontePlanejamento; ano++) {
                // Projetar faturamento com crescimento e inflação
                faturamentoProjetado *= (1 + taxaCrescimento) * (1 + taxaInflacao);
                
                // Calcular tributos no regime atual
                let tributosRegimeAtual;
                
                if (regime_tributario_atual === 'simples_nacional') {
                    const aliquotaSimples = this.calcularAliquotaSimples(faturamentoProjetado);
                    tributosRegimeAtual = aliquotaSimples ? faturamentoProjetado * aliquotaSimples : null;
                } else if (regime_tributario_atual === 'lucro_presumido') {
                    const resultado = this.calcularTributosLucroPresumido(faturamentoProjetado, atividade_principal);
                    tributosRegimeAtual = resultado ? resultado.totalTributos : null;
                } else if (regime_tributario_atual === 'lucro_real') {
                    const resultado = this.calcularTributosLucroReal(faturamentoProjetado, margemLucro);
                    tributosRegimeAtual = resultado.totalTributos;
                } else {
                    throw new Error(`Regime tributário atual '${regime_tributario_atual}' não reconhecido`);
                }
                
                // Calcular tributos no regime recomendado
                let tributosRegimeRecomendado;
                
                if (regimeTributarioRecomendado === 'simples_nacional') {
                    const aliquotaSimples = this.calcularAliquotaSimples(faturamentoProjetado);
                    tributosRegimeRecomendado = aliquotaSimples ? faturamentoProjetado * aliquotaSimples : null;
                } else if (regimeTributarioRecomendado === 'lucro_presumido') {
                    const resultado = this.calcularTributosLucroPresumido(faturamentoProjetado, atividade_principal);
                    tributosRegimeRecomendado = resultado ? resultado.totalTributos : null;
                } else if (regimeTributarioRecomendado === 'lucro_real') {
                    const resultado = this.calcularTributosLucroReal(faturamentoProjetado, margemLucro);
                    tributosRegimeRecomendado = resultado.totalTributos;
                }
                
                // Verificar se algum regime não é elegível
                if (tributosRegimeAtual === null) {
                    tributosRegimeAtual = tributosRegimeRecomendado; // Assumir migração forçada
                }
                
                if (tributosRegimeRecomendado === null) {
                    tributosRegimeRecomendado = tributosRegimeAtual; // Manter regime atual
                }
                
                // Calcular economia tributária
                const economiaTributaria = tributosRegimeAtual - tributosRegimeRecomendado;
                economiaTributariaTotal += economiaTributaria;
                
                // Adicionar projeção anual
                projecoesAnuais.push({
                    ano: new Date().getFullYear() + ano - 1,
                    faturamentoProjetado,
                    tributosRegimeAtual,
                    tributosRegimeRecomendado,
                    economiaTributaria
                });
            }
            
            // Calcular percentual de economia
            const totalTributosRegimeAtual = projecoesAnuais.reduce((sum, proj) => sum + proj.tributosRegimeAtual, 0);
            const percentualEconomia = economiaTributariaTotal / totalTributosRegimeAtual;
            
            // Calcular valor presente da economia
            const fluxoEconomia = projecoesAnuais.map(proj => proj.economiaTributaria);
            fluxoEconomia.unshift(-custoImplementacao); // Incluir custo de implementação no ano 0
            
            const valorPresenteEconomia = this.calcularVPL(fluxoEconomia.slice(1), taxaJuros); // Excluir ano 0
            
            // Calcular ROI do planejamento tributário
            const roiPlanejamentoTributario = (valorPresenteEconomia - custoImplementacao) / custoImplementacao;
            
            // Gerar análise de sensibilidade
            const analiseSensibilidade = [
                // Variação na taxa de crescimento
                {
                    parametro: 'Taxa de Crescimento',
                    variacao: `+2 pontos percentuais (${((taxaCrescimento + 0.02) * 100).toFixed(2)}%)`,
                    economiaTributaria: this.simularVariacaoParametro(params, 'taxa_crescimento', taxaCrescimento + 0.02)
                },
                {
                    parametro: 'Taxa de Crescimento',
                    variacao: `-2 pontos percentuais (${((taxaCrescimento - 0.02) * 100).toFixed(2)}%)`,
                    economiaTributaria: this.simularVariacaoParametro(params, 'taxa_crescimento', taxaCrescimento - 0.02)
                },
                // Variação na margem de lucro
                {
                    parametro: 'Margem de Lucro',
                    variacao: `+5 pontos percentuais (${((margemLucro + 0.05) * 100).toFixed(2)}%)`,
                    economiaTributaria: this.simularVariacaoParametro(params, 'margem_lucro', (margemLucro + 0.05) * 100)
                },
                {
                    parametro: 'Margem de Lucro',
                    variacao: `-5 pontos percentuais (${((margemLucro - 0.05) * 100).toFixed(2)}%)`,
                    economiaTributaria: this.simularVariacaoParametro(params, 'margem_lucro', (margemLucro - 0.05) * 100)
                },
                // Variação na taxa de inflação
                {
                    parametro: 'Taxa de Inflação',
                    variacao: `+2 pontos percentuais (${((taxaInflacao + 0.02) * 100).toFixed(2)}%)`,
                    economiaTributaria: this.simularVariacaoParametro(params, 'taxa_inflacao', taxaInflacao + 0.02)
                },
                {
                    parametro: 'Taxa de Inflação',
                    variacao: `-2 pontos percentuais (${((taxaInflacao - 0.02) * 100).toFixed(2)}%)`,
                    economiaTributaria: this.simularVariacaoParametro(params, 'taxa_inflacao', taxaInflacao - 0.02)
                }
            ];
            
            // Gerar recomendações estratégicas
            const recomendacoesEstrategicas = this.gerarRecomendacoesEstrategicas(params, {
                cenarioEconomico: cenario_economico,
                horizontePlanejamento,
                faturamentoAnual,
                regimeTributarioAtual: regime_tributario_atual,
                regimeTributarioRecomendado,
                economiaTributariaTotal
            });
            
            // Retornar resultados da simulação
            return {
                cenarioEconomico: cenario_economico,
                horizontePlanejamento,
                faturamentoAnual,
                margemLucro,
                atividadePrincipal: atividade_principal,
                regimeTributarioAtual: regime_tributario_atual,
                regimeTributarioRecomendado,
                taxaCrescimento,
                taxaInflacao,
                taxaJuros,
                custoImplementacao,
                economiaTributariaTotal,
                percentualEconomia,
                valorPresenteEconomia,
                roiPlanejamentoTributario,
                projecoesAnuais,
                analiseSensibilidade,
                recomendacoesEstrategicas
            };
        },
        
        // Simular variação de parâmetro para análise de sensibilidade
        simularVariacaoParametro: function(params, parametro, novoValor) {
            // Clonar parâmetros
            const novosParams = { ...params };
            
            // Atualizar parâmetro
            novosParams[parametro] = novoValor;
            
            // Simular com novo parâmetro (versão simplificada)
            const resultado = this.simulate(novosParams);
            
            return resultado.economiaTributariaTotal;
        },
        
        // Exporta os resultados da simulação para diferentes formatos
        exportResults: function(resultados, formato) {
            switch (formato) {
                case 'json':
                    return JSON.stringify(resultados, null, 2);
                case 'csv':
                    return this.converterParaCSV(resultados);
                case 'html':
                    return this.converterParaHTML(resultados);
                default:
                    throw new Error(`Formato de exportação '${formato}' não suportado`);
            }
        },
        
        // Converte resultados para formato CSV
        converterParaCSV: function(resultados) {
            // Implementação básica para exportação CSV
            let csv = 'Cenário Econômico,Horizonte Planejamento,Faturamento Anual,Regime Atual,Regime Recomendado,Economia Total,Percentual Economia,Valor Presente Economia,ROI\n';
            csv += `${resultados.cenarioEconomico},${resultados.horizontePlanejamento},${resultados.faturamentoAnual.toFixed(2)},${resultados.regimeTributarioAtual},${resultados.regimeTributarioRecomendado},${resultados.economiaTributariaTotal.toFixed(2)},${(resultados.percentualEconomia * 100).toFixed(2)}%,${resultados.valorPresenteEconomia.toFixed(2)},${(resultados.roiPlanejamentoTributario * 100).toFixed(2)}%\n\n`;
            
            csv += 'Projeções Anuais\n';
            csv += 'Ano,Faturamento Projetado,Tributos Regime Atual,Tributos Regime Recomendado,Economia Anual\n';
            
            resultados.projecoesAnuais.forEach(ano => {
                csv += `${ano.ano},${ano.faturamentoProjetado.toFixed(2)},${ano.tributosRegimeAtual.toFixed(2)},${ano.tributosRegimeRecomendado.toFixed(2)},${ano.economiaTributaria.toFixed(2)}\n`;
            });
            
            csv += '\nAnálise de Sensibilidade\n';
            csv += 'Parâmetro,Variação,Economia Tributária,Diferença,Impacto\n';
            
            resultados.analiseSensibilidade.forEach(analise => {
                const diferenca = analise.economiaTributaria - resultados.economiaTributariaTotal;
                const impactoPercentual = diferenca / resultados.economiaTributariaTotal;
                
                csv += `${analise.parametro},${analise.variacao},${analise.economiaTributaria.toFixed(2)},${diferenca.toFixed(2)},${(impactoPercentual * 100).toFixed(2)}%\n`;
            });
            
            csv += '\nRecomendações Estratégicas\n';
            csv += 'Título,Descrição,Prioridade,Impacto,Complexidade\n';
            
            resultados.recomendacoesEstrategicas.forEach(recomendacao => {
                csv += `"${recomendacao.titulo}","${recomendacao.descricao}",${recomendacao.prioridade},${recomendacao.impacto},${recomendacao.complexidade}\n`;
            });
            
            return csv;
        },
        
        // Converte resultados para formato HTML
        converterParaHTML: function(resultados) {
            // Implementação básica para exportação HTML
            let html = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Planejamento Tributário Estratégico - TAX MASTER</title>
                <meta charset="UTF-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; color: #333; }
                    h1, h2, h3 { color: #0e6ba8; }
                    table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
                    th { background-color: #f2f2f2; text-align: center; }
                    .header { background-color: #1a1a1a; color: white; padding: 10px; }
                    .logo { height: 50px; margin-right: 20px; }
                    .summary { margin-bottom: 30px; }
                    .highlight { background-color: #ffc107; font-weight: bold; }
                    .section { margin-bottom: 30px; }
                    .recommendation-item { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 4px; }
                    .recommendation-details { display: flex; margin-top: 10px; }
                    .recommendation-details span { margin-right: 20px; font-size: 0.9em; color: #666; }
                    .positive { color: green; }
                    .negative { color: red; }
                    .neutral { color: #333; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>TAX MASTER - Planejamento Tributário Estratégico</h1>
                </div>
                
                <div class="section summary">
                    <h2>Resumo do Planejamento</h2>
                    <table>
                        <tr>
                            <th>Cenário Econômico</th>
                            <th>Horizonte</th>
                            <th>Faturamento Anual</th>
                            <th>Regime Atual</th>
                            <th>Regime Recomendado</th>
                        </tr>
                        <tr>
                            <td>${resultados.cenarioEconomico}</td>
                            <td>${resultados.horizontePlanejamento} anos</td>
                            <td>R$ ${resultados.faturamentoAnual.toFixed(2)}</td>
                            <td>${resultados.regimeTributarioAtual}</td>
                            <td>${resultados.regimeTributarioRecomendado}</td>
                        </tr>
                    </table>
                    
                    <h2>Resultados Financeiros</h2>
                    <table>
                        <tr>
                            <th>Economia Total</th>
                            <th>Percentual Economia</th>
                            <th>Valor Presente Economia</th>
                            <th>ROI do Planejamento</th>
                            <th>Custo Implementação</th>
                        </tr>
                        <tr>
                            <td>R$ ${resultados.economiaTributariaTotal.toFixed(2)}</td>
                            <td>${(resultados.percentualEconomia * 100).toFixed(2)}%</td>
                            <td>R$ ${resultados.valorPresenteEconomia.toFixed(2)}</td>
                            <td>${(resultados.roiPlanejamentoTributario * 100).toFixed(2)}%</td>
                            <td>R$ ${resultados.custoImplementacao.toFixed(2)}</td>
                        </tr>
                    </table>
                </div>`;
                
            // Adicionar projeções anuais
            html += `
                <div class="section">
                    <h2>Projeções Anuais</h2>
                    <table>
                        <tr>
                            <th>Ano</th>
                            <th>Faturamento Projetado</th>
                            <th>Tributos (Regime Atual)</th>
                            <th>Tributos (Regime Recomendado)</th>
                            <th>Economia Anual</th>
                            <th>Economia Acumulada</th>
                        </tr>`;
            
            let economiaAcumulada = 0;
            
            resultados.projecoesAnuais.forEach(ano => {
                economiaAcumulada += ano.economiaTributaria;
                
                html += `
                        <tr>
                            <td>${ano.ano}</td>
                            <td>R$ ${ano.faturamentoProjetado.toFixed(2)}</td>
                            <td>R$ ${ano.tributosRegimeAtual.toFixed(2)}</td>
                            <td>R$ ${ano.tributosRegimeRecomendado.toFixed(2)}</td>
                            <td>R$ ${ano.economiaTributaria.toFixed(2)}</td>
                            <td>R$ ${economiaAcumulada.toFixed(2)}</td>
                        </tr>`;
            });
            
            html += `
                    </table>
                </div>`;
            
            // Adicionar análise de sensibilidade
            html += `
                <div class="section">
                    <h2>Análise de Sensibilidade</h2>
                    <p>Impacto de variações nos parâmetros econômicos na economia tributária projetada:</p>
                    <table>
                        <tr>
                            <th>Parâmetro</th>
                            <th>Variação</th>
                            <th>Economia Tributária</th>
                            <th>Diferença</th>
                            <th>Impacto</th>
                        </tr>`;
            
            resultados.analiseSensibilidade.forEach(analise => {
                const diferenca = analise.economiaTributaria - resultados.economiaTributariaTotal;
                const impactoPercentual = diferenca / resultados.economiaTributariaTotal;
                const impactoClass = impactoPercentual > 0 ? 'positive' : (impactoPercentual < 0 ? 'negative' : 'neutral');
                
                html += `
                        <tr>
                            <td>${analise.parametro}</td>
                            <td>${analise.variacao}</td>
                            <td>R$ ${analise.economiaTributaria.toFixed(2)}</td>
                            <td class="${impactoClass}">R$ ${diferenca.toFixed(2)}</td>
                            <td class="${impactoClass}">${(impactoPercentual * 100).toFixed(2)}%</td>
                        </tr>`;
            });
            
            html += `
                    </table>
                </div>`;
            
            // Adicionar recomendações estratégicas
            html += `
                <div class="section">
                    <h2>Recomendações Estratégicas</h2>`;
            
            resultados.recomendacoesEstrategicas.forEach(recomendacao => {
                html += `
                    <div class="recommendation-item">
                        <h3>${recomendacao.titulo}</h3>
                        <p>${recomendacao.descricao}</p>
                        <div class="recommendation-details">
                            <span>Prioridade: ${recomendacao.prioridade}</span>
                            <span>Impacto: ${recomendacao.impacto}</span>
                            <span>Complexidade: ${recomendacao.complexidade}</span>
                        </div>
                    </div>`;
            });
            
            html += `
                </div>
                
                <div>
                    <p><strong>Data da Simulação:</strong> ${new Date().toLocaleDateString()}</p>
                    <p><small>Este relatório é meramente informativo e não constitui aconselhamento tributário formal. Consulte um especialista antes de implementar qualquer estratégia.</small></p>
                </div>
            </body>
            </html>`;
            
            return html;
        }
    }
};
