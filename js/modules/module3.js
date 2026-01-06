// TAX MASTER - Módulo III: Parcelamento e Redução de Débitos
// Gerencia a interface e interações do Módulo III

TAXMASTER.modules.module3 = {
    init: function() {
        console.log("Inicializando Módulo III");
        this.setupForm();
        this.setupTabs();
        this.setupCashFlowAnalysis();
        TAXMASTER.events.trigger("module:initialized", { module: "module3" });
    },

    setupForm: function() {
        const form = document.getElementById("simulacao-parcelamento-form");
        if (!form) return;

        form.addEventListener("submit", (e) => {
            e.preventDefault();
            if (!TAXMASTER.ui.forms.validate(form)) return;
            const formData = TAXMASTER.ui.forms.serialize(form);
            try {
                const simulator = TAXMASTER.simulators.installment; // Assume simulator is globally accessible
                if (!simulator) throw new Error("Simulador do Módulo III não encontrado.");
                const results = simulator.simulate(formData);
                this.displayResults(results);
                this.displayComparison(results.comparativoModalidades); // Display comparison table
            } catch (error) {
                TAXMASTER.ui.notifications.show(error.message, "error");
                console.error("Erro na simulação do Módulo III:", error);
            }
        });

        form.addEventListener("reset", () => {
            this.hideResults();
        });
        
        // Toggle para análise de capacidade de pagamento
        const capacityToggle = form.querySelector("#usar-capacidade-pagamento");
        const capacityFields = form.querySelector("#capacidade-pagamento-fields");
        if (capacityToggle && capacityFields) {
            capacityToggle.addEventListener("change", () => {
                capacityFields.style.display = capacityToggle.checked ? "block" : "none";
                capacityFields.querySelectorAll("input").forEach(input => input.required = capacityToggle.checked);
            });
            // Estado inicial
            capacityFields.style.display = capacityToggle.checked ? "block" : "none";
            capacityFields.querySelectorAll("input").forEach(input => input.required = capacityToggle.checked);
        }
    },
    
    setupCashFlowAnalysis: function() {
        const updateButton = document.getElementById("btn-atualizar-fluxo");
        if (updateButton) {
            updateButton.addEventListener("click", () => {
                // Obter parâmetros da análise de fluxo de caixa
                const periodo = document.getElementById("periodo-projecao")?.value || 12;
                const taxaCrescimento = document.getElementById("taxa-crescimento")?.value || 2;
                const inflacao = document.getElementById("inflacao-projetada")?.value || 3.5;
                const juros = document.getElementById("taxa-juros-projetada")?.value || 6.5;
                
                // Obter resultados da simulação atual (se houver)
                const currentResults = this.getCurrentResults(); // Função auxiliar para pegar os resultados atuais
                if (!currentResults || !currentResults.tabelaAmortizacao) {
                    TAXMASTER.ui.notifications.show("Execute uma simulação de parcelamento primeiro.", "warning");
                    return;
                }
                
                try {
                    const simulator = TAXMASTER.simulators.installment;
                    if (!simulator || !simulator.projectCashFlow) throw new Error("Função de projeção de fluxo de caixa não encontrada.");
                    
                    const cashFlowParams = {
                        periodo: parseInt(periodo),
                        taxaCrescimento: parseFloat(taxaCrescimento) / 100,
                        inflacaoProjetada: parseFloat(inflacao) / 100,
                        taxaJurosProjetada: parseFloat(juros) / 100,
                        receitaMensal: currentResults.parametros?.receitaMensal || 0, // Usar dados da simulação
                        despesasFixas: currentResults.parametros?.despesasFixas || 0,
                        outrosParcelamentos: currentResults.parametros?.outrosParcelamentos || 0,
                        parcelaMensal: currentResults.valorParcela || 0
                    };
                    
                    const cashFlowData = simulator.projectCashFlow(cashFlowParams);
                    this.displayCashFlow(cashFlowData);
                } catch (error) {
                    TAXMASTER.ui.notifications.show(error.message, "error");
                    console.error("Erro na projeção de fluxo de caixa:", error);
                }
            });
        }
    },
    
    getCurrentResults: function() {
        // Função auxiliar para obter os resultados da última simulação bem-sucedida
        // Pode ser armazenado em uma variável do módulo
        return this.lastSimulationResults || null;
    },

    setupTabs: function() {
        TAXMASTER.ui.tabs.init(document.querySelector("#module3-page .tab-container"));
    },

    displayResults: function(results) {
        console.log("Exibindo resultados Módulo III:", results);
        this.lastSimulationResults = results; // Armazenar resultados para uso posterior (fluxo de caixa)
        const resultsContainer = document.getElementById("resultados-simulacao-parcelamento");
        if (!resultsContainer) return;

        resultsContainer.style.display = "block";
        // Preencher campos de resultado
        document.getElementById("resultado-parcelamento-valor-original").textContent = TAXMASTER.utils.formatCurrency(results.valorOriginal);
        document.getElementById("resultado-parcelamento-valor-atualizado").textContent = TAXMASTER.utils.formatCurrency(results.valorAtualizado);
        document.getElementById("resultado-parcelamento-modalidade").textContent = results.modalidadeParcelamento;
        document.getElementById("resultado-parcelamento-entrada").textContent = TAXMASTER.utils.formatCurrency(results.valorEntrada);
        document.getElementById("resultado-parcelamento-valor-parcelado").textContent = TAXMASTER.utils.formatCurrency(results.valorParcelado);
        document.getElementById("resultado-parcelamento-num-parcelas").textContent = results.numeroParcelas;
        document.getElementById("resultado-parcelamento-valor-parcela").textContent = TAXMASTER.utils.formatCurrency(results.valorParcela);
        document.getElementById("resultado-parcelamento-reducao").textContent = TAXMASTER.utils.formatCurrency(results.reducaoTotal);
        document.getElementById("resultado-parcelamento-percentual-reducao").textContent = `${(results.percentualReducao * 100).toFixed(2)}%`;
        
        // Preencher análise de viabilidade (se houver)
        if(results.analiseViabilidade) {
            document.getElementById("resultado-comprometimento").textContent = `${(results.analiseViabilidade.comprometimentoReceita * 100).toFixed(1)}%`;
            document.getElementById("resultado-classificacao-risco").textContent = results.analiseViabilidade.classificacaoRisco;
            document.getElementById("resultado-probabilidade-adimplencia").textContent = `${(results.analiseViabilidade.probabilidadeAdimplencia * 100).toFixed(0)}%`;
            document.getElementById("resultado-recomendacao").textContent = results.analiseViabilidade.recomendacao;
            // Atualizar gauge de viabilidade (requer biblioteca ou implementação)
            this.updateViabilityGauge(results.analiseViabilidade.indiceViabilidade);
        }

        // Preencher tabela de amortização
        const tableBody = document.getElementById("tabela-amortizacao-parcelamento-body");
        if (tableBody && results.tabelaAmortizacao) {
            tableBody.innerHTML = ""; // Limpar tabela anterior
            results.tabelaAmortizacao.forEach(row => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${row.numeroParcela}</td>
                    <td>${TAXMASTER.utils.formatDate(new Date(row.vencimento))}</td>
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
        TAXMASTER.ui.tabs.showTab(document.querySelector("#module3-page .tab-container"), "resultados-parcelamento");
    },
    
    displayCashFlow: function(cashFlowData) {
        const tableBody = document.getElementById("tabela-fluxo-caixa-body");
        const chartCanvas = document.getElementById("grafico-fluxo-caixa");
        if (!tableBody || !chartCanvas || !cashFlowData || !cashFlowData.projecao) return;

        tableBody.innerHTML = ""; // Limpar tabela
        const chartLabels = [];
        const chartDataSaldo = [];
        const chartDataAcumulado = [];

        cashFlowData.projecao.forEach(item => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${item.periodo}</td>
                <td>${TAXMASTER.utils.formatCurrency(item.receitas)}</td>
                <td>${TAXMASTER.utils.formatCurrency(item.despesas)}</td>
                <td>${TAXMASTER.utils.formatCurrency(item.parcelamento)}</td>
                <td class="${item.saldo < 0 ? 'text-danger' : 'text-success'}">${TAXMASTER.utils.formatCurrency(item.saldo)}</td>
                <td class="${item.saldoAcumulado < 0 ? 'text-danger' : 'text-success'}">${TAXMASTER.utils.formatCurrency(item.saldoAcumulado)}</td>
            `;
            tableBody.appendChild(tr);
            
            chartLabels.push(`Mês ${item.periodo}`);
            chartDataSaldo.push(item.saldo);
            chartDataAcumulado.push(item.saldoAcumulado);
        });

        // Gerar gráfico de fluxo de caixa
        const existingChart = Chart.getChart(chartCanvas);
        if (existingChart) existingChart.destroy();
        
        new Chart(chartCanvas.getContext("2d"), {
            type: "line",
            data: {
                labels: chartLabels,
                datasets: [
                    { label: "Saldo Mensal (R$)", data: chartDataSaldo, borderColor: "#007bff", fill: false, tension: 0.1 },
                    { label: "Saldo Acumulado (R$)", data: chartDataAcumulado, borderColor: "#28a745", fill: false, tension: 0.1 }
                ]
            },
            options: {
                responsive: true,
                plugins: { title: { display: true, text: "Projeção de Fluxo de Caixa" } },
                scales: { y: { beginAtZero: false } }
            }
        });
        
        TAXMASTER.ui.notifications.show("Projeção de fluxo de caixa atualizada.", "info");
    },
    
    displayComparison: function(comparisonData) {
        const tableBody = document.getElementById("tabela-comparativo-modalidades-body");
        const chartCanvas = document.getElementById("grafico-comparativo-modalidades");
        const economyChartCanvas = document.getElementById("grafico-economia-modalidades");
        const cashFlowImpactChartCanvas = document.getElementById("grafico-impacto-fluxo");
        
        if (!tableBody || !chartCanvas || !economyChartCanvas || !cashFlowImpactChartCanvas || !comparisonData) return;

        tableBody.innerHTML = ""; // Limpar tabela
        const chartLabels = [];
        const chartDataValor = [];
        const chartDataEconomia = [];
        const chartDataParcela = [];
        const chartDataPrazo = [];

        comparisonData.forEach(item => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${item.modalidade}</td>
                <td>${TAXMASTER.utils.formatCurrency(item.valorFinal)}</td>
                <td>${TAXMASTER.utils.formatCurrency(item.reducaoTotal)} (${(item.percentualReducao * 100).toFixed(1)}%)</td>
                <td>${TAXMASTER.utils.formatCurrency(item.economiaTotal)}</td>
                <td>${TAXMASTER.utils.formatCurrency(item.valorParcela)}</td>
                <td>${item.prazoMaximo}</td>
                <td>${(item.entradaMinima * 100).toFixed(0)}%</td>
                <td>${item.elegivel ? '<span class="badge badge-success">Sim</span>' : '<span class="badge badge-danger">Não</span>'}</td>
                <td><button class="btn btn-sm btn-info select-modality-installment" data-modality="${item.modalidade}">Selecionar</button></td>
            `;
            tableBody.appendChild(tr);
            
            // Dados para os gráficos
            chartLabels.push(item.modalidade);
            chartDataValor.push(item.valorFinal);
            chartDataEconomia.push(item.economiaTotal);
            chartDataParcela.push(item.valorParcela);
            chartDataPrazo.push(item.prazoMaximo);
        });
        
        // Adicionar evento aos botões "Selecionar"
        tableBody.querySelectorAll(".select-modality-installment").forEach(button => {
            button.addEventListener("click", (e) => {
                const modality = e.target.getAttribute("data-modality");
                TAXMASTER.ui.notifications.show(`Modalidade ${modality} selecionada para simulação detalhada.`, "info");
                document.getElementById("modalidade-parcelamento").value = modality;
                // Opcional: Recalcular ou ir para a aba de simulação
                TAXMASTER.ui.tabs.showTab(document.querySelector("#module3-page .tab-container"), "simulacao-parcelamento");
            });
        });

        // Gerar gráficos comparativos
        this.generateComparisonCharts(chartLabels, chartDataValor, chartDataEconomia, chartDataParcela, chartDataPrazo);
    },
    
    generateComparisonCharts: function(labels, dataValor, dataEconomia, dataParcela, dataPrazo) {
        const chartCanvas = document.getElementById("grafico-comparativo-modalidades");
        const economyChartCanvas = document.getElementById("grafico-economia-modalidades");
        const cashFlowImpactChartCanvas = document.getElementById("grafico-impacto-fluxo");

        // Gráfico Principal Comparativo
        const existingChart1 = Chart.getChart(chartCanvas);
        if (existingChart1) existingChart1.destroy();
        new Chart(chartCanvas.getContext("2d"), {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    { label: "Valor Final (R$)", data: dataValor, backgroundColor: "#007bff" },
                    { label: "Economia (R$)", data: dataEconomia, backgroundColor: "#28a745" }
                ]
            },
            options: { responsive: true, plugins: { title: { display: true, text: "Comparativo Geral" } }, scales: { y: { beginAtZero: true } } }
        });

        // Gráfico de Economia
        const existingChart2 = Chart.getChart(economyChartCanvas);
        if (existingChart2) existingChart2.destroy();
        new Chart(economyChartCanvas.getContext("2d"), {
            type: "pie",
            data: {
                labels: labels,
                datasets: [{ label: "Economia (R$)", data: dataEconomia, backgroundColor: ["#28a745", "#17a2b8", "#ffc107", "#dc3545"] }]
            },
            options: { responsive: true, plugins: { title: { display: true, text: "Economia por Modalidade" } } }
        });

        // Gráfico de Impacto no Fluxo (Valor da Parcela)
        const existingChart3 = Chart.getChart(cashFlowImpactChartCanvas);
        if (existingChart3) existingChart3.destroy();
        new Chart(cashFlowImpactChartCanvas.getContext("2d"), {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{ label: "Valor da Parcela (R$)", data: dataParcela, backgroundColor: "#6f42c1" }]
            },
            options: { responsive: true, plugins: { title: { display: true, text: "Impacto no Fluxo (Parcela Mensal)" } }, scales: { y: { beginAtZero: true } } }
        });
    },

    hideResults: function() {
        const resultsContainer = document.getElementById("resultados-simulacao-parcelamento");
        if (resultsContainer) resultsContainer.style.display = "none";
        const cashFlowTableBody = document.getElementById("tabela-fluxo-caixa-body");
        if (cashFlowTableBody) cashFlowTableBody.innerHTML = "";
        const comparisonTableBody = document.getElementById("tabela-comparativo-modalidades-body");
        if (comparisonTableBody) comparisonTableBody.innerHTML = "";
        
        // Limpar gráficos
        const chart1 = Chart.getChart("grafico-fluxo-caixa");
        if (chart1) chart1.destroy();
        const chart2 = Chart.getChart("grafico-comparativo-modalidades");
        if (chart2) chart2.destroy();
        const chart3 = Chart.getChart("grafico-economia-modalidades");
        if (chart3) chart3.destroy();
        const chart4 = Chart.getChart("grafico-impacto-fluxo");
        if (chart4) chart4.destroy();
        const chart5 = Chart.getChart("grafico-composicao-parcelamento");
        if (chart5) chart5.destroy();
        const chart6 = Chart.getChart("grafico-evolucao-saldo");
        if (chart6) chart6.destroy();
        const tableBody = document.getElementById("tabela-amortizacao-parcelamento-body");
        if (tableBody) tableBody.innerHTML = "";
    },

    generateCharts: function(results) {
        // Gráfico de Composição do Parcelamento
        const ctxComposition = document.getElementById("grafico-composicao-parcelamento")?.getContext("2d");
        if (ctxComposition && results.composicaoValorFinal) {
            const existingChart = Chart.getChart(ctxComposition.canvas);
            if (existingChart) existingChart.destroy();
            new Chart(ctxComposition, {
                type: "doughnut",
                data: {
                    labels: ["Principal Pago", "Juros Pagos", "Multa Paga", "Encargos Pagos"],
                    datasets: [{
                        data: [
                            results.composicaoValorFinal.principal || 0,
                            results.composicaoValorFinal.juros || 0,
                            results.composicaoValorFinal.multa || 0,
                            results.composicaoValorFinal.encargos || 0
                        ],
                        backgroundColor: ["#007bff", "#dc3545", "#ffc107", "#6c757d"]
                    }]
                },
                options: { responsive: true, plugins: { title: { display: true, text: "Composição do Valor Final Pago" } } }
            });
        }

        // Gráfico de Evolução do Saldo Devedor
        const ctxEvolution = document.getElementById("grafico-evolucao-saldo")?.getContext("2d");
        if (ctxEvolution && results.tabelaAmortizacao) {
            const existingChart = Chart.getChart(ctxEvolution.canvas);
            if (existingChart) existingChart.destroy();
            const labels = results.tabelaAmortizacao.map(row => row.numeroParcela);
            const dataSaldo = results.tabelaAmortizacao.map(row => row.saldoDevedor);
            new Chart(ctxEvolution, {
                type: "line",
                data: {
                    labels: labels,
                    datasets: [{
                        label: "Saldo Devedor (R$)",
                        data: dataSaldo,
                        borderColor: "#17a2b8",
                        fill: false,
                        tension: 0.1
                    }]
                },
                options: { responsive: true, plugins: { title: { display: true, text: "Evolução do Saldo Devedor" } }, scales: { y: { beginAtZero: false } } }
            });
        }
    },
    
    updateViabilityGauge: function(value) {
        const gaugeElement = document.getElementById("indicador-viabilidade");
        const gaugeValueElement = gaugeElement?.querySelector(".gauge-value");
        if (!gaugeElement || !gaugeValueElement) return;
        
        const percentage = Math.max(0, Math.min(100, (value || 0) * 100));
        gaugeValueElement.textContent = `${percentage.toFixed(0)}%`;
        
        // Implementar lógica visual do gauge (ex: rotação, cor)
        // Exemplo simples com cor de fundo:
        let color = "#dc3545"; // Vermelho (Baixa)
        if (percentage > 70) color = "#28a745"; // Verde (Alta)
        else if (percentage > 40) color = "#ffc107"; // Amarelo (Média)
        gaugeElement.style.setProperty("--gauge-color", color);
        gaugeElement.style.setProperty("--gauge-value-deg", `${percentage * 1.8}deg`); // Mapeia 0-100% para 0-180deg
    },

    setupExportButtons: function(results) {
        const btnPdf = document.getElementById("btn-exportar-pdf-parcelamento");
        const btnExcel = document.getElementById("btn-exportar-excel-parcelamento");
        const btnSave = document.getElementById("btn-salvar-simulacao-parcelamento");

        if (btnPdf) {
            btnPdf.onclick = () => TAXMASTER.reports.exportToPdf("resultados-simulacao-parcelamento", "simulacao_parcelamento.pdf");
        }
        if (btnExcel) {
            btnExcel.onclick = () => TAXMASTER.reports.exportToExcel(results.tabelaAmortizacao, "tabela_amortizacao_parcelamento.xlsx", "Amortização");
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
                modulo: 'module3',
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
            if (simulation && simulation.modulo === 'module3') {
                const form = document.getElementById('simulacao-parcelamento-form');
                TAXMASTER.ui.forms.fill(form, simulation.parametros);
                this.displayResults(simulation.resultados);
                this.displayComparison(simulation.resultados.comparativoModalidades);
                // Carregar fluxo de caixa se os dados estiverem disponíveis
                if(simulation.resultados.fluxoCaixaProjetado) {
                    this.displayCashFlow(simulation.resultados.fluxoCaixaProjetado);
                }
                TAXMASTER.ui.notifications.show('Simulação carregada.', 'info');
            } else {
                TAXMASTER.ui.notifications.show('Simulação não encontrada ou inválida.', 'error');
            }
        }
    }
};

