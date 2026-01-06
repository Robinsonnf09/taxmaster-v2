// Simulador de Transação Tributária Avançada para o TAX MASTER - Módulo II
// Implementa cálculos avançados para diferentes modalidades de transação com análise de capacidade de pagamento

TAXMASTER.modules.module2 = {
    // Inicialização do módulo
    init: function() {
        console.log('Inicializando Módulo II - Transação Tributária Avançada');
        
        // Inicializar simulador
        this.simulator.init();
        
        // Configurar formulário de simulação
        this.setupForm();
        
        // Configurar tabs
        this.setupTabs();
        
        // Disparar evento de módulo inicializado
        TAXMASTER.events.trigger('module:initialized', { module: 'module2' });
    },
    
    // Configurar formulário de simulação
    setupForm: function() {
        const form = document.getElementById('advanced-transaction-form');
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
        
        // Configurar seleção de modalidade
        const modalitySelect = form.querySelector('#modalidade');
        if (modalitySelect) {
            modalitySelect.addEventListener('change', () => {
                this.updateFormFields(modalitySelect.value);
            });
            
            // Inicializar campos com modalidade padrão
            this.updateFormFields(modalitySelect.value);
        }
        
        // Configurar campos de capacidade de pagamento
        const capacidadeToggle = form.querySelector('#usar_capacidade_pagamento');
        if (capacidadeToggle) {
            capacidadeToggle.addEventListener('change', () => {
                this.toggleCapacidadePagamento(capacidadeToggle.checked);
            });
            
            // Inicializar estado
            this.toggleCapacidadePagamento(capacidadeToggle.checked);
        }
    },
    
    // Atualizar campos do formulário com base na modalidade selecionada
    updateFormFields: function(modality) {
        const config = this.simulator.getModalityConfig(modality);
        if (!config) return;
        
        // Atualizar campos com valores da modalidade
        const form = document.getElementById('advanced-transaction-form');
        
        // Atualizar prazo máximo
        const prazoField = form.querySelector('#prazo');
        if (prazoField) {
            prazoField.max = config.prazoMaximo;
            prazoField.nextElementSibling.textContent = `Máximo: ${config.prazoMaximo} meses`;
        }
        
        // Atualizar entrada mínima
        const entradaField = form.querySelector('#percentualEntrada');
        if (entradaField) {
            entradaField.min = config.entradaMinima * 100;
            entradaField.nextElementSibling.textContent = `Mínimo: ${config.entradaMinima * 100}%`;
        }
        
        // Atualizar informações de descontos
        const discountInfo = document.getElementById('discount-info');
        if (discountInfo) {
            discountInfo.innerHTML = `
                <p>Descontos para modalidade <strong>${modality}</strong>:</p>
                <ul>
                    <li>Multas: até ${config.descontoMultasMax * 100}%</li>
                    <li>Juros: até ${config.descontoJurosMax * 100}%</li>
                    <li>Encargos: até ${config.descontoEncargosMax * 100}%</li>
                </ul>
                <p><small>Os descontos efetivos dependem da capacidade de pagamento e do perfil de risco.</small></p>
            `;
        }
        
        // Atualizar informações de elegibilidade
        const eligibilityInfo = document.getElementById('eligibility-info');
        if (eligibilityInfo) {
            eligibilityInfo.innerHTML = `
                <p>Requisitos de elegibilidade para <strong>${modality}</strong>:</p>
                <ul>
                    <li>Tempo mínimo de inscrição em dívida ativa: ${config.tempoMinimoDividaAtiva} meses</li>
                    <li>Valor mínimo consolidado: ${TAXMASTER.utils.formatCurrency(config.valorMinimoConsolidado)}</li>
                    <li>${config.exigeRecuperacaoJudicial ? 'Exige recuperação judicial' : 'Não exige recuperação judicial'}</li>
                </ul>
            `;
        }
    },
    
    // Mostrar/esconder campos de capacidade de pagamento
    toggleCapacidadePagamento: function(mostrar) {
        const capacidadeFields = document.getElementById('capacidade_pagamento_fields');
        if (capacidadeFields) {
            capacidadeFields.style.display = mostrar ? 'block' : 'none';
            
            // Atualizar required nos campos
            const fields = capacidadeFields.querySelectorAll('input, select');
            fields.forEach(field => {
                field.required = mostrar;
            });
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
                    <span class="result-label">Modalidade:</span>
                    <span class="result-value">${results.modalidade}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Valor Original:</span>
                    <span class="result-value">${TAXMASTER.utils.formatCurrency(results.valorOriginal)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Valor Após Descontos:</span>
                    <span class="result-value">${TAXMASTER.utils.formatCurrency(results.valorAposDescontos)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Economia Total:</span>
                    <span class="result-value">${TAXMASTER.utils.formatCurrency(results.economiaTotal)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Percentual de Economia:</span>
                    <span class="result-value">${(results.percentualEconomia * 100).toFixed(2)}%</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Valor da Entrada:</span>
                    <span class="result-value">${TAXMASTER.utils.formatCurrency(results.valorEntrada)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Valor Parcelado:</span>
                    <span class="result-value">${TAXMASTER.utils.formatCurrency(results.valorParcelado)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Número de Parcelas:</span>
                    <span class="result-value">${results.numeroParcelas}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Valor da Parcela:</span>
                    <span class="result-value">${TAXMASTER.utils.formatCurrency(results.valorParcela)}</span>
                </div>
            `;
        }
        
        // Preencher análise de capacidade de pagamento
        const capacidadeContainer = document.getElementById('capacidade-pagamento-results');
        if (capacidadeContainer && results.analiseCapacidade) {
            capacidadeContainer.innerHTML = `
                <h3>Análise de Capacidade de Pagamento</h3>
                <div class="result-item">
                    <span class="result-label">Receita Mensal:</span>
                    <span class="result-value">${TAXMASTER.utils.formatCurrency(results.analiseCapacidade.receitaMensal)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Despesas Mensais:</span>
                    <span class="result-value">${TAXMASTER.utils.formatCurrency(results.analiseCapacidade.despesasMensais)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Capacidade de Pagamento:</span>
                    <span class="result-value">${TAXMASTER.utils.formatCurrency(results.analiseCapacidade.capacidadePagamento)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Comprometimento da Renda:</span>
                    <span class="result-value">${(results.analiseCapacidade.comprometimentoRenda * 100).toFixed(2)}%</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Classificação de Risco:</span>
                    <span class="result-value">${results.analiseCapacidade.classificacaoRisco}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Recomendação:</span>
                    <span class="result-value">${results.analiseCapacidade.recomendacao}</span>
                </div>
            `;
            
            // Adicionar classe de alerta conforme comprometimento
            const comprometimento = results.analiseCapacidade.comprometimentoRenda;
            if (comprometimento > 0.5) {
                capacidadeContainer.classList.add('alert-danger');
            } else if (comprometimento > 0.3) {
                capacidadeContainer.classList.add('alert-warning');
            } else {
                capacidadeContainer.classList.add('alert-success');
            }
        }
        
        // Preencher comparativo entre modalidades
        const comparativoContainer = document.getElementById('comparativo-modalidades');
        if (comparativoContainer && results.comparativoModalidades) {
            let comparativoHtml = `
                <h3>Comparativo entre Modalidades</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Modalidade</th>
                            <th>Valor Final</th>
                            <th>Economia</th>
                            <th>Prazo</th>
                            <th>Parcela</th>
                            <th>Elegível</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            results.comparativoModalidades.forEach(modalidade => {
                comparativoHtml += `
                    <tr class="${modalidade.modalidade === results.modalidade ? 'active' : ''}">
                        <td>${modalidade.modalidade}</td>
                        <td>${TAXMASTER.utils.formatCurrency(modalidade.valorFinal)}</td>
                        <td>${TAXMASTER.utils.formatCurrency(modalidade.economia)} (${(modalidade.percentualEconomia * 100).toFixed(2)}%)</td>
                        <td>${modalidade.prazo} meses</td>
                        <td>${TAXMASTER.utils.formatCurrency(modalidade.valorParcela)}</td>
                        <td>${modalidade.elegivel ? '<span class="badge badge-success">Sim</span>' : '<span class="badge badge-danger">Não</span>'}</td>
                    </tr>
                `;
            });
            
            comparativoHtml += `
                    </tbody>
                </table>
            `;
            
            comparativoContainer.innerHTML = comparativoHtml;
        }
        
        // Preencher tabela de amortização
        const amortizationTable = document.getElementById('amortization-table');
        if (amortizationTable && results.tabelaAmortizacao) {
            let tableHtml = `
                <table class="table">
                    <thead>
                        <tr>
                            <th>Parcela</th>
                            <th>Valor Parcela</th>
                            <th>Juros</th>
                            <th>Amortização</th>
                            <th>Saldo Devedor</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            results.tabelaAmortizacao.forEach(row => {
                tableHtml += `
                    <tr>
                        <td>${row.numeroParcela}</td>
                        <td>${TAXMASTER.utils.formatCurrency(row.valorParcela)}</td>
                        <td>${TAXMASTER.utils.formatCurrency(row.juros)}</td>
                        <td>${TAXMASTER.utils.formatCurrency(row.amortizacao)}</td>
                        <td>${TAXMASTER.utils.formatCurrency(row.saldoDevedor)}</td>
                    </tr>
                `;
            });
            
            tableHtml += `
                    </tbody>
                </table>
            `;
            
            amortizationTable.innerHTML = tableHtml;
        }
        
        // Gerar gráfico de composição da dívida
        this.generateDebtCompositionChart(results);
        
        // Gerar gráfico de economia
        this.generateSavingsChart(results);
        
        // Gerar gráfico de fluxo de caixa
        this.generateCashFlowChart(results);
        
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
    
    // Gerar gráfico de composição da dívida
    generateDebtCompositionChart: function(results) {
        const chartContainer = document.getElementById('debt-composition-chart');
        if (!chartContainer) return;
        
        // Limpar container
        chartContainer.innerHTML = '';
        
        // Criar canvas para o gráfico
        const canvas = document.createElement('canvas');
        chartContainer.appendChild(canvas);
        
        // Dados para o gráfico
        const originalValues = [
            results.valoresAposDesconto.principal,
            results.valoresAposDesconto.multas + results.descontos.multas,
            results.valoresAposDesconto.juros + results.descontos.juros,
            results.valoresAposDesconto.encargos + results.descontos.encargos
        ];
        
        const discountedValues = [
            results.valoresAposDesconto.principal,
            results.valoresAposDesconto.multas,
            results.valoresAposDesconto.juros,
            results.valoresAposDesconto.encargos
        ];
        
        // Criar gráfico usando Chart.js
        if (typeof Chart !== 'undefined') {
            new Chart(canvas, {
                type: 'bar',
                data: {
                    labels: ['Principal', 'Multas', 'Juros', 'Encargos'],
                    datasets: [
                        {
                            label: 'Valor Original',
                            data: originalValues,
                            backgroundColor: 'rgba(255, 99, 132, 0.7)'
                        },
                        {
                            label: 'Valor Após Descontos',
                            data: discountedValues,
                            backgroundColor: 'rgba(54, 162, 235, 0.7)'
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
                            text: 'Composição da Dívida'
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
    
    // Gerar gráfico de economia
    generateSavingsChart: function(results) {
        const chartContainer = document.getElementById('savings-chart');
        if (!chartContainer) return;
        
        // Limpar container
        chartContainer.innerHTML = '';
        
        // Criar canvas para o gráfico
        const canvas = document.createElement('canvas');
        chartContainer.appendChild(canvas);
        
        // Dados para o gráfico
        const data = [
            results.valorAposDescontos,
            results.economiaTotal
        ];
        
        // Criar gráfico usando Chart.js
        if (typeof Chart !== 'undefined') {
            new Chart(canvas, {
                type: 'pie',
                data: {
                    labels: ['Valor a Pagar', 'Economia'],
                    datasets: [{
                        data: data,
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.7)',
                            'rgba(75, 192, 192, 0.7)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Economia na Transação'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = TAXMASTER.utils.formatCurrency(context.raw);
                                    const percentage = ((context.raw / results.valorOriginal) * 100).toFixed(2) + '%';
                                    return label + ': ' + value + ' (' + percentage + ')';
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
    
    // Gerar gráfico de fluxo de caixa
    generateCashFlowChart: function(results) {
        const chartContainer = document.getElementById('cash-flow-chart');
        if (!chartContainer || !results.analiseCapacidade) return;
        
        // Limpar container
        chartContainer.innerHTML = '';
        
        // Criar canvas para o gráfico
        const canvas = document.createElement('canvas');
        chartContainer.appendChild(canvas);
        
        // Dados para o gráfico
        const meses = Array.from({length: 12}, (_, i) => i + 1);
        const receitaProjetada = Array(12).fill(results.analiseCapacidade.receitaMensal);
        const despesasProjetadas = Array(12).fill(results.analiseCapacidade.despesasMensais);
        const parcelasDivida = Array(12).fill(results.valorParcela);
        
        // Criar gráfico usando Chart.js
        if (typeof Chart !== 'undefined') {
            new Chart(canvas, {
                type: 'line',
                data: {
                    labels: meses.map(m => `Mês ${m}`),
                    datasets: [
                        {
                            label: 'Receita Projetada',
                            data: receitaProjetada,
                            borderColor: 'rgba(75, 192, 192, 1)',
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            fill: false
                        },
                        {
                            label: 'Despesas Projetadas',
                            data: despesasProjetadas,
                            borderColor: 'rgba(255, 99, 132, 1)',
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            fill: false
                        },
                        {
                            label: 'Parcelas da Dívida',
                            data: parcelasDivida,
                            borderColor: 'rgba(54, 162, 235, 1)',
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            fill: false
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
                            text: 'Projeção de Fluxo de Caixa (12 meses)'
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
            modulo: 'Módulo II',
            titulo: 'Transação Tributária Avançada - ' + results.modalidade,
            data_criacao: new Date().toISOString(),
            valor_original: results.valorOriginal,
            valor_final: results.valorAposDescontos,
            economia: results.economiaTotal,
            modalidade: results.modalidade,
            parametros: JSON.stringify({
                modalidade: results.modalidade,
                prazo: results.numeroParcelas,
                percentualEntrada: results.valorEntrada / results.valorAposDescontos,
                percentuais: {
                    principal: results.valoresAposDesconto.principal / results.valorOriginal,
                    multas: (results.valoresAposDesconto.multas + results.descontos.multas) / results.valorOriginal,
                    juros: (results.valoresAposDesconto.juros + results.descontos.juros) / results.valorOriginal,
                    encargos: (results.valoresAposDesconto.encargos + results.descontos.encargos) / results.valorOriginal
                },
                capacidadePagamento: results.analiseCapacidade ? {
                    receitaMensal: results.analiseCapacidade.receitaMensal,
                    despesasMensais: results.analiseCapacidade.despesasMensais,
                    comprometimentoRenda: results.analiseCapacidade.comprometimentoRenda
                } : null
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
        a.download = `transacao_tributaria_avancada_${results.modalidade}_${new Date().toISOString().split('T')[0]}.html`;
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
        a.download = `transacao_tributaria_avancada_${results.modalidade}_${new Date().toISOString().split('T')[0]}.csv`;
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
    
    // Simulador de Transação Tributária Avançada
    simulator: {
        // Configurações das modalidades de transação
        modalidades: {
            // Transação por adesão - Lei 13.988/2020
            adesao: {
                descontoMultasMin: 0.30,
                descontoMultasMax: 0.50,
                descontoJurosMin: 0.25,
                descontoJurosMax: 0.40,
                descontoEncargosMin: 0.15,
                descontoEncargosMax: 0.25,
                prazoMaximo: 60,
                entradaMinima: 0.05,
                tempoMinimoDividaAtiva: 12,
                valorMinimoConsolidado: 10000,
                exigeRecuperacaoJudicial: false
            },
            // Transação individual - Lei 13.988/2020
            individual: {
                descontoMultasMin: 0.50,
                descontoMultasMax: 0.70,
                descontoJurosMin: 0.40,
                descontoJurosMax: 0.65,
                descontoEncargosMin: 0.20,
                descontoEncargosMax: 0.30,
                prazoMaximo: 120,
                entradaMinima: 0.04,
                tempoMinimoDividaAtiva: 36,
                valorMinimoConsolidado: 15000000,
                exigeRecuperacaoJudicial: true
            },
            // Transação extraordinária - Portaria PGFN
            extraordinaria: {
                descontoMultasMin: 0.30,
                descontoMultasMax: 0.40,
                descontoJurosMin: 0.30,
                descontoJurosMax: 0.40,
                descontoEncargosMin: 0.15,
                descontoEncargosMax: 0.20,
                prazoMaximo: 72,
                entradaMinima: 0.04,
                tempoMinimoDividaAtiva: 6,
                valorMinimoConsolidado: 5000,
                exigeRecuperacaoJudicial: false
            },
            // Transação excepcional - COVID-19
            excepcional: {
                descontoMultasMin: 0.40,
                descontoMultasMax: 0.70,
                descontoJurosMin: 0.40,
                descontoJurosMax: 0.70,
                descontoEncargosMin: 0.20,
                descontoEncargosMax: 0.30,
                prazoMaximo: 145,
                entradaMinima: 0.04,
                tempoMinimoDividaAtiva: 0,
                valorMinimoConsolidado: 0,
                exigeRecuperacaoJudicial: false
            }
        },
        
        // Taxa de juros para parcelamento
        taxaJurosMensal: 0.01, // 1% ao mês
        
        // Inicialização do simulador
        init: function() {
            console.log('Inicializando simulador de transação tributária avançada');
        },
        
        // Obter configuração de uma modalidade
        getModalityConfig: function(modalidade) {
            return this.modalidades[modalidade];
        },
        
        // Calcular o valor da parcela com base no montante, prazo e taxa de juros
        calcularParcela: function(montante, prazo, taxaJuros) {
            // Fórmula de amortização: PMT = PV * (r * (1 + r)^n) / ((1 + r)^n - 1)
            const r = taxaJuros;
            const n = prazo;
            
            if (r === 0) {
                return montante / n;
            }
            
            const parcela = montante * (r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
            return parcela;
        },
        
        // Analisar capacidade de pagamento
        analisarCapacidadePagamento: function(receitaMensal, despesasMensais, valorParcela) {
            const capacidadePagamento = receitaMensal - despesasMensais;
            const comprometimentoRenda = valorParcela / capacidadePagamento;
            
            let classificacaoRisco, recomendacao;
            
            if (comprometimentoRenda > 0.7) {
                classificacaoRisco = 'Alto Risco';
                recomendacao = 'Renegociar com prazo maior ou buscar modalidade com maiores descontos';
            } else if (comprometimentoRenda > 0.5) {
                classificacaoRisco = 'Risco Moderado';
                recomendacao = 'Monitorar fluxo de caixa e considerar aumento de prazo';
            } else if (comprometimentoRenda > 0.3) {
                classificacaoRisco = 'Risco Baixo';
                recomendacao = 'Capacidade de pagamento adequada';
            } else {
                classificacaoRisco = 'Risco Muito Baixo';
                recomendacao = 'Excelente capacidade de pagamento, considerar redução de prazo';
            }
            
            return {
                receitaMensal,
                despesasMensais,
                capacidadePagamento,
                comprometimentoRenda,
                classificacaoRisco,
                recomendacao
            };
        },
        
        // Verificar elegibilidade para modalidade
        verificarElegibilidade: function(modalidade, tempoInscricaoDividaAtiva, valorConsolidado, emRecuperacaoJudicial) {
            const config = this.modalidades[modalidade];
            
            if (!config) {
                return {
                    elegivel: false,
                    motivos: ['Modalidade não reconhecida']
                };
            }
            
            const motivos = [];
            
            if (tempoInscricaoDividaAtiva < config.tempoMinimoDividaAtiva) {
                motivos.push(`Tempo mínimo de inscrição em dívida ativa não atingido (${tempoInscricaoDividaAtiva} meses < ${config.tempoMinimoDividaAtiva} meses)`);
            }
            
            if (valorConsolidado < config.valorMinimoConsolidado) {
                motivos.push(`Valor mínimo consolidado não atingido (${TAXMASTER.utils.formatCurrency(valorConsolidado)} < ${TAXMASTER.utils.formatCurrency(config.valorMinimoConsolidado)})`);
            }
            
            if (config.exigeRecuperacaoJudicial && !emRecuperacaoJudicial) {
                motivos.push('Recuperação judicial é exigida para esta modalidade');
            }
            
            return {
                elegivel: motivos.length === 0,
                motivos: motivos
            };
        },
        
        // Calcular descontos com base na capacidade de pagamento e perfil de risco
        calcularDescontos: function(modalidade, comprometimentoRenda) {
            const config = this.modalidades[modalidade];
            
            if (!config) {
                throw new Error(`Modalidade de transação '${modalidade}' não reconhecida`);
            }
            
            // Fator de ajuste baseado no comprometimento da renda
            // Quanto maior o comprometimento, maiores os descontos
            let fatorAjuste;
            
            if (comprometimentoRenda > 0.7) {
                fatorAjuste = 1.0; // 100% do desconto máximo
            } else if (comprometimentoRenda > 0.5) {
                fatorAjuste = 0.9; // 90% do desconto máximo
            } else if (comprometimentoRenda > 0.3) {
                fatorAjuste = 0.7; // 70% do desconto máximo
            } else {
                fatorAjuste = 0.5; // 50% do desconto máximo
            }
            
            // Calcular descontos ajustados
            const descontoMultas = config.descontoMultasMin + (config.descontoMultasMax - config.descontoMultasMin) * fatorAjuste;
            const descontoJuros = config.descontoJurosMin + (config.descontoJurosMax - config.descontoJurosMin) * fatorAjuste;
            const descontoEncargos = config.descontoEncargosMin + (config.descontoEncargosMax - config.descontoEncargosMin) * fatorAjuste;
            
            return {
                descontoMultas,
                descontoJuros,
                descontoEncargos,
                fatorAjuste
            };
        },
        
        // Simular transação tributária avançada com base nos parâmetros fornecidos
        simulate: function(params) {
            const {
                modalidade,
                valorPrincipal,
                valorMultas,
                valorJuros,
                valorEncargos,
                prazo,
                percentualEntrada,
                tempoInscricaoDividaAtiva,
                emRecuperacaoJudicial,
                usar_capacidade_pagamento,
                receita_mensal,
                despesas_mensais
            } = params;
            
            // Converter valores para números
            const principal = parseFloat(valorPrincipal);
            const multas = parseFloat(valorMultas);
            const juros = parseFloat(valorJuros);
            const encargos = parseFloat(valorEncargos);
            const meses = parseInt(prazo);
            const entrada = parseFloat(percentualEntrada) / 100; // Converter de percentual para decimal
            const tempoInscricao = parseInt(tempoInscricaoDividaAtiva) || 0;
            const recuperacaoJudicial = emRecuperacaoJudicial === 'sim';
            
            // Verificar se a modalidade existe
            if (!this.modalidades[modalidade]) {
                throw new Error(`Modalidade de transação '${modalidade}' não reconhecida`);
            }
            
            const config = this.modalidades[modalidade];
            
            // Validar parâmetros
            if (meses > config.prazoMaximo) {
                throw new Error(`Prazo máximo para modalidade ${modalidade} é de ${config.prazoMaximo} meses`);
            }
            
            if (entrada < config.entradaMinima) {
                throw new Error(`Entrada mínima para modalidade ${modalidade} é de ${config.entradaMinima * 100}%`);
            }
            
            // Verificar elegibilidade
            const valorTotal = principal + multas + juros + encargos;
            const elegibilidade = this.verificarElegibilidade(modalidade, tempoInscricao, valorTotal, recuperacaoJudicial);
            
            if (!elegibilidade.elegivel) {
                throw new Error(`Não elegível para modalidade ${modalidade}: ${elegibilidade.motivos.join(', ')}`);
            }
            
            // Calcular descontos
            let descontos;
            let analiseCapacidade = null;
            
            if (usar_capacidade_pagamento === 'sim' && receita_mensal && despesas_mensais) {
                const receitaMensal = parseFloat(receita_mensal);
                const despesasMensais = parseFloat(despesas_mensais);
                
                // Estimativa inicial de parcela para análise
                const valorEstimadoAposDescontos = principal + multas * (1 - config.descontoMultasMin) + 
                                                 juros * (1 - config.descontoJurosMin) + 
                                                 encargos * (1 - config.descontoEncargosMin);
                const valorEstimadoParcelado = valorEstimadoAposDescontos * (1 - entrada);
                const valorEstimadoParcela = this.calcularParcela(valorEstimadoParcelado, meses, this.taxaJurosMensal);
                
                // Analisar capacidade de pagamento
                analiseCapacidade = this.analisarCapacidadePagamento(receitaMensal, despesasMensais, valorEstimadoParcela);
                
                // Calcular descontos com base na capacidade de pagamento
                descontos = this.calcularDescontos(modalidade, analiseCapacidade.comprometimentoRenda);
            } else {
                // Usar descontos mínimos se não houver análise de capacidade
                descontos = {
                    descontoMultas: config.descontoMultasMin,
                    descontoJuros: config.descontoJurosMin,
                    descontoEncargos: config.descontoEncargosMin,
                    fatorAjuste: 0
                };
            }
            
            // Calcular valores após descontos
            const descontoMultasValor = multas * descontos.descontoMultas;
            const descontoJurosValor = juros * descontos.descontoJuros;
            const descontoEncargosValor = encargos * descontos.descontoEncargos;
            
            const multasAposDesconto = multas - descontoMultasValor;
            const jurosAposDesconto = juros - descontoJurosValor;
            const encargosAposDesconto = encargos - descontoEncargosValor;
            
            // Calcular valor total da dívida após descontos
            const valorTotalAposDescontos = principal + multasAposDesconto + jurosAposDesconto + encargosAposDesconto;
            
            // Calcular valor da entrada
            const valorEntrada = valorTotalAposDescontos * entrada;
            
            // Calcular valor a ser parcelado
            const valorParcelado = valorTotalAposDescontos - valorEntrada;
            
            // Calcular valor da parcela
            const valorParcela = this.calcularParcela(valorParcelado, meses, this.taxaJurosMensal);
            
            // Calcular economia total
            const economiaTotal = descontoMultasValor + descontoJurosValor + descontoEncargosValor;
            
            // Calcular percentual de economia
            const valorOriginal = principal + multas + juros + encargos;
            const percentualEconomia = economiaTotal / valorOriginal;
            
            // Gerar tabela de amortização
            const tabelaAmortizacao = this.gerarTabelaAmortizacao(valorParcelado, meses, this.taxaJurosMensal);
            
            // Gerar comparativo entre modalidades
            const comparativoModalidades = this.gerarComparativoModalidades(
                principal, multas, juros, encargos, 
                meses, entrada, 
                tempoInscricao, recuperacaoJudicial
            );
            
            // Atualizar análise de capacidade com valor real da parcela
            if (analiseCapacidade) {
                analiseCapacidade = this.analisarCapacidadePagamento(
                    analiseCapacidade.receitaMensal,
                    analiseCapacidade.despesasMensais,
                    valorParcela
                );
            }
            
            // Retornar resultados da simulação
            return {
                modalidade,
                valorOriginal,
                valorAposDescontos: valorTotalAposDescontos,
                economiaTotal,
                percentualEconomia,
                valorEntrada,
                valorParcelado,
                numeroParcelas: meses,
                valorParcela,
                tabelaAmortizacao,
                descontos: {
                    multas: descontoMultasValor,
                    juros: descontoJurosValor,
                    encargos: descontoEncargosValor,
                    fatorAjuste: descontos.fatorAjuste
                },
                valoresAposDesconto: {
                    principal: principal, // Principal não tem desconto
                    multas: multasAposDesconto,
                    juros: jurosAposDesconto,
                    encargos: encargosAposDesconto
                },
                analiseCapacidade,
                comparativoModalidades,
                elegibilidade
            };
        },
        
        // Gera tabela de amortização para o parcelamento
        gerarTabelaAmortizacao: function(valorParcelado, prazo, taxaJuros) {
            const tabela = [];
            let saldoDevedor = valorParcelado;
            
            for (let i = 1; i <= prazo; i++) {
                const juros = saldoDevedor * taxaJuros;
                const valorParcela = this.calcularParcela(valorParcelado, prazo, taxaJuros);
                const amortizacao = valorParcela - juros;
                
                saldoDevedor -= amortizacao;
                
                tabela.push({
                    numeroParcela: i,
                    valorParcela: valorParcela,
                    juros: juros,
                    amortizacao: amortizacao,
                    saldoDevedor: saldoDevedor > 0 ? saldoDevedor : 0
                });
            }
            
            return tabela;
        },
        
        // Gera comparativo entre modalidades
        gerarComparativoModalidades: function(principal, multas, juros, encargos, prazo, entrada, tempoInscricao, recuperacaoJudicial) {
            const comparativo = [];
            const valorTotal = principal + multas + juros + encargos;
            
            // Simular cada modalidade
            Object.keys(this.modalidades).forEach(modalidade => {
                const config = this.modalidades[modalidade];
                
                // Verificar elegibilidade
                const elegibilidade = this.verificarElegibilidade(modalidade, tempoInscricao, valorTotal, recuperacaoJudicial);
                
                // Calcular descontos (usando valores mínimos para comparação)
                const descontoMultas = multas * config.descontoMultasMin;
                const descontoJuros = juros * config.descontoJurosMin;
                const descontoEncargos = encargos * config.descontoEncargosMin;
                
                // Calcular valor após descontos
                const valorFinal = principal + (multas - descontoMultas) + (juros - descontoJuros) + (encargos - descontoEncargos);
                
                // Calcular economia
                const economia = valorTotal - valorFinal;
                const percentualEconomia = economia / valorTotal;
                
                // Calcular valor parcelado
                const prazoEfetivo = Math.min(prazo, config.prazoMaximo);
                const entradaEfetiva = Math.max(entrada, config.entradaMinima);
                const valorParcelado = valorFinal * (1 - entradaEfetiva);
                
                // Calcular valor da parcela
                const valorParcela = this.calcularParcela(valorParcelado, prazoEfetivo, this.taxaJurosMensal);
                
                comparativo.push({
                    modalidade,
                    valorFinal,
                    economia,
                    percentualEconomia,
                    prazo: prazoEfetivo,
                    valorParcela,
                    elegivel: elegibilidade.elegivel,
                    motivosInelegibilidade: elegibilidade.motivos
                });
            });
            
            return comparativo;
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
            let csv = 'Modalidade,Valor Original,Valor Após Descontos,Economia Total,Percentual Economia,Valor Entrada,Valor Parcelado,Número Parcelas,Valor Parcela\n';
            csv += `${resultados.modalidade},${resultados.valorOriginal.toFixed(2)},${resultados.valorAposDescontos.toFixed(2)},${resultados.economiaTotal.toFixed(2)},${(resultados.percentualEconomia * 100).toFixed(2)}%,${resultados.valorEntrada.toFixed(2)},${resultados.valorParcelado.toFixed(2)},${resultados.numeroParcelas},${resultados.valorParcela.toFixed(2)}\n\n`;
            
            if (resultados.analiseCapacidade) {
                csv += 'Análise de Capacidade de Pagamento\n';
                csv += 'Receita Mensal,Despesas Mensais,Capacidade de Pagamento,Comprometimento da Renda,Classificação de Risco\n';
                csv += `${resultados.analiseCapacidade.receitaMensal.toFixed(2)},${resultados.analiseCapacidade.despesasMensais.toFixed(2)},${resultados.analiseCapacidade.capacidadePagamento.toFixed(2)},${(resultados.analiseCapacidade.comprometimentoRenda * 100).toFixed(2)}%,${resultados.analiseCapacidade.classificacaoRisco}\n\n`;
            }
            
            csv += 'Comparativo entre Modalidades\n';
            csv += 'Modalidade,Valor Final,Economia,Percentual Economia,Prazo,Valor Parcela,Elegível\n';
            
            resultados.comparativoModalidades.forEach(modalidade => {
                csv += `${modalidade.modalidade},${modalidade.valorFinal.toFixed(2)},${modalidade.economia.toFixed(2)},${(modalidade.percentualEconomia * 100).toFixed(2)}%,${modalidade.prazo},${modalidade.valorParcela.toFixed(2)},${modalidade.elegivel ? 'Sim' : 'Não'}\n`;
            });
            
            csv += '\nTabela de Amortização\n';
            csv += 'Parcela,Valor Parcela,Juros,Amortização,Saldo Devedor\n';
            
            resultados.tabelaAmortizacao.forEach(linha => {
                csv += `${linha.numeroParcela},${linha.valorParcela.toFixed(2)},${linha.juros.toFixed(2)},${linha.amortizacao.toFixed(2)},${linha.saldoDevedor.toFixed(2)}\n`;
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
                <title>Simulação de Transação Tributária Avançada - TAX MASTER</title>
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
                    .alert { padding: 15px; border-radius: 4px; margin-bottom: 20px; }
                    .alert-success { background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
                    .alert-warning { background-color: #fff3cd; border: 1px solid #ffeeba; color: #856404; }
                    .alert-danger { background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>TAX MASTER - Simulação de Transação Tributária Avançada</h1>
                </div>
                
                <div class="section summary">
                    <h2>Resumo da Simulação</h2>
                    <table>
                        <tr>
                            <th>Modalidade</th>
                            <th>Valor Original</th>
                            <th>Valor Após Descontos</th>
                            <th>Economia Total</th>
                            <th>Percentual Economia</th>
                        </tr>
                        <tr>
                            <td>${resultados.modalidade}</td>
                            <td>R$ ${resultados.valorOriginal.toFixed(2)}</td>
                            <td>R$ ${resultados.valorAposDescontos.toFixed(2)}</td>
                            <td>R$ ${resultados.economiaTotal.toFixed(2)}</td>
                            <td>${(resultados.percentualEconomia * 100).toFixed(2)}%</td>
                        </tr>
                    </table>
                    
                    <h2>Detalhes do Parcelamento</h2>
                    <table>
                        <tr>
                            <th>Valor Entrada</th>
                            <th>Valor Parcelado</th>
                            <th>Número Parcelas</th>
                            <th>Valor Parcela</th>
                        </tr>
                        <tr>
                            <td>R$ ${resultados.valorEntrada.toFixed(2)}</td>
                            <td>R$ ${resultados.valorParcelado.toFixed(2)}</td>
                            <td>${resultados.numeroParcelas}</td>
                            <td>R$ ${resultados.valorParcela.toFixed(2)}</td>
                        </tr>
                    </table>
                </div>`;
                
            // Adicionar análise de capacidade de pagamento se disponível
            if (resultados.analiseCapacidade) {
                const comprometimento = resultados.analiseCapacidade.comprometimentoRenda;
                let alertClass = 'alert-success';
                
                if (comprometimento > 0.5) {
                    alertClass = 'alert-danger';
                } else if (comprometimento > 0.3) {
                    alertClass = 'alert-warning';
                }
                
                html += `
                <div class="section">
                    <h2>Análise de Capacidade de Pagamento</h2>
                    <div class="alert ${alertClass}">
                        <strong>Classificação de Risco:</strong> ${resultados.analiseCapacidade.classificacaoRisco}<br>
                        <strong>Recomendação:</strong> ${resultados.analiseCapacidade.recomendacao}
                    </div>
                    <table>
                        <tr>
                            <th>Receita Mensal</th>
                            <th>Despesas Mensais</th>
                            <th>Capacidade de Pagamento</th>
                            <th>Valor da Parcela</th>
                            <th>Comprometimento da Renda</th>
                        </tr>
                        <tr>
                            <td>R$ ${resultados.analiseCapacidade.receitaMensal.toFixed(2)}</td>
                            <td>R$ ${resultados.analiseCapacidade.despesasMensais.toFixed(2)}</td>
                            <td>R$ ${resultados.analiseCapacidade.capacidadePagamento.toFixed(2)}</td>
                            <td>R$ ${resultados.valorParcela.toFixed(2)}</td>
                            <td>${(resultados.analiseCapacidade.comprometimentoRenda * 100).toFixed(2)}%</td>
                        </tr>
                    </table>
                </div>`;
            }
            
            // Adicionar comparativo entre modalidades
            html += `
                <div class="section">
                    <h2>Comparativo entre Modalidades</h2>
                    <table>
                        <tr>
                            <th>Modalidade</th>
                            <th>Valor Final</th>
                            <th>Economia</th>
                            <th>Prazo</th>
                            <th>Valor Parcela</th>
                            <th>Elegível</th>
                        </tr>`;
            
            resultados.comparativoModalidades.forEach(modalidade => {
                html += `
                        <tr ${modalidade.modalidade === resultados.modalidade ? 'class="highlight"' : ''}>
                            <td>${modalidade.modalidade}</td>
                            <td>R$ ${modalidade.valorFinal.toFixed(2)}</td>
                            <td>R$ ${modalidade.economia.toFixed(2)} (${(modalidade.percentualEconomia * 100).toFixed(2)}%)</td>
                            <td>${modalidade.prazo} meses</td>
                            <td>R$ ${modalidade.valorParcela.toFixed(2)}</td>
                            <td>${modalidade.elegivel ? 'Sim' : 'Não'}</td>
                        </tr>`;
            });
            
            html += `
                    </table>
                </div>
                
                <div class="section">
                    <h2>Tabela de Amortização</h2>
                    <table>
                        <tr>
                            <th>Parcela</th>
                            <th>Valor Parcela</th>
                            <th>Juros</th>
                            <th>Amortização</th>
                            <th>Saldo Devedor</th>
                        </tr>`;
            
            resultados.tabelaAmortizacao.forEach(linha => {
                html += `
                        <tr>
                            <td>${linha.numeroParcela}</td>
                            <td>R$ ${linha.valorParcela.toFixed(2)}</td>
                            <td>R$ ${linha.juros.toFixed(2)}</td>
                            <td>R$ ${linha.amortizacao.toFixed(2)}</td>
                            <td>R$ ${linha.saldoDevedor.toFixed(2)}</td>
                        </tr>`;
            });
            
            html += `
                    </table>
                </div>
                
                <div>
                    <p><strong>Data da Simulação:</strong> ${new Date().toLocaleDateString()}</p>
                    <p><small>Esta simulação é meramente informativa e não constitui compromisso legal.</small></p>
                </div>
            </body>
            </html>`;
            
            return html;
        }
    }
};
