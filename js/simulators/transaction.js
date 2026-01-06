// Simulador de Transação Tributária para o TAX MASTER - Módulo I
// Implementa cálculos para diferentes modalidades de transação

TAXMASTER.modules.module1 = {
    // Inicialização do módulo
    init: function() {
        console.log('Inicializando Módulo I - Transação Tributária Básica');
        
        // Inicializar simulador
        this.simulator.init();
        
        // Configurar formulário de simulação
        this.setupForm();
        
        // Configurar tabs
        this.setupTabs();
        
        // Disparar evento de módulo inicializado
        TAXMASTER.events.trigger('module:initialized', { module: 'module1' });
    },
    
    // Configurar formulário de simulação
    setupForm: function() {
        const form = document.getElementById('transaction-form');
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
    },
    
    // Atualizar campos do formulário com base na modalidade selecionada
    updateFormFields: function(modality) {
        const config = this.simulator.getModalityConfig(modality);
        if (!config) return;
        
        // Atualizar campos com valores da modalidade
        const form = document.getElementById('transaction-form');
        
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
                    <li>Multas: ${config.descontoMultas * 100}%</li>
                    <li>Juros: ${config.descontoJuros * 100}%</li>
                    <li>Encargos: ${config.descontoEncargos * 100}%</li>
                </ul>
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
            modulo: 'Módulo I',
            titulo: 'Transação Tributária - ' + results.modalidade,
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
                }
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
        a.download = `transacao_tributaria_${results.modalidade}_${new Date().toISOString().split('T')[0]}.html`;
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
        a.download = `transacao_tributaria_${results.modalidade}_${new Date().toISOString().split('T')[0]}.csv`;
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
    
    // Simulador de Transação Tributária
    simulator: {
        // Configurações das modalidades de transação
        modalidades: {
            // Transação por adesão - Lei 13.988/2020
            adesao: {
                descontoMultas: 0.50,
                descontoJuros: 0.40,
                descontoEncargos: 0.25,
                prazoMaximo: 60,
                entradaMinima: 0.05
            },
            // Transação individual - Lei 13.988/2020
            individual: {
                descontoMultas: 0.70,
                descontoJuros: 0.65,
                descontoEncargos: 0.30,
                prazoMaximo: 120,
                entradaMinima: 0.04
            },
            // Transação extraordinária - Portaria PGFN
            extraordinaria: {
                descontoMultas: 0.40,
                descontoJuros: 0.40,
                descontoEncargos: 0.20,
                prazoMaximo: 72,
                entradaMinima: 0.04
            }
        },
        
        // Taxa de juros para parcelamento
        taxaJurosMensal: 0.01, // 1% ao mês
        
        // Inicialização do simulador
        init: function() {
            console.log('Inicializando simulador de transação tributária');
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
        
        // Simular transação tributária com base nos parâmetros fornecidos
        simulate: function(params) {
            const {
                modalidade,
                valorPrincipal,
                valorMultas,
                valorJuros,
                valorEncargos,
                prazo,
                percentualEntrada
            } = params;
            
            // Converter valores para números
            const principal = parseFloat(valorPrincipal);
            const multas = parseFloat(valorMultas);
            const juros = parseFloat(valorJuros);
            const encargos = parseFloat(valorEncargos);
            const meses = parseInt(prazo);
            const entrada = parseFloat(percentualEntrada) / 100; // Converter de percentual para decimal
            
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
            
            // Calcular descontos
            const descontoMultas = multas * config.descontoMultas;
            const descontoJuros = juros * config.descontoJuros;
            const descontoEncargos = encargos * config.descontoEncargos;
            
            // Calcular valores após descontos
            const multasAposDesconto = multas - descontoMultas;
            const jurosAposDesconto = juros - descontoJuros;
            const encargosAposDesconto = encargos - descontoEncargos;
            
            // Calcular valor total da dívida após descontos
            const valorTotalAposDescontos = principal + multasAposDesconto + jurosAposDesconto + encargosAposDesconto;
            
            // Calcular valor da entrada
            const valorEntrada = valorTotalAposDescontos * entrada;
            
            // Calcular valor a ser parcelado
            const valorParcelado = valorTotalAposDescontos - valorEntrada;
            
            // Calcular valor da parcela
            const valorParcela = this.calcularParcela(valorParcelado, meses, this.taxaJurosMensal);
            
            // Calcular economia total
            const economiaTotal = descontoMultas + descontoJuros + descontoEncargos;
            
            // Calcular percentual de economia
            const valorOriginal = principal + multas + juros + encargos;
            const percentualEconomia = economiaTotal / valorOriginal;
            
            // Gerar tabela de amortização
            const tabelaAmortizacao = this.gerarTabelaAmortizacao(valorParcelado, meses, this.taxaJurosMensal);
            
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
                    multas: descontoMultas,
                    juros: descontoJuros,
                    encargos: descontoEncargos
                },
                valoresAposDesconto: {
                    principal: principal, // Principal não tem desconto
                    multas: multasAposDesconto,
                    juros: jurosAposDesconto,
                    encargos: encargosAposDesconto
                }
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
            
            csv += 'Tabela de Amortização\n';
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
                <title>Simulação de Transação Tributária - TAX MASTER</title>
                <meta charset="UTF-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; color: #333; }
                    h1, h2 { color: #0e6ba8; }
                    table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
                    th { background-color: #f2f2f2; text-align: center; }
                    .header { background-color: #1a1a1a; color: white; padding: 10px; }
                    .logo { height: 50px; margin-right: 20px; }
                    .summary { margin-bottom: 30px; }
                    .highlight { background-color: #ffc107; font-weight: bold; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>TAX MASTER - Simulação de Transação Tributária</h1>
                </div>
                
                <div class="summary">
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
                </div>
                
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
