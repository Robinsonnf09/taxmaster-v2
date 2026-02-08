# Script PowerShell - Criar Planilha Financeira Automatizada
# Versao: 2.0 - Compatibilidade Total

# Configuracoes
$caminhoArquivo = "$PSScriptRoot\FinancasRobinson_2026_Automatizada.xlsm"

Write-Host "[INICIO] Criando planilha financeira automatizada..." -ForegroundColor Cyan

try {
    # Criar objeto Excel
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    
    Write-Host "[OK] Excel iniciado com sucesso." -ForegroundColor Green
    
    # Criar nova pasta de trabalho
    $workbook = $excel.Workbooks.Add()
    
    Write-Host "[OK] Arquivo Excel criado." -ForegroundColor Green
    
    # Remover planilhas padrao extras
    while ($workbook.Worksheets.Count -gt 1) {
        $workbook.Worksheets.Item($workbook.Worksheets.Count).Delete()
    }
    
    # Renomear primeira planilha
    $workbook.Worksheets.Item(1).Name = "DASHBOARD"
    
    # Criar as outras 9 abas
    $abas = @("DESPESAS", "RECEITAS", "ORCAMENTO", "ANALISE_MENSAL", "MEMBROS", "PARCELAMENTOS", "METAS", "INVESTIMENTOS", "LOG")
    
    foreach ($nomeAba in $abas) {
        $workbook.Worksheets.Add([System.Reflection.Missing]::Value, $workbook.Worksheets.Item($workbook.Worksheets.Count)) | Out-Null
        $workbook.Worksheets.Item($workbook.Worksheets.Count).Name = $nomeAba
        Write-Host "[OK] Aba '$nomeAba' criada." -ForegroundColor Green
    }
    
    # === ABA DASHBOARD ===
    $wsDashboard = $workbook.Worksheets.Item("DASHBOARD")
    $wsDashboard.Range("A1").Value = "DASHBOARD FINANCEIRO FAMILIAR"
    $wsDashboard.Range("A1:C1").Merge()
    $wsDashboard.Range("A1").Font.Size = 16
    $wsDashboard.Range("A1").Font.Bold = $true
    $wsDashboard.Range("A1").Interior.Color = 15773696
    $wsDashboard.Range("A1").Font.Color = 16777215
    $wsDashboard.Range("A1").HorizontalAlignment = -4108
    
    $wsDashboard.Range("A3").Value = "Periodo:"
    $wsDashboard.Range("B3").Value = "Janeiro/2026"
    $wsDashboard.Range("A5").Value = "RECEITAS TOTAIS:"
    $wsDashboard.Range("B5").Value = 0
    $wsDashboard.Range("B5").NumberFormat = "R$ #,##0.00"
    $wsDashboard.Range("A6").Value = "DESPESAS TOTAIS:"
    $wsDashboard.Range("B6").Value = 0
    $wsDashboard.Range("B6").NumberFormat = "R$ #,##0.00"
    $wsDashboard.Range("A7").Value = "SALDO MENSAL:"
    $wsDashboard.Range("B7").Value = 0
    $wsDashboard.Range("B7").NumberFormat = "R$ #,##0.00"
    $wsDashboard.Range("A8").Value = "TAXA DE POUPANCA:"
    $wsDashboard.Range("B8").Value = "0%"
    
    $wsDashboard.Range("A5:A8").Font.Bold = $true
    $wsDashboard.Columns.Item("A:A").ColumnWidth = 25
    $wsDashboard.Columns.Item("B:B").ColumnWidth = 20
    
    Write-Host "[OK] Aba DASHBOARD estruturada." -ForegroundColor Green
    
    # === ABA DESPESAS ===
    $wsDespesas = $workbook.Worksheets.Item("DESPESAS")
    $cabecalhos = @("Data", "Mes", "Ano", "Descricao", "Valor", "Categoria", "Subcategoria", "Metodo_Pagamento", "Responsavel")
    
    for ($i = 0; $i -lt $cabecalhos.Length; $i++) {
        $wsDespesas.Cells.Item(1, $i + 1).Value = $cabecalhos[$i]
    }
    
    $wsDespesas.Range("A1:I1").Font.Bold = $true
    $wsDespesas.Range("A1:I1").Interior.Color = 15773696
    $wsDespesas.Range("A1:I1").Font.Color = 16777215
    $wsDespesas.Range("A1:I1").HorizontalAlignment = -4108
    
    # Dados de exemplo
    $despesas = @(
        @("15/01/2026", "Janeiro", 2026, "Supermercado Dia", 450.00, "Alimentacao", "Supermercado", "Cartao de Credito", "Robinson"),
        @("16/01/2026", "Janeiro", 2026, "Gasolina", 250.00, "Transporte", "Combustivel", "Debito", "Robinson"),
        @("17/01/2026", "Janeiro", 2026, "Conta de Luz", 180.00, "Moradia", "Energia", "Boleto", "Robinson"),
        @("18/01/2026", "Janeiro", 2026, "Farmacia", 85.50, "Saude", "Medicamentos", "Dinheiro", "Robinson"),
        @("19/01/2026", "Janeiro", 2026, "Internet", 120.00, "Moradia", "Telecomunicacoes", "Debito", "Robinson"),
        @("20/01/2026", "Janeiro", 2026, "Restaurante", 95.00, "Alimentacao", "Restaurante", "Cartao de Credito", "Robinson"),
        @("21/01/2026", "Janeiro", 2026, "Academia", 150.00, "Saude", "Atividade Fisica", "Boleto", "Robinson"),
        @("22/01/2026", "Janeiro", 2026, "Uber", 45.00, "Transporte", "App de Transporte", "Cartao de Credito", "Robinson"),
        @("23/01/2026", "Janeiro", 2026, "Cinema", 60.00, "Lazer", "Entretenimento", "Cartao de Credito", "Robinson"),
        @("24/01/2026", "Janeiro", 2026, "Padaria", 35.00, "Alimentacao", "Padaria", "Dinheiro", "Robinson")
    )
    
    for ($i = 0; $i -lt $despesas.Length; $i++) {
        for ($j = 0; $j -lt $despesas[$i].Length; $j++) {
            $wsDespesas.Cells.Item($i + 2, $j + 1).Value = $despesas[$i][$j]
        }
    }
    
    $wsDespesas.Columns.Item("A:A").NumberFormat = "dd/mm/yyyy"
    $wsDespesas.Columns.Item("E:E").NumberFormat = "R$ #,##0.00"
    $wsDespesas.Columns.Item("A:I").AutoFit()
    
    Write-Host "[OK] Aba DESPESAS estruturada com dados de exemplo." -ForegroundColor Green
    
    # === ABA RECEITAS ===
    $wsReceitas = $workbook.Worksheets.Item("RECEITAS")
    $cabecalhosRec = @("Data", "Mes", "Ano", "Descricao", "Valor", "Fonte")
    
    for ($i = 0; $i -lt $cabecalhosRec.Length; $i++) {
        $wsReceitas.Cells.Item(1, $i + 1).Value = $cabecalhosRec[$i]
    }
    
    $wsReceitas.Range("A1:F1").Font.Bold = $true
    $wsReceitas.Range("A1:F1").Interior.Color = 5287936
    $wsReceitas.Range("A1:F1").Font.Color = 16777215
    
    $receitas = @(
        @("05/01/2026", "Janeiro", 2026, "Salario", 8500.00, "Emprego Principal"),
        @("05/01/2026", "Janeiro", 2026, "Bonus", 1500.00, "Emprego Principal"),
        @("10/01/2026", "Janeiro", 2026, "Consultoria", 2000.00, "Freelancer"),
        @("15/01/2026", "Janeiro", 2026, "Aluguel Imovel", 1200.00, "Investimentos"),
        @("20/01/2026", "Janeiro", 2026, "Dividendos", 350.00, "Investimentos"),
        @("25/01/2026", "Janeiro", 2026, "Vendas Online", 450.00, "Renda Extra")
    )
    
    for ($i = 0; $i -lt $receitas.Length; $i++) {
        for ($j = 0; $j -lt $receitas[$i].Length; $j++) {
            $wsReceitas.Cells.Item($i + 2, $j + 1).Value = $receitas[$i][$j]
        }
    }
    
    $wsReceitas.Columns.Item("A:A").NumberFormat = "dd/mm/yyyy"
    $wsReceitas.Columns.Item("E:E").NumberFormat = "R$ #,##0.00"
    $wsReceitas.Columns.Item("A:F").AutoFit()
    
    Write-Host "[OK] Aba RECEITAS estruturada com dados de exemplo." -ForegroundColor Green
    
    # === ABA ORCAMENTO ===
    $wsOrcamento = $workbook.Worksheets.Item("ORCAMENTO")
    $cabecalhosOrc = @("Categoria", "Orcamento Mensal", "Gasto Real", "% Usado")
    
    for ($i = 0; $i -lt $cabecalhosOrc.Length; $i++) {
        $wsOrcamento.Cells.Item(1, $i + 1).Value = $cabecalhosOrc[$i]
    }
    
    $wsOrcamento.Range("A1:D1").Font.Bold = $true
    $wsOrcamento.Range("A1:D1").Interior.Color = 49407
    $wsOrcamento.Range("A1:D1").Font.Color = 16777215
    
    $categorias = @(
        @("Alimentacao", 1500.00, 580.00, "38.7%"),
        @("Transporte", 800.00, 295.00, "36.9%"),
        @("Moradia", 2000.00, 300.00, "15.0%"),
        @("Saude", 500.00, 235.50, "47.1%"),
        @("Educacao", 600.00, 0.00, "0.0%"),
        @("Lazer", 400.00, 60.00, "15.0%"),
        @("Vestuario", 300.00, 0.00, "0.0%"),
        @("Comunicacao", 200.00, 0.00, "0.0%"),
        @("Impostos", 1000.00, 0.00, "0.0%"),
        @("Outros", 300.00, 0.00, "0.0%")
    )
    
    for ($i = 0; $i -lt $categorias.Length; $i++) {
        for ($j = 0; $j -lt $categorias[$i].Length; $j++) {
            $wsOrcamento.Cells.Item($i + 2, $j + 1).Value = $categorias[$i][$j]
        }
    }
    
    $wsOrcamento.Columns.Item("B:C").NumberFormat = "R$ #,##0.00"
    $wsOrcamento.Columns.Item("A:D").AutoFit()
    
    Write-Host "[OK] Aba ORCAMENTO estruturada com dados de exemplo." -ForegroundColor Green
    
    # === ABA LOG ===
    $wsLog = $workbook.Worksheets.Item("LOG")
    $cabecalhosLog = @("Data/Hora", "Modulo", "Evento", "Detalhes")
    
    for ($i = 0; $i -lt $cabecalhosLog.Length; $i++) {
        $wsLog.Cells.Item(1, $i + 1).Value = $cabecalhosLog[$i]
    }
    
    $wsLog.Range("A1:D1").Font.Bold = $true
    $wsLog.Range("A1:D1").Interior.Color = 8421504
    $wsLog.Range("A1:D1").Font.Color = 16777215
    $wsLog.Columns.Item("A:D").AutoFit()
    
    Write-Host "[OK] Aba LOG estruturada." -ForegroundColor Green
    
    # === INJETAR CODIGO VBA ===
    Write-Host "[PROCESSO] Injetando codigo VBA na planilha..." -ForegroundColor Yellow
    
    $vbaCode = @"
Sub Auto_Open()
    Application.OnKey "^+D", "RegistrarDespesaRapida"
    Application.OnKey "^+R", "RegistrarReceitaRapida"
    Application.OnKey "^+A", "AtualizarDashboard"
    MsgBox "Sistema Financeiro Ativado!" & vbCrLf & vbCrLf & _
           "Atalhos disponiveis:" & vbCrLf & _
           "Ctrl+Shift+D = Nova Despesa" & vbCrLf & _
           "Ctrl+Shift+R = Nova Receita" & vbCrLf & _
           "Ctrl+Shift+A = Atualizar Dashboard", vbInformation, "Sistema Pronto"
End Sub

Sub RegistrarDespesaRapida()
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Worksheets("DESPESAS")
    
    Dim ultimaLinha As Long
    ultimaLinha = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row + 1
    
    Dim descricao As String, valor As Double, categoria As String
    descricao = InputBox("Descricao da despesa:", "Nova Despesa")
    If descricao = "" Then Exit Sub
    
    valor = InputBox("Valor (R$):", "Nova Despesa")
    If valor = 0 Then Exit Sub
    
    categoria = InputBox("Categoria:", "Nova Despesa", "Alimentacao")
    
    ws.Cells(ultimaLinha, 1).Value = Date
    ws.Cells(ultimaLinha, 2).Value = Format(Date, "mmmm")
    ws.Cells(ultimaLinha, 3).Value = Year(Date)
    ws.Cells(ultimaLinha, 4).Value = descricao
    ws.Cells(ultimaLinha, 5).Value = valor
    ws.Cells(ultimaLinha, 6).Value = categoria
    ws.Cells(ultimaLinha, 9).Value = "Usuario"
    
    MsgBox "Despesa registrada com sucesso!", vbInformation
    Call AtualizarDashboard
End Sub

Sub RegistrarReceitaRapida()
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Worksheets("RECEITAS")
    
    Dim ultimaLinha As Long
    ultimaLinha = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row + 1
    
    Dim descricao As String, valor As Double, fonte As String
    descricao = InputBox("Descricao da receita:", "Nova Receita")
    If descricao = "" Then Exit Sub
    
    valor = InputBox("Valor (R$):", "Nova Receita")
    If valor = 0 Then Exit Sub
    
    fonte = InputBox("Fonte:", "Nova Receita", "Salario")
    
    ws.Cells(ultimaLinha, 1).Value = Date
    ws.Cells(ultimaLinha, 2).Value = Format(Date, "mmmm")
    ws.Cells(ultimaLinha, 3).Value = Year(Date)
    ws.Cells(ultimaLinha, 4).Value = descricao
    ws.Cells(ultimaLinha, 5).Value = valor
    ws.Cells(ultimaLinha, 6).Value = fonte
    
    MsgBox "Receita registrada com sucesso!", vbInformation
    Call AtualizarDashboard
End Sub

Sub AtualizarDashboard()
    Dim wsDash As Worksheet, wsDesp As Worksheet, wsRec As Worksheet
    Set wsDash = ThisWorkbook.Worksheets("DASHBOARD")
    Set wsDesp = ThisWorkbook.Worksheets("DESPESAS")
    Set wsRec = ThisWorkbook.Worksheets("RECEITAS")
    
    Dim totalReceitas As Double, totalDespesas As Double
    totalReceitas = Application.WorksheetFunction.Sum(wsRec.Range("E:E"))
    totalDespesas = Application.WorksheetFunction.Sum(wsDesp.Range("E:E"))
    
    wsDash.Range("B5").Value = totalReceitas
    wsDash.Range("B6").Value = totalDespesas
    wsDash.Range("B7").Value = totalReceitas - totalDespesas
    
    If totalReceitas > 0 Then
        wsDash.Range("B8").Value = Format((totalReceitas - totalDespesas) / totalReceitas, "0.0%")
    End If
    
    MsgBox "Dashboard atualizado com sucesso!", vbInformation
End Sub
"@
    
    $vbaModule = $workbook.VBProject.VBComponents.Add(1)
    $vbaModule.CodeModule.AddFromString($vbaCode)
    $vbaModule.Name = "modFinanceiro"
    
    Write-Host "[OK] Codigo VBA injetado com sucesso!" -ForegroundColor Green
    
    # Salvar como XLSM
    Write-Host "[PROCESSO] Salvando planilha como XLSM..." -ForegroundColor Yellow
    $workbook.SaveAs($caminhoArquivo, 52)
    
    Write-Host "[OK] Planilha salva em: $caminhoArquivo" -ForegroundColor Green
    
    # Fechar
    $workbook.Close($false)
    $excel.Quit()
    
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
    
    Write-Host ""
    Write-Host "[SUCESSO] Processo concluido com sucesso!" -ForegroundColor Green
    Write-Host "[INFO] Arquivo criado: $caminhoArquivo" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Proximos passos:" -ForegroundColor Yellow
    Write-Host "1. Abra o arquivo no Excel" -ForegroundColor White
    Write-Host "2. Clique em 'Habilitar Conteudo' (barra amarela)" -ForegroundColor White
    Write-Host "3. Teste: Ctrl+Shift+D para registrar despesa" -ForegroundColor White
    
} catch {
    Write-Host ""
    Write-Host "[ERRO] Ocorreu um erro: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[DETALHE] $($_.Exception.StackTrace)" -ForegroundColor Red
    
    if ($excel) {
        $excel.Quit()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
    }
}