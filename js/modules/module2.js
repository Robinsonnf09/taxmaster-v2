// TAX MASTER - Módulo II: Transação Tributária Avançada
// Gerencia a interface e interações do Módulo II

TAXMASTER.modules.module2 = {
    init: function() {
        console.log("Inicializando Módulo II");
        this.setupForm();
        this.setupTabs();
        this.setupCapacityAnalysisForm();
        TAXMASTER.events.trigger("module:initialized", { module: "module2" });
    },

    setupForm: function() {
        const form = document.getElementById("simulacao-avancada-form");
        if (!form) return;

        form.addEventListener("submit", (e) => {
            e.preventDefault();
            if (!TAXMASTER.ui.forms.validate(form)) return;
            const formData = TAXMASTER.ui.forms.serialize(form);
            try {
                const simulator = TAXMASTER.simulators.advancedTransaction; // Assume simulator is globally accessible
                if (!simulator) throw new Error("Simulador do Módulo II não encontrado.");
                const results = simulator.simulate(formData);
                this.displayResults(results);
                this.displayComparison(results.comparativoModalidades); // Display comparison table
            } catch (error) {
                TAXMASTER.ui.notifications.show(error.message, "error");
                console.error("Erro na simulação do Módulo II:", error);
            }
        });

        form.addEventListener("reset", () => {
            this.hideResults();
        });
    },
    
    setupCapacityAnalysisForm: function() {
        const form = document.getElementById("capacidade-pagamento-form");
        if (!form) return;

        form.addEventListener("submit", (e) => {
            e.preventDefault();
            if (!TAXMASTER.ui.forms.validate(form)) return;
            const formData = TAXMASTER.ui.forms.serialize(form);
            try {
                const simulator = TAXMASTER.simulators.advancedTransaction;
                if (!simulator || !simulator.analyzeCapacity) throw new Error("Função de análise de capacidade não encontrada.");
                const capacityResults = simulator.analyzeCapacity(formData);
                this.displayCapacityResults(capacityResults);
            } catch (error) {
                TAXMASTER.ui.notifications.show(error.message, "error");
                console.error("Erro na análise de capacidade:", error);
            }
        });
        
         form.addEventListener("reset", () => {
            const resultDiv = document.getElementById("resultado-capacidade");
            if(resultDiv) resultDiv.style.display = 'none';
        });
    },

    setupTabs: function() {
        TAXMASTER.ui.tabs.init(document.querySelector("#module2-page .tab-container"));
    },

    displayResults: function(results) {
        console.log("Exibindo resultados Módulo II:", results);
        const resultsContainer = document.getElementById("resultados-simulacao-avancada");
        if (!resultsContainer) return;

        resultsContainer.style.display = "block";
        // Preencher campos de resultado (exemplo)
        document.getElementById("resultado-avancado-valor-original").textContent = TAXMASTER.utils.formatCurrency(results.valorOriginal);
        // ... (preencher outros campos de resultado como no módulo 1)
        document.getElementById("resultado-avancado-valor-final").textContent = TAXMASTER.utils.formatCurrency(results.valorAposDescontos);
        document.getElementById("resultado-avancado-economia").textContent = TAXMASTER.utils.formatCurrency(results.economiaTotal);
        document.getElementById("resultado-avancado-percentual-economia").textContent = `${(results.percentualEconomia * 100).toFixed(2)}%`;
        document.getElementById("resultado-avancado-entrada").textContent = TAXMASTER.utils.formatCurrency(results.valorEntrada);
        document.getElementById("resultado-avancado-num-parcelas").textContent = results.numeroParcelas;
        document.getElementById("resultado-avancado-valor-parcela").textContent = TAXMASTER.utils.formatCurrency(results.valorParcela);

        // Preencher tabela de amortização
        const tableBody = document.getElementById("tabela-amortizacao-avancada-body");
        if (tableBody && results.tabelaAmortizacao) {
            tableBody.innerHTML = ""; // Limpar tabela anterior
            results.tabelaAmortizacao.forEach(row => {
                const tr = document.createElement("tr");
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

        // Gerar gráficos
        this.generateCharts(results);

        // Configurar botões de exportação
        this.setupExportButtons(results);
        
        // Salvar simulação
        this.saveSimulation(results);
        
        // Mover para a tab de resultados
        TAXMASTER.ui.tabs.showTab(document.querySelector('#module2-page .tab-container'), 'resultados-avancados');
    },
    
    displayCapacityResults: function(capacityResults) {
        const resultDiv = document.getElementById("resultado-capacidade");
        if (!resultDiv) return;
        
        resultDiv.style.display = 'block';
        document.getElementById("capacidade-pagamento-valor").textContent = TAXMASTER.utils.formatCurrency(capacityResults.capacidadeMensal);
        document.getElementById("comprometimento-receita").textContent = `${(capacityResults.comprometimentoReceita * 100).toFixed(1)}%`;
        document.getElementById("prazo-maximo").textContent = `${capacityResults.prazoMaximoRecomendado} meses`;
        document.getElementById("entrada-maxima").textContent = TAXMASTER.utils.formatCurrency(capacityResults.entradaMaximaRecomendada);
        document.getElementById("classificacao-capacidade").textContent = capacityResults.classificacao;
        
        // Atualizar barra de progresso
        const progressBar = document.getElementById("capacidade-barra");
        const progressValue = Math.min(100, (capacityResults.capacidadeMensal / (capacityResults.receitaMensal * 0.3)) * 100 || 0); // Exemplo de cálculo
        progressBar.style.width = `${progressValue}%`;
        progressBar.textContent = `${progressValue.toFixed(0)}%`;
        progressBar.setAttribute('aria-valuenow', progressValue);
        
        // Mudar cor da barra com base na classificação
        progressBar.classList.remove('bg-success', 'bg-warning', 'bg-danger');
        if (capacityResults.classificacao === 'Boa') {
            progressBar.classList.add('bg-success');
        } else if (capacityResults.classificacao === 'Regular') {
            progressBar.classList.add('bg-warning');
        } else {
            progressBar.classList.add('bg-danger');
        }
    },
    
    displayComparison: function(comparisonData) {
        const tableBody = document.getElementById("tabela-comparativo-body");
        const chartCanvas = document.getElementById("grafico-comparativo");
        if (!tableBody || !chartCanvas || !comparisonData) return;

        tableBody.innerHTML = ""; // Limpar tabela
        const chartLabels = [];
        const chartDataValor = [];
        const chartDataEconomia = [];
        const chartDataParcela = [];

        comparisonData.forEach(item => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${item.modalidade}</td>
                <td>${TAXMASTER.utils.formatCurrency(item.valorFinal)}</td>
                <td>${TAXMASTER.utils.formatCurrency(item.descontoTotal)} (${(item.percentualDesconto * 100).toFixed(1)}%)</td>
                <td>${TAXMASTER.utils.formatCurrency(item.economiaTotal)}</td>
                <td>${TAXMASTER.utils.formatCurrency(item.valorParcela)}</td>
                <td>${item.prazo}</td>
                <td><button class="btn btn-sm btn-info select-modality" data-modality="${item.modalidade}">Selecionar</button></td>
            `;
            tableBody.appendChild(tr);
            
            // Dados para o gráfico
            chartLabels.push(item.modalidade);
            chartDataValor.push(item.valorFinal);
            chartDataEconomia.push(item.economiaTotal);
            chartDataParcela.push(item.valorParcela);
        });
        
        // Adicionar evento aos botões "Selecionar"
        tableBody.querySelectorAll('.select-modality').forEach(button => {
            button.addEventListener('click', (e) => {
                const modality = e.target.getAttribute('data-modality');
                // Preencher o formulário principal com os dados desta modalidade (se necessário)
                // Ou apenas destacar a linha e recalcular com esta modalidade
                TAXMASTER.ui.notifications.show(`Modalidade ${modality} selecionada para simulação detalhada.`, 'info');
                // Ex: document.getElementById('modalidade-transacao-avancado').value = modality;
                // Ex: document.getElementById('btn-simular-avancado').click();
                TAXMASTER.ui.tabs.showTab(document.querySelector('#module2-page .tab-container'), 'simulacao-avancada');
            });
        });

        // Gerar gráfico comparativo
        const existingChart = Chart.getChart(chartCanvas);
        if (existingChart) existingChart.destroy();
        
        new Chart(chartCanvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: chartLabels,
                datasets: [
                    { label: 'Valor Final (R$)', data: chartDataValor, backgroundColor: '#007bff' },
                    { label: 'Economia (R$)', data: chartDataEconomia, backgroundColor: '#28a745' },
                    { label: 'Valor Parcela (R$)', data: chartDataParcela, backgroundColor: '#ffc107' }
                ]
            },
            options: {
                responsive: true,
                plugins: { title: { display: true, text: 'Comparativo entre Modalidades' } },
                scales: { y: { beginAtZero: true } }
            }
        });
    },

    hideResults: function() {
        const resultsContainer = document.getElementById("resultados-simulacao-avancada");
        if (resultsContainer) resultsContainer.style.display = "none";
        const capacityContainer = document.getElementById("resultado-capacidade");
        if (capacityContainer) capacityContainer.style.display = "none";
        const comparisonTableBody = document.getElementById("tabela-comparativo-body");
        if (comparisonTableBody) comparisonTableBody.innerHTML = "";
        
        // Limpar gráficos
        const chart1 = Chart.getChart('grafico-comparativo');
        if (chart1) chart1.destroy();
        const chart2 = Chart.getChart('grafico-composicao-divida-avancada');
        if (chart2) chart2.destroy();
        const chart3 = Chart.getChart('grafico-economia-avancada');
        if (chart3) chart3.destroy();
        const tableBody = document.getElementById("tabela-amortizacao-avancada-body");
        if (tableBody) tableBody.innerHTML = "";
    },

    generateCharts: function(results) {
        // Gráfico de Composição da Dívida
        const ctxComposition = document.getElementById("grafico-composicao-divida-avancada")?.getContext("2d");
        if (ctxComposition) {
             const existingChart = Chart.getChart(ctxComposition.canvas);
             if (existingChart) existingChart.destroy();
            new Chart(ctxComposition, {
                type: "pie",
                data: {
                    labels: ["Principal", "Multa", "Juros", "Encargos"],
                    datasets: [{
                        data: [
                            results.composicaoDivida?.principal || 0,
                            results.composicaoDivida?.multa || 0,
                            results.composicaoDivida?.juros || 0,
                            results.composicaoDivida?.encargos || 0
                        ],
                        backgroundColor: ["#007bff", "#ffc107", "#dc3545", "#6c757d"]
                    }]
                },
                options: { responsive: true, plugins: { title: { display: true, text: "Composição da Dívida Original" } } }
            });
        }

        // Gráfico de Economia
        const ctxSavings = document.getElementById("grafico-economia-avancada")?.getContext("2d");
        if (ctxSavings) {
            const existingChart = Chart.getChart(ctxSavings.canvas);
             if (existingChart) existingChart.destroy();
            new Chart(ctxSavings, {
                type: "bar",
                data: {
                    labels: ["Valor Original", "Valor Final"],
                    datasets: [{
                        label: "Valor (R$)",
                        data: [results.valorOriginal, results.valorAposDescontos],
                        backgroundColor: ["#dc3545", "#28a745"]
                    }]
                },
                options: { responsive: true, plugins: { title: { display: true, text: "Economia Obtida" } }, indexAxis: 'y' }
            });
        }
    },

    setupExportButtons: function(results) {
        const btnPdf = document.getElementById("btn-exportar-pdf-avancado");
        const btnExcel = document.getElementById("btn-exportar-excel-avancado");
        const btnSave = document.getElementById("btn-salvar-simulacao-avancado");

        if (btnPdf) {
            btnPdf.onclick = () => TAXMASTER.reports.exportToPdf("resultados-simulacao-avancada", "simulacao_avancada.pdf");
        }
        if (btnExcel) {
            btnExcel.onclick = () => TAXMASTER.reports.exportToExcel(results.tabelaAmortizacao, "tabela_amortizacao_avancada.xlsx", "Amortização");
        }
         if (btnSave) {
             btnSave.onclick = () => this.saveSimulation(results, true);
        }
    },
    
    saveSimulation: function(results, notify = false) {
        const user = TAXMASTER.auth.getCurrentUser();
        if (user) {
            const simulationData = {
                id: `sim_${Date.now()}`,
                userId: user.id,
                modulo: 'module2',
                data: new Date().toISOString(),
                parametros: results.parametros,
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
            if (simulation && simulation.modulo === 'module2') {
                const form = document.getElementById('simulacao-avancada-form');
                TAXMASTER.ui.forms.fill(form, simulation.parametros);
                this.displayResults(simulation.resultados);
                this.displayComparison(simulation.resultados.comparativoModalidades);
                TAXMASTER.ui.notifications.show('Simulação carregada.', 'info');
            } else {
                TAXMASTER.ui.notifications.show('Simulação não encontrada ou inválida.', 'error');
            }
        }
    }
};

