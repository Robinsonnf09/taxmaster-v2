// Módulo de exportação de relatórios para o TAX MASTER
// Implementa funções para exportar simulações em diferentes formatos

TAXMASTER.reports = {
    // Formatos suportados
    formats: ['html', 'csv', 'pdf', 'excel', 'json'],
    
    // Inicialização do módulo
    init: function() {
        console.log('Inicializando módulo de exportação de relatórios');
        
        // Verificar disponibilidade de bibliotecas externas
        this.checkDependencies();
        
        // Registrar eventos
        this.registerEvents();
    },
    
    // Verificar dependências externas
    checkDependencies: function() {
        // Verificar html2pdf
        this.html2pdfAvailable = typeof html2pdf !== 'undefined';
        if (!this.html2pdfAvailable) {
            console.warn('Biblioteca html2pdf não encontrada. Exportação para PDF será limitada.');
        }
        
        // Verificar jspdf
        this.jspdfAvailable = typeof jsPDF !== 'undefined';
        if (!this.jspdfAvailable && !this.html2pdfAvailable) {
            console.warn('Nenhuma biblioteca de PDF encontrada. Exportação para PDF não estará disponível.');
        }
        
        // Verificar xlsx
        this.xlsxAvailable = typeof XLSX !== 'undefined';
        if (!this.xlsxAvailable) {
            console.warn('Biblioteca xlsx não encontrada. Exportação para Excel será limitada.');
        }
        
        // Verificar Chart.js
        this.chartjsAvailable = typeof Chart !== 'undefined';
        if (!this.chartjsAvailable) {
            console.warn('Biblioteca Chart.js não encontrada. Gráficos nos relatórios serão limitados.');
        }
    },
    
    // Registrar eventos
    registerEvents: function() {
        // Registrar evento para botões de exportação
        document.addEventListener('click', function(e) {
            // Verificar se é um botão de exportação
            if (e.target && e.target.classList.contains('export-btn')) {
                const format = e.target.getAttribute('data-format');
                const moduleId = e.target.getAttribute('data-module');
                const simulationId = e.target.getAttribute('data-simulation');
                
                if (format && moduleId) {
                    // Obter dados da simulação atual ou do histórico
                    let simulationData;
                    
                    if (simulationId) {
                        // Obter simulação específica do histórico
                        const userId = TAXMASTER.auth.getCurrentUser()?.id || 'guest';
                        const simulations = TAXMASTER.storage.getSimulations(userId);
                        simulationData = simulations.find(sim => sim.id === simulationId)?.resultados;
                        
                        if (simulationData && typeof simulationData === 'string') {
                            simulationData = JSON.parse(simulationData);
                        }
                    } else {
                        // Obter simulação atual do módulo
                        simulationData = TAXMASTER.modules[moduleId].currentSimulation;
                    }
                    
                    if (simulationData) {
                        // Exportar simulação no formato solicitado
                        TAXMASTER.reports.exportSimulation(simulationData, format, moduleId);
                    } else {
                        TAXMASTER.ui.notifications.show('Nenhuma simulação disponível para exportação', 'error');
                    }
                }
            }
        });
    },
    
    // Exportar simulação em formato específico
    exportSimulation: function(simulationData, format, moduleId) {
        // Verificar formato suportado
        if (!this.formats.includes(format)) {
            TAXMASTER.ui.notifications.show(`Formato de exportação '${format}' não suportado`, 'error');
            return false;
        }
        
        // Gerar nome do arquivo
        const timestamp = new Date().toISOString().split('T')[0];
        let filename = `tax_master_${moduleId}_${timestamp}`;
        
        // Exportar no formato solicitado
        switch (format) {
            case 'html':
                return this.exportToHtml(simulationData, moduleId, `${filename}.html`);
            case 'csv':
                return this.exportToCsv(simulationData, moduleId, `${filename}.csv`);
            case 'pdf':
                return this.exportToPdf(simulationData, moduleId, `${filename}.pdf`);
            case 'excel':
                return this.exportToExcel(simulationData, moduleId, `${filename}.xlsx`);
            case 'json':
                return this.exportToJson(simulationData, moduleId, `${filename}.json`);
            default:
                TAXMASTER.ui.notifications.show(`Formato de exportação '${format}' não implementado`, 'error');
                return false;
        }
    },
    
    // Exportar para HTML
    exportToHtml: function(simulationData, moduleId, filename) {
        try {
            // Gerar HTML do relatório
            const html = this.generateHtmlReport(simulationData, moduleId);
            
            // Criar blob e link para download
            const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            
            // Criar link e simular clique
            this.downloadFile(url, filename);
            
            // Notificar usuário
            TAXMASTER.ui.notifications.show('Relatório HTML exportado com sucesso', 'success');
            return true;
        } catch (error) {
            console.error('Erro ao exportar para HTML:', error);
            TAXMASTER.ui.notifications.show('Erro ao exportar relatório HTML', 'error');
            return false;
        }
    },
    
    // Exportar para CSV
    exportToCsv: function(simulationData, moduleId, filename) {
        try {
            // Gerar CSV do relatório
            const csv = this.generateCsvReport(simulationData, moduleId);
            
            // Criar blob e link para download
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            
            // Criar link e simular clique
            this.downloadFile(url, filename);
            
            // Notificar usuário
            TAXMASTER.ui.notifications.show('Relatório CSV exportado com sucesso', 'success');
            return true;
        } catch (error) {
            console.error('Erro ao exportar para CSV:', error);
            TAXMASTER.ui.notifications.show('Erro ao exportar relatório CSV', 'error');
            return false;
        }
    },
    
    // Exportar para PDF
    exportToPdf: function(simulationData, moduleId, filename) {
        try {
            // Verificar disponibilidade de bibliotecas
            if (!this.html2pdfAvailable && !this.jspdfAvailable) {
                TAXMASTER.ui.notifications.show('Exportação para PDF não disponível. Bibliotecas necessárias não encontradas.', 'error');
                return false;
            }
            
            // Notificar usuário que a exportação está em andamento
            TAXMASTER.ui.notifications.show('Gerando PDF, aguarde...', 'info');
            
            // Gerar HTML do relatório
            const html = this.generateHtmlReport(simulationData, moduleId);
            
            // Método preferencial: html2pdf
            if (this.html2pdfAvailable) {
                // Criar elemento temporário
                const element = document.createElement('div');
                element.innerHTML = html;
                document.body.appendChild(element);
                
                // Configurar opções
                const options = {
                    margin: 10,
                    filename: filename,
                    image: { type: 'jpeg', quality: 0.98 },
                    html2canvas: { scale: 2 },
                    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
                };
                
                // Gerar PDF
                html2pdf().from(element).set(options).save().then(() => {
                    // Remover elemento temporário
                    document.body.removeChild(element);
                    
                    // Notificar usuário
                    TAXMASTER.ui.notifications.show('Relatório PDF exportado com sucesso', 'success');
                });
                
                return true;
            }
            // Método alternativo: jsPDF
            else if (this.jspdfAvailable) {
                // Criar documento PDF
                const doc = new jsPDF();
                
                // Adicionar conteúdo
                doc.html(html, {
                    callback: function(doc) {
                        // Salvar PDF
                        doc.save(filename);
                        
                        // Notificar usuário
                        TAXMASTER.ui.notifications.show('Relatório PDF exportado com sucesso', 'success');
                    },
                    x: 10,
                    y: 10
                });
                
                return true;
            }
        } catch (error) {
            console.error('Erro ao exportar para PDF:', error);
            TAXMASTER.ui.notifications.show('Erro ao exportar relatório PDF', 'error');
            return false;
        }
    },
    
    // Exportar para Excel
    exportToExcel: function(simulationData, moduleId, filename) {
        try {
            // Verificar disponibilidade da biblioteca
            if (!this.xlsxAvailable) {
                TAXMASTER.ui.notifications.show('Exportação para Excel não disponível. Biblioteca necessária não encontrada.', 'error');
                return false;
            }
            
            // Gerar dados para Excel
            const data = this.generateExcelData(simulationData, moduleId);
            
            // Criar workbook
            const wb = XLSX.utils.book_new();
            
            // Adicionar worksheets
            Object.keys(data).forEach(sheetName => {
                const ws = XLSX.utils.json_to_sheet(data[sheetName]);
                XLSX.utils.book_append_sheet(wb, ws, sheetName);
            });
            
            // Exportar workbook
            XLSX.writeFile(wb, filename);
            
            // Notificar usuário
            TAXMASTER.ui.notifications.show('Relatório Excel exportado com sucesso', 'success');
            return true;
        } catch (error) {
            console.error('Erro ao exportar para Excel:', error);
            TAXMASTER.ui.notifications.show('Erro ao exportar relatório Excel', 'error');
            return false;
        }
    },
    
    // Exportar para JSON
    exportToJson: function(simulationData, moduleId, filename) {
        try {
            // Converter para string JSON formatada
            const json = JSON.stringify(simulationData, null, 2);
            
            // Criar blob e link para download
            const blob = new Blob([json], { type: 'application/json;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            
            // Criar link e simular clique
            this.downloadFile(url, filename);
            
            // Notificar usuário
            TAXMASTER.ui.notifications.show('Relatório JSON exportado com sucesso', 'success');
            return true;
        } catch (error) {
            console.error('Erro ao exportar para JSON:', error);
            TAXMASTER.ui.notifications.show('Erro ao exportar relatório JSON', 'error');
            return false;
        }
    },
    
    // Função auxiliar para download de arquivo
    downloadFile: function(url, filename) {
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        // Limpar
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);
    },
    
    // Gerar relatório HTML
    generateHtmlReport: function(simulationData, moduleId) {
        // Obter template específico do módulo
        let template;
        
        switch (moduleId) {
            case 'module1':
                template = this.templates.module1.html;
                break;
            case 'module2':
                template = this.templates.module2.html;
                break;
            case 'module3':
                template = this.templates.module3.html;
                break;
            case 'module4':
                template = this.templates.module4.html;
                break;
            default:
                template = this.templates.default.html;
        }
        
        // Substituir placeholders com dados da simulação
        let html = template;
        
        // Substituir placeholders básicos
        html = html.replace(/\{\{timestamp\}\}/g, new Date().toLocaleString());
        html = html.replace(/\{\{moduleId\}\}/g, moduleId);
        
        // Substituir placeholders específicos do módulo
        html = this.replacePlaceholders(html, simulationData);
        
        return html;
    },
    
    // Gerar relatório CSV
    generateCsvReport: function(simulationData, moduleId) {
        // Obter template específico do módulo
        let template;
        
        switch (moduleId) {
            case 'module1':
                template = this.templates.module1.csv;
                break;
            case 'module2':
                template = this.templates.module2.csv;
                break;
            case 'module3':
                template = this.templates.module3.csv;
                break;
            case 'module4':
                template = this.templates.module4.csv;
                break;
            default:
                template = this.templates.default.csv;
        }
        
        // Substituir placeholders com dados da simulação
        let csv = template;
        
        // Substituir placeholders básicos
        csv = csv.replace(/\{\{timestamp\}\}/g, new Date().toLocaleString());
        csv = csv.replace(/\{\{moduleId\}\}/g, moduleId);
        
        // Substituir placeholders específicos do módulo
        csv = this.replacePlaceholders(csv, simulationData);
        
        return csv;
    },
    
    // Gerar dados para Excel
    generateExcelData: function(simulationData, moduleId) {
        // Dados para Excel (objeto com worksheets)
        const data = {
            'Resumo': []
        };
        
        // Adicionar dados básicos ao resumo
        data['Resumo'].push({
            'Data da Simulação': new Date().toLocaleString(),
            'Módulo': this.getModuleName(moduleId)
        });
        
        // Adicionar dados específicos do módulo
        switch (moduleId) {
            case 'module1':
                // Transação Tributária Básica
                data['Resumo'].push({
                    'Valor da Dívida': TAXMASTER.utils.formatCurrency(simulationData.valorDivida),
                    'Modalidade': simulationData.modalidade,
                    'Valor Após Descontos': TAXMASTER.utils.formatCurrency(simulationData.valorAposDescontos),
                    'Economia Total': TAXMASTER.utils.formatCurrency(simulationData.economiaTotal),
                    'Percentual de Economia': (simulationData.percentualEconomia * 100).toFixed(2) + '%'
                });
                
                // Adicionar tabela de amortização
                if (simulationData.tabelaAmortizacao && simulationData.tabelaAmortizacao.length > 0) {
                    data['Tabela de Amortização'] = simulationData.tabelaAmortizacao.map(row => ({
                        'Parcela': row.numeroParcela,
                        'Valor da Parcela': row.valorParcela,
                        'Juros': row.juros,
                        'Amortização': row.amortizacao,
                        'Saldo Devedor': row.saldoDevedor
                    }));
                }
                break;
                
            case 'module2':
                // Transação Tributária Avançada
                data['Resumo'].push({
                    'Valor da Dívida': TAXMASTER.utils.formatCurrency(simulationData.valorDivida),
                    'Modalidade': simulationData.modalidade,
                    'Valor Após Descontos': TAXMASTER.utils.formatCurrency(simulationData.valorAposDescontos),
                    'Economia Total': TAXMASTER.utils.formatCurrency(simulationData.economiaTotal),
                    'Percentual de Economia': (simulationData.percentualEconomia * 100).toFixed(2) + '%',
                    'Capacidade de Pagamento': TAXMASTER.utils.formatCurrency(simulationData.capacidadePagamento),
                    'Risco': simulationData.classificacaoRisco
                });
                
                // Adicionar análise de capacidade
                if (simulationData.analiseCapacidade) {
                    data['Análise de Capacidade'] = [
                        {
                            'Receita Mensal': TAXMASTER.utils.formatCurrency(simulationData.analiseCapacidade.receitaMensal),
                            'Despesas Mensais': TAXMASTER.utils.formatCurrency(simulationData.analiseCapacidade.despesasMensais),
                            'Fluxo de Caixa Líquido': TAXMASTER.utils.formatCurrency(simulationData.analiseCapacidade.fluxoCaixaLiquido),
                            'Impacto da Parcela': (simulationData.analiseCapacidade.impactoParcela * 100).toFixed(2) + '%',
                            'Classificação de Risco': simulationData.analiseCapacidade.classificacaoRisco
                        }
                    ];
                }
                
                // Adicionar comparativo entre modalidades
                if (simulationData.comparativoModalidades && simulationData.comparativoModalidades.length > 0) {
                    data['Comparativo de Modalidades'] = simulationData.comparativoModalidades.map(modalidade => ({
                        'Modalidade': modalidade.modalidade,
                        'Valor Final': modalidade.valorFinal,
                        'Economia': modalidade.economia,
                        'Percentual de Economia': (modalidade.percentualEconomia * 100).toFixed(2) + '%',
                        'Elegível': modalidade.elegivel ? 'Sim' : 'Não'
                    }));
                }
                break;
                
            case 'module3':
                // Parcelamento e Redução de Débitos
                data['Resumo'].push({
                    'Modalidade': simulationData.modalidade,
                    'Valor Original': TAXMASTER.utils.formatCurrency(simulationData.valorOriginal),
                    'Valor Após Descontos': TAXMASTER.utils.formatCurrency(simulationData.valorAposDescontos),
                    'Economia Total': TAXMASTER.utils.formatCurrency(simulationData.economiaTotal),
                    'Percentual de Economia': (simulationData.percentualEconomia * 100).toFixed(2) + '%',
                    'Valor da Entrada': TAXMASTER.utils.formatCurrency(simulationData.valorEntrada),
                    'Valor Parcelado': TAXMASTER.utils.formatCurrency(simulationData.valorParcelado),
                    'Número de Parcelas': simulationData.numeroParcelas,
                    'Valor da Parcela': TAXMASTER.utils.formatCurrency(simulationData.valorParcela)
                });
                
                // Adicionar análise de fluxo de caixa
                if (simulationData.analiseFluxoCaixa) {
                    data['Análise de Fluxo de Caixa'] = [
                        {
                            'Receita Mensal': TAXMASTER.utils.formatCurrency(simulationData.analiseFluxoCaixa.receitaMensal),
                            'Despesas Mensais': TAXMASTER.utils.formatCurrency(simulationData.analiseFluxoCaixa.despesasMensais),
                            'Fluxo de Caixa Líquido': TAXMASTER.utils.formatCurrency(simulationData.analiseFluxoCaixa.fluxoCaixaLiquido),
                            'Impacto da Parcela': (simulationData.analiseFluxoCaixa.impactoParcela * 100).toFixed(2) + '%',
                            'Classificação de Risco': simulationData.analiseFluxoCaixa.classificacaoRisco,
                            'Recomendação': simulationData.analiseFluxoCaixa.recomendacao
                        }
                    ];
                }
                
                // Adicionar tabela de amortização
                if (simulationData.tabelaAmortizacao && simulationData.tabelaAmortizacao.length > 0) {
                    data['Tabela de Amortização'] = simulationData.tabelaAmortizacao.map(row => ({
                        'Parcela': row.numeroParcela,
                        'Valor da Parcela': row.valorParcela,
                        'Juros': row.juros,
                        'Amortização': row.amortizacao,
                        'Saldo Devedor': row.saldoDevedor
                    }));
                }
                break;
                
            case 'module4':
                // Planejamento Tributário Estratégico
                data['Resumo'].push({
                    'Cenário Econômico': simulationData.cenarioEconomico,
                    'Horizonte de Planejamento': simulationData.horizontePlanejamento + ' anos',
                    'Faturamento Anual': TAXMASTER.utils.formatCurrency(simulationData.faturamentoAnual),
                    'Regime Tributário Atual': simulationData.regimeTributarioAtual,
                    'Regime Tributário Recomendado': simulationData.regimeTributarioRecomendado,
                    'Economia Tributária Total': TAXMASTER.utils.formatCurrency(simulationData.economiaTributariaTotal),
                    'Percentual de Economia': (simulationData.percentualEconomia * 100).toFixed(2) + '%',
                    'ROI do Planejamento': (simulationData.roiPlanejamentoTributario * 100).toFixed(2) + '%'
                });
                
                // Adicionar projeções anuais
                if (simulationData.projecoesAnuais && simulationData.projecoesAnuais.length > 0) {
                    data['Projeções Anuais'] = simulationData.projecoesAnuais.map(ano => ({
                        'Ano': ano.ano,
                        'Faturamento Projetado': ano.faturamentoProjetado,
                        'Tributos (Regime Atual)': ano.tributosRegimeAtual,
                        'Tributos (Regime Recomendado)': ano.tributosRegimeRecomendado,
                        'Economia Anual': ano.economiaTributaria
                    }));
                }
                
                // Adicionar análise de sensibilidade
                if (simulationData.analiseSensibilidade && simulationData.analiseSensibilidade.length > 0) {
                    data['Análise de Sensibilidade'] = simulationData.analiseSensibilidade.map(analise => {
                        const diferenca = analise.economiaTributaria - simulationData.economiaTributariaTotal;
                        const impactoPercentual = diferenca / simulationData.economiaTributariaTotal;
                        
                        return {
                            'Parâmetro': analise.parametro,
                            'Variação': analise.variacao,
                            'Economia Tributária': analise.economiaTributaria,
                            'Diferença': diferenca,
                            'Impacto': (impactoPercentual * 100).toFixed(2) + '%'
                        };
                    });
                }
                
                // Adicionar recomendações estratégicas
                if (simulationData.recomendacoesEstrategicas && simulationData.recomendacoesEstrategicas.length > 0) {
                    data['Recomendações Estratégicas'] = simulationData.recomendacoesEstrategicas.map(recomendacao => ({
                        'Título': recomendacao.titulo,
                        'Descrição': recomendacao.descricao,
                        'Prioridade': recomendacao.prioridade,
                        'Impacto': recomendacao.impacto,
                        'Complexidade': recomendacao.complexidade
                    }));
                }
                break;
                
            default:
                // Dados genéricos
                data['Resumo'].push({
                    'Tipo de Simulação': 'Genérica',
                    'Dados': JSON.stringify(simulationData)
                });
        }
        
        return data;
    },
    
    // Substituir placeholders em templates
    replacePlaceholders: function(template, data) {
        // Função recursiva para substituir placeholders em objetos aninhados
        const replacePlaceholder = (template, path, value) => {
            const placeholder = `{{${path}}}`;
            
            // Substituir placeholder direto
            if (template.includes(placeholder)) {
                // Formatar valor conforme tipo
                let formattedValue = value;
                
                if (typeof value === 'number') {
                    // Verificar se é valor monetário (baseado no nome do campo)
                    if (path.toLowerCase().includes('valor') || 
                        path.toLowerCase().includes('economia') || 
                        path.toLowerCase().includes('tributo') || 
                        path.toLowerCase().includes('parcela')) {
                        formattedValue = TAXMASTER.utils.formatCurrency(value);
                    } 
                    // Verificar se é percentual
                    else if (path.toLowerCase().includes('percentual') || 
                             path.toLowerCase().includes('taxa') || 
                             path.toLowerCase().includes('aliquota') || 
                             path.toLowerCase().includes('impacto')) {
                        formattedValue = (value * 100).toFixed(2) + '%';
                    }
                    // Outros números
                    else {
                        formattedValue = value.toString();
                    }
                } else if (value === null || value === undefined) {
                    formattedValue = 'N/A';
                } else if (typeof value === 'boolean') {
                    formattedValue = value ? 'Sim' : 'Não';
                } else if (Array.isArray(value)) {
                    formattedValue = JSON.stringify(value);
                } else if (typeof value === 'object') {
                    formattedValue = JSON.stringify(value);
                }
                
                // Substituir no template
                template = template.replace(new RegExp(placeholder, 'g'), formattedValue);
            }
            
            return template;
        };
        
        // Função para processar objeto recursivamente
        const processObject = (obj, parentPath = '') => {
            for (const key in obj) {
                if (obj.hasOwnProperty(key)) {
                    const value = obj[key];
                    const currentPath = parentPath ? `${parentPath}.${key}` : key;
                    
                    // Substituir placeholder para este campo
                    template = replacePlaceholder(template, currentPath, value);
                    
                    // Processar recursivamente se for objeto
                    if (value !== null && typeof value === 'object' && !Array.isArray(value)) {
                        processObject(value, currentPath);
                    }
                    // Processar arrays de objetos
                    else if (Array.isArray(value) && value.length > 0 && typeof value[0] === 'object') {
                        // Verificar se há placeholders para itens de array
                        const arrayPlaceholder = `{{#each ${currentPath}}}`;
                        const arrayEndPlaceholder = `{{/each}}`;
                        
                        if (template.includes(arrayPlaceholder) && template.includes(arrayEndPlaceholder)) {
                            // Extrair template do item
                            const startIdx = template.indexOf(arrayPlaceholder) + arrayPlaceholder.length;
                            const endIdx = template.indexOf(arrayEndPlaceholder);
                            const itemTemplate = template.substring(startIdx, endIdx);
                            
                            // Gerar HTML para cada item
                            let itemsHtml = '';
                            value.forEach((item, index) => {
                                let itemHtml = itemTemplate;
                                
                                // Substituir placeholders específicos do item
                                for (const itemKey in item) {
                                    if (item.hasOwnProperty(itemKey)) {
                                        const itemValue = item[itemKey];
                                        const itemPath = `${currentPath}[${index}].${itemKey}`;
                                        const itemPlaceholder = `{{${itemKey}}}`;
                                        
                                        // Formatar valor
                                        let formattedValue = itemValue;
                                        
                                        if (typeof itemValue === 'number') {
                                            if (itemKey.toLowerCase().includes('valor') || 
                                                itemKey.toLowerCase().includes('economia') || 
                                                itemKey.toLowerCase().includes('tributo') || 
                                                itemKey.toLowerCase().includes('parcela')) {
                                                formattedValue = TAXMASTER.utils.formatCurrency(itemValue);
                                            } else if (itemKey.toLowerCase().includes('percentual') || 
                                                      itemKey.toLowerCase().includes('taxa') || 
                                                      itemKey.toLowerCase().includes('aliquota') || 
                                                      itemKey.toLowerCase().includes('impacto')) {
                                                formattedValue = (itemValue * 100).toFixed(2) + '%';
                                            } else {
                                                formattedValue = itemValue.toString();
                                            }
                                        } else if (itemValue === null || itemValue === undefined) {
                                            formattedValue = 'N/A';
                                        } else if (typeof itemValue === 'boolean') {
                                            formattedValue = itemValue ? 'Sim' : 'Não';
                                        }
                                        
                                        // Substituir no template do item
                                        itemHtml = itemHtml.replace(new RegExp(itemPlaceholder, 'g'), formattedValue);
                                    }
                                }
                                
                                // Adicionar ao HTML de itens
                                itemsHtml += itemHtml;
                            });
                            
                            // Substituir seção de array no template principal
                            template = template.replace(
                                template.substring(template.indexOf(arrayPlaceholder), template.indexOf(arrayEndPlaceholder) + arrayEndPlaceholder.length),
                                itemsHtml
                            );
                        }
                    }
                }
            }
        };
        
        // Processar objeto de dados
        processObject(data);
        
        return template;
    },
    
    // Obter nome do módulo
    getModuleName: function(moduleId) {
        switch (moduleId) {
            case 'module1':
                return 'Transação Tributária Básica';
            case 'module2':
                return 'Transação Tributária Avançada';
            case 'module3':
                return 'Parcelamento e Redução de Débitos';
            case 'module4':
                return 'Planejamento Tributário Estratégico';
            default:
                return 'Módulo Desconhecido';
        }
    },
    
    // Templates para relatórios
    templates: {
        // Template padrão
        default: {
            html: `
<!DOCTYPE html>
<html>
<head>
    <title>Relatório TAX MASTER</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; color: #333; }
        h1, h2, h3 { color: #0e6ba8; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
        th { background-color: #f2f2f2; text-align: center; }
        .header { background-color: #1a1a1a; color: white; padding: 10px; }
        .summary { margin-bottom: 30px; }
        .footer { margin-top: 30px; font-size: 0.8em; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>TAX MASTER - Relatório de Simulação</h1>
    </div>
    
    <div class="summary">
        <h2>Resumo da Simulação</h2>
        <p>Data: {{timestamp}}</p>
        <p>Módulo: {{moduleId}}</p>
        <pre>{{JSON.stringify data}}</pre>
    </div>
    
    <div class="footer">
        <p>Este relatório foi gerado automaticamente pelo TAX MASTER.</p>
        <p>Data e hora: {{timestamp}}</p>
    </div>
</body>
</html>
            `,
            csv: `Data,{{timestamp}}
Módulo,{{moduleId}}
Dados,{{JSON.stringify data}}
            `
        },
        
        // Template para Módulo 1 - Transação Tributária Básica
        module1: {
            html: `
<!DOCTYPE html>
<html>
<head>
    <title>Relatório de Transação Tributária - TAX MASTER</title>
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
        .footer { margin-top: 30px; font-size: 0.8em; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>TAX MASTER - Relatório de Transação Tributária</h1>
    </div>
    
    <div class="section summary">
        <h2>Resumo da Simulação</h2>
        <table>
            <tr>
                <th>Valor da Dívida</th>
                <th>Modalidade</th>
                <th>Valor Após Descontos</th>
                <th>Economia Total</th>
                <th>Percentual de Economia</th>
            </tr>
            <tr>
                <td>{{valorDivida}}</td>
                <td>{{modalidade}}</td>
                <td>{{valorAposDescontos}}</td>
                <td>{{economiaTotal}}</td>
                <td>{{percentualEconomia}}</td>
            </tr>
        </table>
        
        <h2>Detalhes do Parcelamento</h2>
        <table>
            <tr>
                <th>Número de Parcelas</th>
                <th>Valor da Parcela</th>
                <th>Taxa de Juros</th>
                <th>Entrada</th>
                <th>Valor Parcelado</th>
            </tr>
            <tr>
                <td>{{numeroParcelas}}</td>
                <td>{{valorParcela}}</td>
                <td>{{taxaJuros}}</td>
                <td>{{valorEntrada}}</td>
                <td>{{valorParcelado}}</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Composição da Dívida</h2>
        <table>
            <tr>
                <th>Componente</th>
                <th>Valor Original</th>
                <th>Desconto</th>
                <th>Valor Final</th>
                <th>Percentual de Desconto</th>
            </tr>
            <tr>
                <td>Principal</td>
                <td>{{composicaoDivida.principal}}</td>
                <td>{{descontos.principal}}</td>
                <td>{{valorAposDescontos - descontos.principal}}</td>
                <td>{{percentualDescontoPrincipal}}</td>
            </tr>
            <tr>
                <td>Multas</td>
                <td>{{composicaoDivida.multas}}</td>
                <td>{{descontos.multas}}</td>
                <td>{{composicaoDivida.multas - descontos.multas}}</td>
                <td>{{percentualDescontoMultas}}</td>
            </tr>
            <tr>
                <td>Juros</td>
                <td>{{composicaoDivida.juros}}</td>
                <td>{{descontos.juros}}</td>
                <td>{{composicaoDivida.juros - descontos.juros}}</td>
                <td>{{percentualDescontoJuros}}</td>
            </tr>
            <tr>
                <td>Encargos</td>
                <td>{{composicaoDivida.encargos}}</td>
                <td>{{descontos.encargos}}</td>
                <td>{{composicaoDivida.encargos - descontos.encargos}}</td>
                <td>{{percentualDescontoEncargos}}</td>
            </tr>
            <tr class="highlight">
                <td>Total</td>
                <td>{{valorDivida}}</td>
                <td>{{economiaTotal}}</td>
                <td>{{valorAposDescontos}}</td>
                <td>{{percentualEconomia}}</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Tabela de Amortização</h2>
        <table>
            <tr>
                <th>Parcela</th>
                <th>Valor da Parcela</th>
                <th>Juros</th>
                <th>Amortização</th>
                <th>Saldo Devedor</th>
            </tr>
            {{#each tabelaAmortizacao}}
            <tr>
                <td>{{numeroParcela}}</td>
                <td>{{valorParcela}}</td>
                <td>{{juros}}</td>
                <td>{{amortizacao}}</td>
                <td>{{saldoDevedor}}</td>
            </tr>
            {{/each}}
        </table>
    </div>
    
    <div class="footer">
        <p>Este relatório foi gerado automaticamente pelo TAX MASTER.</p>
        <p>Data e hora: {{timestamp}}</p>
        <p><small>Este relatório é meramente informativo e não constitui compromisso legal.</small></p>
    </div>
</body>
</html>
            `,
            csv: `Relatório de Transação Tributária - TAX MASTER
Data,{{timestamp}}

Resumo da Simulação
Valor da Dívida,{{valorDivida}}
Modalidade,{{modalidade}}
Valor Após Descontos,{{valorAposDescontos}}
Economia Total,{{economiaTotal}}
Percentual de Economia,{{percentualEconomia}}

Detalhes do Parcelamento
Número de Parcelas,{{numeroParcelas}}
Valor da Parcela,{{valorParcela}}
Taxa de Juros,{{taxaJuros}}
Entrada,{{valorEntrada}}
Valor Parcelado,{{valorParcelado}}

Composição da Dívida
Componente,Valor Original,Desconto,Valor Final,Percentual de Desconto
Principal,{{composicaoDivida.principal}},{{descontos.principal}},{{valorAposDescontos - descontos.principal}},{{percentualDescontoPrincipal}}
Multas,{{composicaoDivida.multas}},{{descontos.multas}},{{composicaoDivida.multas - descontos.multas}},{{percentualDescontoMultas}}
Juros,{{composicaoDivida.juros}},{{descontos.juros}},{{composicaoDivida.juros - descontos.juros}},{{percentualDescontoJuros}}
Encargos,{{composicaoDivida.encargos}},{{descontos.encargos}},{{composicaoDivida.encargos - descontos.encargos}},{{percentualDescontoEncargos}}
Total,{{valorDivida}},{{economiaTotal}},{{valorAposDescontos}},{{percentualEconomia}}

Tabela de Amortização
Parcela,Valor da Parcela,Juros,Amortização,Saldo Devedor
{{#each tabelaAmortizacao}}
{{numeroParcela}},{{valorParcela}},{{juros}},{{amortizacao}},{{saldoDevedor}}
{{/each}}
            `
        },
        
        // Template para Módulo 2 - Transação Tributária Avançada
        module2: {
            html: `
<!DOCTYPE html>
<html>
<head>
    <title>Relatório de Transação Tributária Avançada - TAX MASTER</title>
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
        .footer { margin-top: 30px; font-size: 0.8em; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>TAX MASTER - Relatório de Transação Tributária Avançada</h1>
    </div>
    
    <div class="section summary">
        <h2>Resumo da Simulação</h2>
        <table>
            <tr>
                <th>Valor da Dívida</th>
                <th>Modalidade</th>
                <th>Valor Após Descontos</th>
                <th>Economia Total</th>
                <th>Percentual de Economia</th>
            </tr>
            <tr>
                <td>{{valorDivida}}</td>
                <td>{{modalidade}}</td>
                <td>{{valorAposDescontos}}</td>
                <td>{{economiaTotal}}</td>
                <td>{{percentualEconomia}}</td>
            </tr>
        </table>
        
        <h2>Detalhes do Parcelamento</h2>
        <table>
            <tr>
                <th>Número de Parcelas</th>
                <th>Valor da Parcela</th>
                <th>Taxa de Juros</th>
                <th>Entrada</th>
                <th>Valor Parcelado</th>
            </tr>
            <tr>
                <td>{{numeroParcelas}}</td>
                <td>{{valorParcela}}</td>
                <td>{{taxaJuros}}</td>
                <td>{{valorEntrada}}</td>
                <td>{{valorParcelado}}</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Análise de Capacidade de Pagamento</h2>
        <div class="alert {{alertClass}}">
            <strong>Classificação de Risco:</strong> {{analiseCapacidade.classificacaoRisco}}<br>
            <strong>Recomendação:</strong> {{analiseCapacidade.recomendacao}}
        </div>
        <table>
            <tr>
                <th>Receita Mensal</th>
                <th>Despesas Mensais</th>
                <th>Fluxo de Caixa Líquido</th>
                <th>Valor da Parcela</th>
                <th>Impacto da Parcela</th>
            </tr>
            <tr>
                <td>{{analiseCapacidade.receitaMensal}}</td>
                <td>{{analiseCapacidade.despesasMensais}}</td>
                <td>{{analiseCapacidade.fluxoCaixaLiquido}}</td>
                <td>{{valorParcela}}</td>
                <td>{{analiseCapacidade.impactoParcela}}</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Composição da Dívida</h2>
        <table>
            <tr>
                <th>Componente</th>
                <th>Valor Original</th>
                <th>Desconto</th>
                <th>Valor Final</th>
                <th>Percentual de Desconto</th>
            </tr>
            <tr>
                <td>Principal</td>
                <td>{{composicaoDivida.principal}}</td>
                <td>{{descontos.principal}}</td>
                <td>{{valorAposDescontos - descontos.principal}}</td>
                <td>{{percentualDescontoPrincipal}}</td>
            </tr>
            <tr>
                <td>Multas</td>
                <td>{{composicaoDivida.multas}}</td>
                <td>{{descontos.multas}}</td>
                <td>{{composicaoDivida.multas - descontos.multas}}</td>
                <td>{{percentualDescontoMultas}}</td>
            </tr>
            <tr>
                <td>Juros</td>
                <td>{{composicaoDivida.juros}}</td>
                <td>{{descontos.juros}}</td>
                <td>{{composicaoDivida.juros - descontos.juros}}</td>
                <td>{{percentualDescontoJuros}}</td>
            </tr>
            <tr>
                <td>Encargos</td>
                <td>{{composicaoDivida.encargos}}</td>
                <td>{{descontos.encargos}}</td>
                <td>{{composicaoDivida.encargos - descontos.encargos}}</td>
                <td>{{percentualDescontoEncargos}}</td>
            </tr>
            <tr class="highlight">
                <td>Total</td>
                <td>{{valorDivida}}</td>
                <td>{{economiaTotal}}</td>
                <td>{{valorAposDescontos}}</td>
                <td>{{percentualEconomia}}</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Comparativo entre Modalidades</h2>
        <table>
            <tr>
                <th>Modalidade</th>
                <th>Valor Final</th>
                <th>Economia</th>
                <th>Percentual de Economia</th>
                <th>Elegível</th>
            </tr>
            {{#each comparativoModalidades}}
            <tr {{#if modalidade === ../modalidade}}class="highlight"{{/if}}>
                <td>{{modalidade}}</td>
                <td>{{valorFinal}}</td>
                <td>{{economia}}</td>
                <td>{{percentualEconomia}}</td>
                <td>{{elegivel}}</td>
            </tr>
            {{/each}}
        </table>
    </div>
    
    <div class="section">
        <h2>Tabela de Amortização</h2>
        <table>
            <tr>
                <th>Parcela</th>
                <th>Valor da Parcela</th>
                <th>Juros</th>
                <th>Amortização</th>
                <th>Saldo Devedor</th>
            </tr>
            {{#each tabelaAmortizacao}}
            <tr>
                <td>{{numeroParcela}}</td>
                <td>{{valorParcela}}</td>
                <td>{{juros}}</td>
                <td>{{amortizacao}}</td>
                <td>{{saldoDevedor}}</td>
            </tr>
            {{/each}}
        </table>
    </div>
    
    <div class="footer">
        <p>Este relatório foi gerado automaticamente pelo TAX MASTER.</p>
        <p>Data e hora: {{timestamp}}</p>
        <p><small>Este relatório é meramente informativo e não constitui compromisso legal.</small></p>
    </div>
</body>
</html>
            `,
            csv: `Relatório de Transação Tributária Avançada - TAX MASTER
Data,{{timestamp}}

Resumo da Simulação
Valor da Dívida,{{valorDivida}}
Modalidade,{{modalidade}}
Valor Após Descontos,{{valorAposDescontos}}
Economia Total,{{economiaTotal}}
Percentual de Economia,{{percentualEconomia}}

Detalhes do Parcelamento
Número de Parcelas,{{numeroParcelas}}
Valor da Parcela,{{valorParcela}}
Taxa de Juros,{{taxaJuros}}
Entrada,{{valorEntrada}}
Valor Parcelado,{{valorParcelado}}

Análise de Capacidade de Pagamento
Receita Mensal,{{analiseCapacidade.receitaMensal}}
Despesas Mensais,{{analiseCapacidade.despesasMensais}}
Fluxo de Caixa Líquido,{{analiseCapacidade.fluxoCaixaLiquido}}
Valor da Parcela,{{valorParcela}}
Impacto da Parcela,{{analiseCapacidade.impactoParcela}}
Classificação de Risco,{{analiseCapacidade.classificacaoRisco}}
Recomendação,{{analiseCapacidade.recomendacao}}

Composição da Dívida
Componente,Valor Original,Desconto,Valor Final,Percentual de Desconto
Principal,{{composicaoDivida.principal}},{{descontos.principal}},{{valorAposDescontos - descontos.principal}},{{percentualDescontoPrincipal}}
Multas,{{composicaoDivida.multas}},{{descontos.multas}},{{composicaoDivida.multas - descontos.multas}},{{percentualDescontoMultas}}
Juros,{{composicaoDivida.juros}},{{descontos.juros}},{{composicaoDivida.juros - descontos.juros}},{{percentualDescontoJuros}}
Encargos,{{composicaoDivida.encargos}},{{descontos.encargos}},{{composicaoDivida.encargos - descontos.encargos}},{{percentualDescontoEncargos}}
Total,{{valorDivida}},{{economiaTotal}},{{valorAposDescontos}},{{percentualEconomia}}

Comparativo entre Modalidades
Modalidade,Valor Final,Economia,Percentual de Economia,Elegível
{{#each comparativoModalidades}}
{{modalidade}},{{valorFinal}},{{economia}},{{percentualEconomia}},{{elegivel}}
{{/each}}

Tabela de Amortização
Parcela,Valor da Parcela,Juros,Amortização,Saldo Devedor
{{#each tabelaAmortizacao}}
{{numeroParcela}},{{valorParcela}},{{juros}},{{amortizacao}},{{saldoDevedor}}
{{/each}}
            `
        },
        
        // Template para Módulo 3 - Parcelamento e Redução de Débitos
        module3: {
            html: `
<!DOCTYPE html>
<html>
<head>
    <title>Relatório de Parcelamento e Redução de Débitos - TAX MASTER</title>
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
        .footer { margin-top: 30px; font-size: 0.8em; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>TAX MASTER - Relatório de Parcelamento e Redução de Débitos</h1>
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
                <td>{{modalidade}}</td>
                <td>{{valorOriginal}}</td>
                <td>{{valorAposDescontos}}</td>
                <td>{{economiaTotal}}</td>
                <td>{{percentualEconomia}}</td>
            </tr>
        </table>
        
        <h2>Detalhes do Parcelamento</h2>
        <table>
            <tr>
                <th>Valor Entrada</th>
                <th>Valor Parcelado</th>
                <th>Número Parcelas</th>
                <th>Valor Parcela</th>
                <th>Taxa Juros Mensal</th>
                <th>Custo Efetivo Total</th>
            </tr>
            <tr>
                <td>{{valorEntrada}}</td>
                <td>{{valorParcelado}}</td>
                <td>{{numeroParcelas}}</td>
                <td>{{valorParcela}}</td>
                <td>{{taxaJurosMensal}}</td>
                <td>{{custoEfetivoTotal}}</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Análise de Fluxo de Caixa</h2>
        <div class="alert {{alertClass}}">
            <strong>Classificação de Risco:</strong> {{analiseFluxoCaixa.classificacaoRisco}}<br>
            <strong>Recomendação:</strong> {{analiseFluxoCaixa.recomendacao}}
        </div>
        <table>
            <tr>
                <th>Receita Mensal</th>
                <th>Despesas Mensais</th>
                <th>Fluxo de Caixa Líquido</th>
                <th>Valor da Parcela</th>
                <th>Impacto da Parcela</th>
            </tr>
            <tr>
                <td>{{analiseFluxoCaixa.receitaMensal}}</td>
                <td>{{analiseFluxoCaixa.despesasMensais}}</td>
                <td>{{analiseFluxoCaixa.fluxoCaixaLiquido}}</td>
                <td>{{valorParcela}}</td>
                <td>{{analiseFluxoCaixa.impactoParcela}}</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Comparativo entre Modalidades</h2>
        <table>
            <tr>
                <th>Modalidade</th>
                <th>Valor Final</th>
                <th>Economia</th>
                <th>Prazo</th>
                <th>Parcela</th>
                <th>CET</th>
                <th>Elegível</th>
            </tr>
            {{#each comparativoModalidades}}
            <tr {{#if modalidade === ../modalidade}}class="highlight"{{/if}}>
                <td>{{modalidade}}</td>
                <td>{{valorFinal}}</td>
                <td>{{economia}}</td>
                <td>{{prazo}}</td>
                <td>{{valorParcela}}</td>
                <td>{{custoEfetivoTotal}}</td>
                <td>{{elegivel}}</td>
            </tr>
            {{/each}}
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
            </tr>
            {{#each tabelaAmortizacao}}
            <tr>
                <td>{{numeroParcela}}</td>
                <td>{{valorParcela}}</td>
                <td>{{juros}}</td>
                <td>{{amortizacao}}</td>
                <td>{{saldoDevedor}}</td>
            </tr>
            {{/each}}
        </table>
    </div>
    
    <div class="footer">
        <p>Este relatório foi gerado automaticamente pelo TAX MASTER.</p>
        <p>Data e hora: {{timestamp}}</p>
        <p><small>Esta simulação é meramente informativa e não constitui compromisso legal.</small></p>
    </div>
</body>
</html>
            `,
            csv: `Relatório de Parcelamento e Redução de Débitos - TAX MASTER
Data,{{timestamp}}

Resumo da Simulação
Modalidade,{{modalidade}}
Valor Original,{{valorOriginal}}
Valor Após Descontos,{{valorAposDescontos}}
Economia Total,{{economiaTotal}}
Percentual Economia,{{percentualEconomia}}

Detalhes do Parcelamento
Valor Entrada,{{valorEntrada}}
Valor Parcelado,{{valorParcelado}}
Número Parcelas,{{numeroParcelas}}
Valor Parcela,{{valorParcela}}
Taxa Juros Mensal,{{taxaJurosMensal}}
Custo Efetivo Total,{{custoEfetivoTotal}}

Análise de Fluxo de Caixa
Receita Mensal,{{analiseFluxoCaixa.receitaMensal}}
Despesas Mensais,{{analiseFluxoCaixa.despesasMensais}}
Fluxo de Caixa Líquido,{{analiseFluxoCaixa.fluxoCaixaLiquido}}
Impacto da Parcela,{{analiseFluxoCaixa.impactoParcela}}
Classificação de Risco,{{analiseFluxoCaixa.classificacaoRisco}}
Recomendação,{{analiseFluxoCaixa.recomendacao}}

Comparativo entre Modalidades
Modalidade,Valor Final,Economia,Prazo,Parcela,CET,Elegível
{{#each comparativoModalidades}}
{{modalidade}},{{valorFinal}},{{economia}},{{prazo}},{{valorParcela}},{{custoEfetivoTotal}},{{elegivel}}
{{/each}}

Tabela de Amortização
Parcela,Valor Parcela,Juros,Amortização,Saldo Devedor
{{#each tabelaAmortizacao}}
{{numeroParcela}},{{valorParcela}},{{juros}},{{amortizacao}},{{saldoDevedor}}
{{/each}}
            `
        },
        
        // Template para Módulo 4 - Planejamento Tributário Estratégico
        module4: {
            html: `
<!DOCTYPE html>
<html>
<head>
    <title>Relatório de Planejamento Tributário Estratégico - TAX MASTER</title>
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
        .footer { margin-top: 30px; font-size: 0.8em; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>TAX MASTER - Relatório de Planejamento Tributário Estratégico</h1>
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
                <td>{{cenarioEconomico}}</td>
                <td>{{horizontePlanejamento}} anos</td>
                <td>{{faturamentoAnual}}</td>
                <td>{{regimeTributarioAtual}}</td>
                <td>{{regimeTributarioRecomendado}}</td>
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
                <td>{{economiaTributariaTotal}}</td>
                <td>{{percentualEconomia}}</td>
                <td>{{valorPresenteEconomia}}</td>
                <td>{{roiPlanejamentoTributario}}</td>
                <td>{{custoImplementacao}}</td>
            </tr>
        </table>
    </div>
    
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
            </tr>
            {{#each projecoesAnuais}}
            <tr>
                <td>{{ano}}</td>
                <td>{{faturamentoProjetado}}</td>
                <td>{{tributosRegimeAtual}}</td>
                <td>{{tributosRegimeRecomendado}}</td>
                <td>{{economiaTributaria}}</td>
                <td>{{economiaAcumulada}}</td>
            </tr>
            {{/each}}
        </table>
    </div>
    
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
            </tr>
            {{#each analiseSensibilidade}}
            <tr>
                <td>{{parametro}}</td>
                <td>{{variacao}}</td>
                <td>{{economiaTributaria}}</td>
                <td class="{{impactoClass}}">{{diferenca}}</td>
                <td class="{{impactoClass}}">{{impactoPercentual}}</td>
            </tr>
            {{/each}}
        </table>
    </div>
    
    <div class="section">
        <h2>Recomendações Estratégicas</h2>
        {{#each recomendacoesEstrategicas}}
        <div class="recommendation-item">
            <h3>{{titulo}}</h3>
            <p>{{descricao}}</p>
            <div class="recommendation-details">
                <span>Prioridade: {{prioridade}}</span>
                <span>Impacto: {{impacto}}</span>
                <span>Complexidade: {{complexidade}}</span>
            </div>
        </div>
        {{/each}}
    </div>
    
    <div class="footer">
        <p>Este relatório foi gerado automaticamente pelo TAX MASTER.</p>
        <p>Data e hora: {{timestamp}}</p>
        <p><small>Este relatório é meramente informativo e não constitui aconselhamento tributário formal. Consulte um especialista antes de implementar qualquer estratégia.</small></p>
    </div>
</body>
</html>
            `,
            csv: `Relatório de Planejamento Tributário Estratégico - TAX MASTER
Data,{{timestamp}}

Resumo do Planejamento
Cenário Econômico,{{cenarioEconomico}}
Horizonte,{{horizontePlanejamento}} anos
Faturamento Anual,{{faturamentoAnual}}
Regime Atual,{{regimeTributarioAtual}}
Regime Recomendado,{{regimeTributarioRecomendado}}

Resultados Financeiros
Economia Total,{{economiaTributariaTotal}}
Percentual Economia,{{percentualEconomia}}
Valor Presente Economia,{{valorPresenteEconomia}}
ROI do Planejamento,{{roiPlanejamentoTributario}}
Custo Implementação,{{custoImplementacao}}

Projeções Anuais
Ano,Faturamento Projetado,Tributos (Regime Atual),Tributos (Regime Recomendado),Economia Anual,Economia Acumulada
{{#each projecoesAnuais}}
{{ano}},{{faturamentoProjetado}},{{tributosRegimeAtual}},{{tributosRegimeRecomendado}},{{economiaTributaria}},{{economiaAcumulada}}
{{/each}}

Análise de Sensibilidade
Parâmetro,Variação,Economia Tributária,Diferença,Impacto
{{#each analiseSensibilidade}}
{{parametro}},{{variacao}},{{economiaTributaria}},{{diferenca}},{{impactoPercentual}}
{{/each}}

Recomendações Estratégicas
Título,Descrição,Prioridade,Impacto,Complexidade
{{#each recomendacoesEstrategicas}}
"{{titulo}}","{{descricao}}",{{prioridade}},{{impacto}},{{complexidade}}
{{/each}}
            `
        }
    }
};

// Inicializar módulo de exportação de relatórios
(function() {
    // Inicializar módulo
    TAXMASTER.reports.init();
    
    console.log('Módulo de exportação de relatórios inicializado com sucesso.');
})();
