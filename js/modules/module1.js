// TAX MASTER - Módulo I: Transação Tributária Básica
// Gerencia a interface e interações do Módulo I

TAXMASTER.modules.module1 = {
    init: function() {
        console.log('Inicializando Módulo I');
        this.setupForm();
        this.setupTabs();
        TAXMASTER.events.trigger('module:initialized', { module: 'module1' });
    },

    setupForm: function() {
        const form = document.getElementById('simulacao-basica-form');
        if (!form) return;

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            if (!TAXMASTER.ui.forms.validate(form)) return;
            const formData = TAXMASTER.ui.forms.serialize(form);
            try {
                const simulator = TAXMASTER.simulators.transaction; // Assume simulator is globally accessible or passed
                if (!simulator) throw new Error("Simulador do Módulo I não encontrado.");
                const results = simulator.simulate(formData);
                this.displayResults(results);
            } catch (error) {
                TAXMASTER.ui.notifications.show(error.message, 'error');
                console.error("Erro na simulação do Módulo I:", error);
            }
        });

        form.addEventListener('reset', () => {
            this.hideResults();
        });
    },

    setupTabs: function() {
        TAXMASTER.ui.tabs.init(document.querySelector('#module1-page .tab-container'));
    },

    displayResults: function(results) {
        console.log("Exibindo resultados Módulo I:", results);
        const resultsContainer = document.getElementById('resultados-simulacao-basica');
        if (!resultsContainer) return;

        resultsContainer.style.display = 'block';
        // Preencher campos de resultado (exemplo)
        document.getElementById('resultado-basico-valor-original').textContent = TAXMASTER.utils.formatCurrency(results.valorOriginal);
        document.getElementById('resultado-basico-valor-final').textContent = TAXMASTER.utils.formatCurrency(results.valorFinal);
        document.getElementById('resultado-basico-economia').textContent = TAXMASTER.utils.formatCurrency(results.economiaTotal);
        document.getElementById('resultado-basico-percentual-economia').textContent = `${(results.percentualEconomia * 100).toFixed(2)}%`;
        document.getElementById('resultado-basico-entrada').textContent = TAXMASTER.utils.formatCurrency(results.valorEntrada);
        document.getElementById('resultado-basico-num-parcelas').textContent = results.numeroParcelas;
        document.getElementById('resultado-basico-valor-parcela').textContent = TAXMASTER.utils.formatCurrency(results.valorParcela);

        // Preencher tabela de amortização
        const tableBody = document.getElementById('tabela-amortizacao-basica-body');
        if (tableBody && results.tabelaAmortizacao) {
            tableBody.innerHTML = ''; // Limpar tabela anterior
            results.tabelaAmortizacao.forEach(row => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${row.numeroParcela}</td>
                    <td>${TAXMASTER.utils.formatCurrency(row.valorParcela)}</td>
                    <td>${TAXMASTER.utils.formatCurrency(row.juros)}</td>
                    <td>${TAXMASTER.utils.formatCurrency(row.amortizacao)}</td>
                    <td>${TAXMASTER.utils.formatCurrency(row.saldoDevedor)}</td>
                `;
                tableBody.appendChild(tr);
            });
        }
        
        // Gerar gráficos (se houver)
        this.generateCharts(results);

        // Configurar botões de exportação
        this.setupExportButtons(results);
        
        // Salvar simulação
        this.saveSimulation(results);
    },

    hideResults: function() {
        const resultsContainer = document.getElementById('resultados-simulacao-basica');
        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }
        // Limpar gráficos e tabela se necessário
        const chart1 = Chart.getChart('grafico-composicao-divida-basica');
        if (chart1) chart1.destroy();
        const chart2 = Chart.getChart('grafico-economia-basica');
        if (chart2) chart2.destroy();
        const tableBody = document.getElementById('tabela-amortizacao-basica-body');
        if (tableBody) tableBody.innerHTML = '';
    },

    generateCharts: function(results) {
        // Gráfico de Composição da Dívida
        const ctxComposition = document.getElementById('grafico-composicao-divida-basica')?.getContext('2d');
        if (ctxComposition) {
            new Chart(ctxComposition, {
                type: 'pie',
                data: {
                    labels: ['Principal', 'Multa', 'Juros', 'Encargos'],
                    datasets: [{
                        data: [
                            results.composicaoDivida?.principal || 0,
                            results.composicaoDivida?.multa || 0,
                            results.composicaoDivida?.juros || 0,
                            results.composicaoDivida?.encargos || 0
                        ],
                        backgroundColor: ['#007bff', '#ffc107', '#dc3545', '#6c757d']
                    }]
                },
                options: { responsive: true, plugins: { title: { display: true, text: 'Composição da Dívida Original' } } }
            });
        }

        // Gráfico de Economia
        const ctxSavings = document.getElementById('grafico-economia-basica')?.getContext('2d');
        if (ctxSavings) {
            new Chart(ctxSavings, {
                type: 'bar',
                data: {
                    labels: ['Valor Original', 'Valor Final'],
                    datasets: [{
                        label: 'Valor (R$)',
                        data: [results.valorOriginal, results.valorFinal],
                        backgroundColor: ['#dc3545', '#28a745']
                    }]
                },
                options: { responsive: true, plugins: { title: { display: true, text: 'Economia Obtida' } }, indexAxis: 'y' }
            });
        }
    },
    
    setupExportButtons: function(results) {
        const btnPdf = document.getElementById('btn-exportar-pdf-basico');
        const btnExcel = document.getElementById('btn-exportar-excel-basico');
        const btnSave = document.getElementById('btn-salvar-simulacao-basico');

        if (btnPdf) {
            btnPdf.onclick = () => TAXMASTER.reports.exportToPdf('resultados-simulacao-basica', 'simulacao_basica.pdf');
        }
        if (btnExcel) {
            btnExcel.onclick = () => TAXMASTER.reports.exportToExcel(results.tabelaAmortizacao, 'tabela_amortizacao_basica.xlsx', 'Amortização');
        }
        if (btnSave) {
             btnSave.onclick = () => this.saveSimulation(results, true); // true para forçar notificação
        }
    },
    
    saveSimulation: function(results, notify = false) {
        const user = TAXMASTER.auth.getCurrentUser();
        if (user) {
            const simulationData = {
                id: `sim_${Date.now()}`,
                userId: user.id,
                modulo: 'module1',
                data: new Date().toISOString(),
                parametros: results.parametros, // Assumindo que os parâmetros estão nos resultados
                resultados: results
            };
            if (TAXMASTER.storage.saveSimulation(simulationData)) {
                 if(notify) TAXMASTER.ui.notifications.show('Simulação salva com sucesso!', 'success');
            } else {
                 if(notify) TAXMASTER.ui.notifications.show('Erro ao salvar simulação.', 'error');
            }
        } else {
             if(notify) TAXMASTER.ui.notifications.show('Faça login para salvar a simulação.', 'warning');
        }
    },
    
    loadSimulation: function(simulationId) {
        const user = TAXMASTER.auth.getCurrentUser();
        if (user) {
            const simulation = TAXMASTER.storage.getSimulationById(user.id, simulationId);
            if (simulation && simulation.modulo === 'module1') {
                // Preencher formulário com parâmetros
                const form = document.getElementById('simulacao-basica-form');
                TAXMASTER.ui.forms.fill(form, simulation.parametros);
                // Exibir resultados
                this.displayResults(simulation.resultados);
                TAXMASTER.ui.notifications.show('Simulação carregada.', 'info');
            } else {
                TAXMASTER.ui.notifications.show('Simulação não encontrada ou inválida.', 'error');
            }
        }
    }
};

