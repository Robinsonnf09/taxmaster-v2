// TAX MASTER - Módulo IV: Planejamento Tributário Estratégico
// Gerencia a interface e interações do Módulo IV

TAXMASTER.modules.module4 = {
    init: function() {
        console.log("Inicializando Módulo IV");
        this.setupForm();
        this.setupTabs();
        this.setupScenarioConfig();
        this.setupSensitivityAnalysis();
        TAXMASTER.events.trigger("module:initialized", { module: "module4" });
    },

    setupForm: function() {
        const form = document.getElementById("simulacao-estrategica-form");
        if (!form) return;

        form.addEventListener("submit", (e) => {
            e.preventDefault();
            if (!TAXMASTER.ui.forms.validate(form)) return;
            const formData = TAXMASTER.ui.forms.serialize(form);
            // Coletar regimes a comparar e estratégias
            formData.compararRegimes = Array.from(form.querySelectorAll('input[name="compararRegimes[]"]:checked')).map(el => el.value);
            formData.estrategiasAvancadas = Array.from(form.querySelectorAll('input[name="estrategiasAvancadas[]"]:checked')).map(el => el.value);
            
            try {
                const simulator = TAXMASTER.simulators.strategicPlanning; // Assume simulator is globally accessible
                if (!simulator) throw new Error("Simulador do Módulo IV não encontrado.");
                const results = simulator.simulate(formData);
                this.displayResults(results);
            } catch (error) {
                TAXMASTER.ui.notifications.show(error.message, "error");
                console.error("Erro na simulação do Módulo IV:", error);
            }
        });

        form.addEventListener("reset", () => {
            this.hideResults();
        });
    },
    
    setupScenarioConfig: function() {
        const applyButton = document.getElementById("btn-aplicar-cenarios");
        const restoreButton = document.getElementById("btn-restaurar-cenarios");
        
        if (applyButton) {
            applyButton.addEventListener("click", () => {
                const scenarios = this.getScenarioData();
                // Atualizar parâmetros do simulador ou armazenar para uso posterior
                TAXMASTER.simulators.strategicPlanning.setScenarios(scenarios);
                TAXMASTER.ui.notifications.show("Cenários econômicos aplicados.", "info");
                // Opcional: Recalcular simulação se houver resultados
                if (this.lastSimulationResults) {
                    document.getElementById("btn-simular-estrategico").click();
                }
            });
        }
        
        if (restoreButton) {
            restoreButton.addEventListener("click", () => {
                const defaultScenarios = TAXMASTER.simulators.strategicPlanning.getDefaultScenarios();
                this.fillScenarioForm(defaultScenarios);
                TAXMASTER.simulators.strategicPlanning.setScenarios(defaultScenarios);
                TAXMASTER.ui.notifications.show("Cenários restaurados para o padrão.", "info");
            });
        }
        
        // Preencher formulário com cenários padrão inicialmente
        const defaultScenarios = TAXMASTER.simulators.strategicPlanning.getDefaultScenarios();
        this.fillScenarioForm(defaultScenarios);
    },
    
    getScenarioData: function() {
        const scenarios = { otimista: {}, base: {}, pessimista: {} };
        const prefixes = ["otimista", "base", "pessimista"];
        const fields = ["crescimento-pib", "inflacao", "cambio", "selic", "crescimento-setor"];
        
        prefixes.forEach(prefix => {
            fields.forEach(field => {
                const element = document.getElementById(`${prefix}-${field}`);
                if (element) {
                    // Mapear nome do campo para chave do objeto (ex: crescimento-pib -> crescimentoPib)
                    const key = field.replace(/-([a-z])/g, g => g[1].toUpperCase());
                    scenarios[prefix][key] = parseFloat(element.value) || 0;
                }
            });
        });
        return scenarios;
    },
    
    fillScenarioForm: function(scenarios) {
        const prefixes = ["otimista", "base", "pessimista"];
        const fields = ["crescimento-pib", "inflacao", "cambio", "selic", "crescimento-setor"];
        
        prefixes.forEach(prefix => {
            fields.forEach(field => {
                const element = document.getElementById(`${prefix}-${field}`);
                const key = field.replace(/-([a-z])/g, g => g[1].toUpperCase());
                if (element && scenarios[prefix] && scenarios[prefix][key] !== undefined) {
                    element.value = scenarios[prefix][key];
                }
            });
        });
    },
    
    setupSensitivityAnalysis: function() {
        const calculateButton = document.getElementById("btn-calcular-sensibilidade");
        if (calculateButton) {
            calculateButton.addEventListener("click", () => {
                if (!this.lastSimulationResults) {
                    TAXMASTER.ui.notifications.show("Execute uma simulação estratégica primeiro.", "warning");
                    return;
                }
                
                const params = {
                    variavel: document.getElementById("variavel-sensibilidade")?.value,
                    variacaoMinima: parseFloat(document.getElementById("variacao-minima")?.value) / 100,
                    variacaoMaxima: parseFloat(document.getElementById("variacao-maxima")?.value) / 100,
                    passos: parseInt(document.getElementById("passos-variacao")?.value),
                    metrica: document.getElementById("metrica-impacto")?.value,
                    regime: document.getElementById("regime-sensibilidade")?.value,
                    periodo: document.getElementById("periodo-sensibilidade")?.value
                };
                
                try {
                    const simulator = TAXMASTER.simulators.strategicPlanning;
                    if (!simulator || !simulator.analyzeSensitivity) throw new Error("Função de análise de sensibilidade não encontrada.");
                    
                    const sensitivityData = simulator.analyzeSensitivity(this.lastSimulationResults, params);
                    this.displaySensitivityAnalysis(sensitivityData, params.variavel, params.metrica);
                } catch (error) {
                    TAXMASTER.ui.notifications.show(error.message, "error");
                    console.error("Erro na análise de sensibilidade:", error);
                }
            });
        }
    },

    setupTabs: function() {
        TAXMASTER.ui.tabs.init(document.querySelector("#module4-page .tab-container"));
    },

    displayResults: function(results) {
        console.log("Exibindo resultados Módulo IV:", results);
        this.lastSimulationResults = results; // Armazenar para análise de sensibilidade
        const resultsContainer = document.getElementById("resultados-simulacao-estrategica");
        if (!resultsContainer) return;

        resultsContainer.style.display = "block";
        
        // 1. Comparativo entre Regimes
        const comparisonTableBody = document.getElementById("tabela-comparativo-regimes-body");
        if (comparisonTableBody && results.comparativoRegimes) {
            comparisonTableBody.innerHTML = "";
            const chartLabels = [];
            const chartDataCarga = [];
            const chartDataLucro = [];
            results.comparativoRegimes.forEach(regime => {
                const tr = document.createElement("tr");
                const isRecommended = regime.recomendado;
                tr.className = isRecommended ? "table-success" : "";
                tr.innerHTML = `
                    <td>${regime.nome} ${isRecommended ? '<span class="badge badge-success ml-2">Recomendado</span>' : ''}</td>
                    <td>${TAXMASTER.utils.formatCurrency(regime.cargaTributariaTotal)}</td>
                    <td>${(regime.aliquotaEfetiva * 100).toFixed(2)}%</td>
                    <td>${TAXMASTER.utils.formatCurrency(regime.lucroLiquido)}</td>
                    <td>${TAXMASTER.utils.formatCurrency(regime.economiaRelativaBase || 0)}</td>
                    <td>${regime.complexidade}</td>
                    <td>${regime.observacoes || '-'}</td>
                `;
                comparisonTableBody.appendChild(tr);
                chartLabels.push(regime.nome);
                chartDataCarga.push(regime.cargaTributariaTotal);
                chartDataLucro.push(regime.lucroLiquido);
            });
            this.generateRegimeComparisonChart(chartLabels, chartDataCarga, chartDataLucro);
        }
        
        // 2. Projeção de Resultados (para regime recomendado)
        const recommendedRegime = results.comparativoRegimes?.find(r => r.recomendado);
        if (recommendedRegime && recommendedRegime.projecaoAnual) {
            this.displayProjectionResults(recommendedRegime.nome, recommendedRegime.projecaoAnual);
            // Preencher select da projeção
            const regimeSelect = document.getElementById("regime-projecao");
            if(regimeSelect) {
                regimeSelect.innerHTML = "; // Limpar opções
                results.comparativoRegimes.forEach(r => {
                    const option = document.createElement('option');
                    option.value = r.nome;
                    option.textContent = r.nome + (r.recomendado ? ' (Recomendado)' : '');
                    regimeSelect.appendChild(option);
                });
                regimeSelect.value = recommendedRegime.nome;
                regimeSelect.onchange = () => {
                    const selectedRegimeData = results.comparativoRegimes.find(r => r.nome === regimeSelect.value);
                    if(selectedRegimeData) this.displayProjectionResults(selectedRegimeData.nome, selectedRegimeData.projecaoAnual);
                };
            }
        }
        
        // 3. Análise de Cenários
        if (results.analiseCenarios) {
            this.displayScenarioAnalysis(results.analiseCenarios);
             // Preencher select da métrica de cenários
            const metricSelect = document.getElementById("metrica-cenarios");
            if(metricSelect) {
                metricSelect.onchange = () => this.displayScenarioAnalysis(results.analiseCenarios, metricSelect.value);
            }
        }
        
        // 4. Recomendações Estratégicas
        const recommendationsDiv = document.getElementById("recomendacoes-estrategicas");
        if (recommendationsDiv && results.recomendacoes) {
            recommendationsDiv.innerHTML = "";
            results.recomendacoes.forEach(rec => {
                const p = document.createElement("p");
                p.innerHTML = `<strong>${rec.tipo}:</strong> ${rec.descricao}`; // Usar innerHTML se a descrição contiver HTML seguro
                recommendationsDiv.appendChild(p);
            });
        } else if (recommendationsDiv) {
             recommendationsDiv.innerHTML = '<p class="text-center text-muted">Nenhuma recomendação específica gerada para esta simulação.</p>';
        }

        // Configurar botões de exportação
        this.setupExportButtons(results);
        
        // Salvar simulação
        this.saveSimulation(results);
        
        // Mover para a tab de resultados
        TAXMASTER.ui.tabs.showTab(document.querySelector("#module4-page .tab-container"), "resultados-estrategicos");
    },
    
    generateRegimeComparisonChart: function(labels, dataCarga, dataLucro) {
        const chartCanvas = document.getElementById("grafico-comparativo-regimes")?.getContext("2d");
        if (!chartCanvas) return;
        const existingChart = Chart.getChart(chartCanvas.canvas);
        if (existingChart) existingChart.destroy();
        
        new Chart(chartCanvas, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    { label: "Carga Tributária Total (R$)", data: dataCarga, backgroundColor: "#dc3545", yAxisID: 'y' },
                    { label: "Lucro Líquido (R$)", data: dataLucro, backgroundColor: "#28a745", yAxisID: 'y1' }
                ]
            },
            options: {
                responsive: true,
                plugins: { title: { display: true, text: "Comparativo entre Regimes Tributários" } },
                scales: {
                    y: { type: 'linear', display: true, position: 'left', title: { display: true, text: 'Carga Tributária (R$)' } },
                    y1: { type: 'linear', display: true, position: 'right', title: { display: true, text: 'Lucro Líquido (R$)' }, grid: { drawOnChartArea: false } }
                }
            }
        });
    },
    
    displayProjectionResults: function(regimeNome, projecaoAnual) {
        const tableBody = document.getElementById("tabela-projecao-body");
        const chartCanvas = document.getElementById("grafico-projecao-resultados")?.getContext("2d");
        if (!tableBody || !chartCanvas || !projecaoAnual) return;
        
        tableBody.innerHTML = "";
        const chartLabels = [];
        const chartDataFaturamento = [];
        const chartDataLucro = [];
        const chartDataTributos = [];
        
        projecaoAnual.forEach(ano => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${ano.ano}</td>
                <td>${TAXMASTER.utils.formatCurrency(ano.faturamento)}</td>
                <td>${TAXMASTER.utils.formatCurrency(ano.lucroBruto)}</td>
                <td>${TAXMASTER.utils.formatCurrency(ano.tributos)}</td>
                <td>${TAXMASTER.utils.formatCurrency(ano.lucroLiquido)}</td>
                <td>${(ano.aliquotaEfetiva * 100).toFixed(2)}%</td>
            `;
            tableBody.appendChild(tr);
            chartLabels.push(`Ano ${ano.ano}`);
            chartDataFaturamento.push(ano.faturamento);
            chartDataLucro.push(ano.lucroLiquido);
            chartDataTributos.push(ano.tributos);
        });
        
        // Gerar gráfico de projeção
        const existingChart = Chart.getChart(chartCanvas.canvas);
        if (existingChart) existingChart.destroy();
        new Chart(chartCanvas, {
            type: "line",
            data: {
                labels: chartLabels,
                datasets: [
                    { label: "Faturamento (R$)", data: chartDataFaturamento, borderColor: "#007bff", fill: false },
                    { label: "Lucro Líquido (R$)", data: chartDataLucro, borderColor: "#28a745", fill: false },
                    { label: "Tributos (R$)", data: chartDataTributos, borderColor: "#dc3545", fill: false }
                ]
            },
            options: { responsive: true, plugins: { title: { display: true, text: `Projeção de Resultados - ${regimeNome}` } }, scales: { y: { beginAtZero: false } } }
        });
    },
    
    displayScenarioAnalysis: function(scenarioData, metric = 'carga-tributaria') {
        const chartCanvas = document.getElementById("grafico-analise-cenarios")?.getContext("2d");
        if (!chartCanvas || !scenarioData) return;
        
        const scenarios = ["otimista", "base", "pessimista"];
        const labels = scenarios.map(s => s.charAt(0).toUpperCase() + s.slice(1)); // Capitalize
        let data = [];
        let chartTitle = "Análise de Cenários";
        let dataKey = 'cargaTributaria'; // Default key

        switch(metric) {
            case 'lucro-liquido':
                dataKey = 'lucroLiquido';
                chartTitle = "Análise de Cenários - Lucro Líquido";
                break;
            case 'roi':
                dataKey = 'roi'; // Assuming ROI is calculated and available
                chartTitle = "Análise de Cenários - ROI";
                break;
            case 'carga-tributaria':
            default:
                dataKey = 'cargaTributaria';
                chartTitle = "Análise de Cenários - Carga Tributária";
                break;
        }
        
        data = scenarios.map(s => scenarioData[s]?.[dataKey] || 0);
        const valorEsperado = scenarioData.valorEsperado?.[dataKey] || 0;
        const valorBase = scenarioData.base?.[dataKey] || 0;

        // Atualizar tabela
        scenarios.forEach(s => {
            document.getElementById(`cenario-${s}-valor`).textContent = TAXMASTER.utils.formatCurrency(scenarioData[s]?.[dataKey] || 0);
            const variacao = valorBase !== 0 ? ((scenarioData[s]?.[dataKey] || 0) / valorBase - 1) * 100 : 0;
            document.getElementById(`cenario-${s}-variacao`).textContent = s === 'base' ? '-' : `${variacao.toFixed(1)}%`;
            document.getElementById(`cenario-${s}-probabilidade`).textContent = `${(scenarioData[s]?.probabilidade || 0) * 100}%`;
        });
        document.getElementById("cenario-esperado-valor").textContent = TAXMASTER.utils.formatCurrency(valorEsperado);
        const variacaoEsperada = valorBase !== 0 ? (valorEsperado / valorBase - 1) * 100 : 0;
        document.getElementById("cenario-esperado-variacao").textContent = `${variacaoEsperada.toFixed(1)}%`;

        // Gerar gráfico
        const existingChart = Chart.getChart(chartCanvas.canvas);
        if (existingChart) existingChart.destroy();
        new Chart(chartCanvas, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: `Valor ${metric.replace('-', ' ')} (R$)`,
                    data: data,
                    backgroundColor: ["#28a745", "#007bff", "#dc3545"]
                }]
            },
            options: { responsive: true, plugins: { title: { display: true, text: chartTitle } }, scales: { y: { beginAtZero: false } } }
        });
    },
    
    displaySensitivityAnalysis: function(sensitivityData, variable, metric) {
        const tableBody = document.getElementById("tabela-sensibilidade-body");
        const chartCanvas = document.getElementById("grafico-sensibilidade")?.getContext("2d");
        if (!tableBody || !chartCanvas || !sensitivityData) return;

        tableBody.innerHTML = "";
        const chartLabels = [];
        const chartDataImpact = [];

        sensitivityData.forEach(item => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${(item.variacao * 100).toFixed(1)}%</td>
                <td>${TAXMASTER.utils.formatCurrency(item.valorBase)}</td>
                <td>${TAXMASTER.utils.formatCurrency(item.valorImpactado)}</td>
                <td>${(item.variacaoImpacto * 100).toFixed(1)}%</td>
                <td>${item.elasticidade?.toFixed(2) || '-'}</td>
            `;
            tableBody.appendChild(tr);
            chartLabels.push(`${(item.variacao * 100).toFixed(1)}%`);
            chartDataImpact.push(item.valorImpactado);
        });

        // Gerar gráfico de sensibilidade
        const existingChart = Chart.getChart(chartCanvas.canvas);
        if (existingChart) existingChart.destroy();
        new Chart(chartCanvas, {
            type: "line",
            data: {
                labels: chartLabels,
                datasets: [{
                    label: `Impacto em ${metric.replace('-', ' ')} (R$)`,
                    data: chartDataImpact,
                    borderColor: "#6f42c1",
                    fill: false,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: { title: { display: true, text: `Análise de Sensibilidade - ${variable} vs ${metric}` } },
                scales: { y: { beginAtZero: false } }
            }
        });
        TAXMASTER.ui.notifications.show("Análise de sensibilidade calculada.", "info");
    },

    hideResults: function() {
        const resultsContainer = document.getElementById("resultados-simulacao-estrategica");
        if (resultsContainer) resultsContainer.style.display = "none";
        const sensitivityTableBody = document.getElementById("tabela-sensibilidade-body");
        if (sensitivityTableBody) sensitivityTableBody.innerHTML = "";
        
        // Limpar gráficos
        const chart1 = Chart.getChart("grafico-comparativo-regimes");
        if (chart1) chart1.destroy();
        const chart2 = Chart.getChart("grafico-projecao-resultados");
        if (chart2) chart2.destroy();
        const chart3 = Chart.getChart("grafico-analise-cenarios");
        if (chart3) chart3.destroy();
        const chart4 = Chart.getChart("grafico-sensibilidade");
        if (chart4) chart4.destroy();
    },

    setupExportButtons: function(results) {
        const btnPdf = document.getElementById("btn-exportar-pdf-estrategico");
        const btnExcel = document.getElementById("btn-exportar-excel-estrategico");
        const btnSave = document.getElementById("btn-salvar-simulacao-estrategica");

        if (btnPdf) {
            btnPdf.onclick = () => TAXMASTER.reports.exportToPdf("resultados-simulacao-estrategica", "planejamento_estrategico.pdf");
        }
        if (btnExcel) {
            // Exportar dados relevantes para Excel (ex: comparativo, projeção)
            btnExcel.onclick = () => {
                const sheets = {};
                if(results.comparativoRegimes) sheets["Comparativo Regimes"] = results.comparativoRegimes;
                const recommended = results.comparativoRegimes?.find(r => r.recomendado);
                if(recommended?.projecaoAnual) sheets["Projecao Recomendada"] = recommended.projecaoAnual;
                if(Object.keys(sheets).length > 0) {
                    TAXMASTER.reports.exportMultipleSheetsToExcel(sheets, "planejamento_estrategico.xlsx");
                } else {
                    TAXMASTER.ui.notifications.show("Não há dados suficientes para exportar para Excel.", "warning");
                }
            };
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
                modulo: 'module4',
                data: new Date().toISOString(),
                parametros: results.parametros,
                resultados: results // Salvar todos os resultados complexos
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
            if (simulation && simulation.modulo === 'module4') {
                const form = document.getElementById('simulacao-estrategica-form');
                TAXMASTER.ui.forms.fill(form, simulation.parametros);
                // Preencher checkboxes de regimes e estratégias
                simulation.parametros.compararRegimes?.forEach(val => { 
                    const el = form.querySelector(`input[name="compararRegimes[]"][value="${val}"]`);
                    if(el) el.checked = true;
                });
                 simulation.parametros.estrategiasAvancadas?.forEach(val => { 
                    const el = form.querySelector(`input[name="estrategiasAvancadas[]"][value="${val}"]`);
                    if(el) el.checked = true;
                });
                
                this.displayResults(simulation.resultados);
                TAXMASTER.ui.notifications.show('Simulação carregada.', 'info');
            } else {
                TAXMASTER.ui.notifications.show('Simulação não encontrada ou inválida.', 'error');
            }
        }
    }
};

