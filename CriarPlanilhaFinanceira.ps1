# Início do Script PowerShell
# Salve este código como CriarPlanilhaFinanceira.ps1

# --- Variáveis de Configuração ---
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$outputPath = Join-Path $scriptPath "FinancasRobinson_2026_Automatizada.xlsm"

# --- Função para Injetar Código VBA ---
function Inject-VBA($workbook, $moduleName, $vbaCode) {
    $vbaProject = $workbook.VBProject
    $module = $vbaProject.VBComponents.Add(1) # 1 = vbext_ct_StdModule
    $module.Name = $moduleName
    $module.CodeModule.AddFromString($vbaCode)
}

function Inject-ThisWorkbookVBA($workbook, $vbaCode) {
    $vbaProject = $workbook.VBProject
    $thisWorkbookModule = $vbaProject.VBComponents.Item("ThisWorkbook")
    $thisWorkbookModule.CodeModule.AddFromString($vbaCode)
}

# --- Código VBA a ser Injetado ---
$vba_modCore = @"
Option Explicit

' Função para configurar o Ribbon e Atalhos
Sub SetupRibbonAndShortcuts()
    On Error GoTo ErrorHandler
    
    ' Configurar Atalhos de Teclado
    Application.OnKey "^+D", "modDataEntry.RegistrarDespesaRapida" ' Ctrl + Shift + D
    Application.OnKey "^+R", "modDataEntry.RegistrarReceitaRapida" ' Ctrl + Shift + R
    Application.OnKey "^+A", "modDashboard.AtualizarDashboard"     ' Ctrl + Shift + A
    
    Exit Sub

ErrorHandler:
    MsgBox "Erro ao configurar Atalhos: " & Err.Description, vbCritical, "Erro de Configuração"
End Sub

' Função para limpar atalhos ao fechar
Sub CleanUpShortcuts()
    Application.OnKey "^+D"
    Application.OnKey "^+R"
    Application.OnKey "^+A"
End Sub
"@

$vba_modDataEntry = @"
Option Explicit

Sub RegistrarDespesaRapida()
    On Error GoTo ErrorHandler
    
    Dim wsDespesas As Worksheet
    Set wsDespesas = ThisWorkbook.Sheets("DESPESAS")
    
    Dim nextRow As Long
    nextRow = modUtilitarios.GetNextEmptyRow(wsDespesas)
    
    Dim dataDespesa As Date
    Dim descricao As String
    Dim valor As Double
    Dim categoria As String
    Dim responsavel As String
    
    ' Entrada de dados
    dataDespesa = InputBox("Data da Despesa (DD/MM/AAAA):", "Registrar Despesa", Format(Date, "DD/MM/YYYY"))
    If Not IsDate(dataDespesa) Then
        MsgBox "Data inválida. Operação cancelada.", vbCritical
        Exit Sub
    End If
    
    descricao = InputBox("Descrição da Despesa:", "Registrar Despesa")
    If descricao = "" Then
        MsgBox "Descrição não pode ser vazia. Operação cancelada.", vbCritical
        Exit Sub
    End If
    
    valor = InputBox("Valor da Despesa (R$):", "Registrar Despesa")
    If Not IsNumeric(valor) Or valor <= 0 Then
        MsgBox "Valor inválido. Operação cancelada.", vbCritical
        Exit Sub
    End If
    
    categoria = InputBox("Categoria (Ex: Alimentação, Transporte):", "Registrar Despesa")
    If categoria = "" Then
        MsgBox "Categoria não pode ser vazia. Operação cancelada.", vbCritical
        Exit Sub
    End If
    
    responsavel = InputBox("Responsável (Ex: João, Maria):", "Registrar Despesa")
    If responsavel = "" Then
        MsgBox "Responsável não pode ser vazio. Operação cancelada.", vbCritical
        Exit Sub
    End If
    
    ' Preencher a planilha
    wsDespesas.Cells(nextRow, 1).Value = dataDespesa
    wsDespesas.Cells(nextRow, 2).Value = Month(dataDespesa) ' Mês numérico
    wsDespesas.Cells(nextRow, 3).Value = Year(dataDespesa)
    wsDespesas.Cells(nextRow, 4).Value = descricao
    wsDespesas.Cells(nextRow, 5).Value = valor
    wsDespesas.Cells(nextRow, 6).Value = categoria
    wsDespesas.Cells(nextRow, 7).Value = "" ' Subcategoria (pode ser adicionada manualmente ou via lista)
    wsDespesas.Cells(nextRow, 8).Value = "Não Informado" ' Método Pgto
    wsDespesas.Cells(nextRow, 9).Value = responsavel
    
    ' Formatar a linha
    wsDespesas.Range("A" & nextRow & ":I" & nextRow).Interior.Color = RGB(240, 248, 255) ' Azul claro
    wsDespesas.Range("A" & nextRow).NumberFormat = "dd/mm/yyyy"
    wsDespesas.Range("E" & nextRow).NumberFormat = "R$ #,##0.00"
    
    MsgBox "Despesa registrada com sucesso!", vbInformation, "Sucesso"
    Call modDashboard.AtualizarDashboard ' Atualiza o dashboard após o registro
    Exit Sub

ErrorHandler:
    MsgBox "Erro ao registrar despesa: " & Err.Description, vbCritical, "Erro"
End Sub

Sub RegistrarReceitaRapida()
    On Error GoTo ErrorHandler
    
    Dim wsReceitas As Worksheet
    Set wsReceitas = ThisWorkbook.Sheets("RECEITAS")
    
    Dim nextRow As Long
    nextRow = modUtilitarios.GetNextEmptyRow(wsReceitas)
    
    Dim dataReceita As Date
    Dim descricao As String
    Dim valor As Double
    Dim fonte As String
    
    ' Entrada de dados
    dataReceita = InputBox("Data da Receita (DD/MM/AAAA):", "Registrar Receita", Format(Date, "DD/MM/YYYY"))
    If Not IsDate(dataReceita) Then
        MsgBox "Data inválida. Operação cancelada.", vbCritical
        Exit Sub
    End If
    
    descricao = InputBox("Descrição da Receita:", "Registrar Receita")
    If descricao = "" Then
        MsgBox "Descrição não pode ser vazia. Operação cancelada.", vbCritical
        Exit Sub
    End If
    
    valor = InputBox("Valor da Receita (R$):", "Registrar Receita")
    If Not IsNumeric(valor) Or valor <= 0 Then
        MsgBox "Valor inválido. Operação cancelada.", vbCritical
        Exit Sub
    End If
    
    fonte = InputBox("Fonte da Receita (Ex: Salário, Freelance):", "Registrar Receita")
    If fonte = "" Then
        MsgBox "Fonte não pode ser vazia. Operação cancelada.", vbCritical
        Exit Sub
    End If
    
    ' Preencher a planilha
    wsReceitas.Cells(nextRow, 1).Value = dataReceita
    wsReceitas.Cells(nextRow, 2).Value = Month(dataReceita)
    wsReceitas.Cells(nextRow, 3).Value = Year(dataReceita)
    wsReceitas.Cells(nextRow, 4).Value = descricao
    wsReceitas.Cells(nextRow, 5).Value = valor
    wsReceitas.Cells(nextRow, 6).Value = fonte
    
    ' Formatar a linha
    wsReceitas.Range("A" & nextRow & ":F" & nextRow).Interior.Color = RGB(240, 255, 240) ' Verde claro
    wsReceitas.Range("A" & nextRow).NumberFormat = "dd/mm/yyyy"
    wsReceitas.Range("E" & nextRow).NumberFormat = "R$ #,##0.00"
    
    MsgBox "Receita registrada com sucesso!", vbInformation, "Sucesso"
    Call modDashboard.AtualizarDashboard ' Atualiza o dashboard após o registro
    Exit Sub

ErrorHandler:
    MsgBox "Erro ao registrar receita: " & Err.Description, vbCritical, "Erro"
End Sub
"@

$vba_modDashboard = @"
Option Explicit

Sub AtualizarDashboard()
    On Error GoTo ErrorHandler
    
    Dim wsDashboard As Worksheet
    Dim wsDespesas As Worksheet
    Dim wsReceitas As Worksheet
    Dim wsOrcamento As Worksheet
    
    Set wsDashboard = ThisWorkbook.Sheets("DASHBOARD")
    Set wsDespesas = ThisWorkbook.Sheets("DESPESAS")
    Set wsReceitas = ThisWorkbook.Sheets("RECEITAS")
    Set wsOrcamento = ThisWorkbook.Sheets("ORÇAMENTO")
    
    ' Desabilitar atualização de tela para performance
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual
    
    ' --- Obter Mês/Ano Atual do Dashboard (Célula B3) ---
    Dim mesAtual As Long
    Dim anoAtual As Long
    
    ' Assumindo que B3 no Dashboard tem o formato "Mês/Ano" ou "Mês Ano"
    ' Ex: "Janeiro/2026"
    Dim periodoStr As String
    periodoStr = wsDashboard.Range("B3").Value
    
    If InStr(periodoStr, "/") > 0 Then
        mesAtual = Month(DateValue("01/" & periodoStr))
        anoAtual = Year(DateValue("01/" & periodoStr))
    ElseIf InStr(periodoStr, " ") > 0 Then
        ' Tenta converter "Janeiro 2026"
        mesAtual = Month(DateValue(periodoStr))
        anoAtual = Year(DateValue(periodoStr))
    Else
        ' Se não conseguir parsear, usa o mês e ano atual do sistema
        mesAtual = Month(Date)
        anoAtual = Year(Date)
        wsDashboard.Range("B3").Value = Format(Date, "MMMM/YYYY") ' Atualiza para o formato padrão
    End If

    ' --- Calcular Receitas Totais ---
    Dim totalReceitas As Double
    totalReceitas = Application.WorksheetFunction.SumIfs(wsReceitas.Range("E:E"), _
 wsReceitas.Range("B:B"), mesAtual, _
 wsReceitas.Range("C:C"), anoAtual)
    wsDashboard.Range("B5").Value = totalReceitas
    
    ' --- Calcular Despesas Totais ---
    Dim totalDespesas As Double
    totalDespesas = Application.WorksheetFunction.SumIfs(wsDespesas.Range("E:E"), _
 wsDespesas.Range("B:B"), mesAtual, _
 wsDespesas.Range("C:C"), anoAtual)
    wsDashboard.Range("B6").Value = totalDespesas
    
    ' --- Calcular Saldo Mensal ---
    wsDashboard.Range("B7").Value = totalReceitas - totalDespesas
    
    ' --- Calcular Taxa de Poupança ---
    If totalReceitas > 0 Then
        wsDashboard.Range("B8").Value = (totalReceitas - totalDespesas) / totalReceitas
        wsDashboard.Range("B8").NumberFormat = "0.00%"
    Else
        wsDashboard.Range("B8").Value = 0
    End If
    
    ' --- Maior Categoria de Gasto ---
    Dim dictCategories As Object
    Set dictCategories = CreateObject("Scripting.Dictionary")
    
    Dim lastRowDespesas As Long
    lastRowDespesas = modUtilitarios.GetNextEmptyRow(wsDespesas) - 1
    
    Dim i As Long
    For i = 2 To lastRowDespesas
        If wsDespesas.Cells(i, 2).Value = mesAtual And wsDespesas.Cells(i, 3).Value = anoAtual Then
            Dim cat As String
            Dim val As Double
            cat = wsDespesas.Cells(i, 6).Value
            val = wsDespesas.Cells(i, 5).Value
            
            If dictCategories.Exists(cat) Then
                dictCategories(cat) = dictCategories(cat) + val
            Else
                dictCategories.Add cat, val
            End If
        End If
    Next i
    
    Dim maxCat As String
    Dim maxVal As Double
    maxVal = 0
    
    If dictCategories.Count > 0 Then
        For Each cat In dictCategories.Keys
            If dictCategories(cat) > maxVal Then
                maxVal = dictCategories(cat)
                maxCat = cat
            End If
        Next cat
        wsDashboard.Range("B10").Value = maxCat & " (R$ " & Format(maxVal, "#,##0.00") & ")"
    Else
        wsDashboard.Range("B10").Value = "-"
    End If
    
    ' --- Atualizar Orçamento (Gasto Real) ---
    Dim lastRowOrcamento As Long
    lastRowOrcamento = modUtilitarios.GetNextEmptyRow(wsOrcamento) - 1
    
    For i = 2 To lastRowOrcamento
        Dim categoriaOrcamento As String
        categoriaOrcamento = wsOrcamento.Cells(i, 1).Value
        
        Dim gastoRealCat As Double
        gastoRealCat = Application.WorksheetFunction.SumIfs(wsDespesas.Range("E:E"), _
 wsDespesas.Range("B:B"), mesAtual, _
 wsDespesas.Range("C:C"), anoAtual, _
 wsDespesas.Range("F:F"), categoriaOrcamento)
        wsOrcamento.Cells(i, 3).Value = gastoRealCat
        
        ' Calcular % Usado
        Dim orcamentoMensal As Double
        orcamentoMensal = wsOrcamento.Cells(i, 2).Value
        If orcamentoMensal > 0 Then
            wsOrcamento.Cells(i, 4).Value = gastoRealCat / orcamentoMensal
            wsOrcamento.Cells(i, 4).NumberFormat = "0.00%"
        Else
            wsOrcamento.Cells(i, 4).Value = 0
        End If
    Next i
    
    ' --- Formatação Condicional para Orçamento ---
    Dim rngOrcamento As Range
    Set rngOrcamento = wsOrcamento.Range("D2:D" & lastRowOrcamento)
    
    ' Limpar regras existentes
    rngOrcamento.FormatConditions.Delete
    
    ' Regra 1: > 90% (Vermelho)
    rngOrcamento.FormatConditions.Add Type:=xlCellValue, Operator:=xlGreater, Formula1:="=0.9"
    rngOrcamento.FormatConditions(rngOrcamento.FormatConditions.Count).Interior.Color = RGB(255, 199, 206) ' Vermelho claro
    rngOrcamento.FormatConditions(rngOrcamento.FormatConditions.Count).Font.Color = RGB(156, 0, 6)
    
    ' Regra 2: > 70% e <= 90% (Amarelo)
    rngOrcamento.FormatConditions.Add Type:=xlCellValue, Operator:=xlBetween, Formula1:="=0.7", Formula2:="=0.9"
    rngOrcamento.FormatConditions(rngOrcamento.FormatConditions.Count).Interior.Color = RGB(255, 235, 156) ' Amarelo claro
    rngOrcamento.FormatConditions(rngOrcamento.FormatConditions.Count).Font.Color = RGB(156, 87, 0)
    
    ' Regra 3: <= 70% (Verde)
    rngOrcamento.FormatConditions.Add Type:=xlCellValue, Operator:=xlLessEqual, Formula1:="=0.7"
    rngOrcamento.FormatConditions(rngOrcamento.FormatConditions.Count).Interior.Color = RGB(198, 239, 206) ' Verde claro
    rngOrcamento.FormatConditions(rngOrcamento.FormatConditions.Count).Font.Color = RGB(0, 97, 0)
    
    ' Reabilitar atualização de tela e cálculo
    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True
    
    Exit Sub

ErrorHandler:
    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True
    MsgBox "Erro ao atualizar Dashboard: " & Err.Description, vbCritical, "Erro"
End Sub
"@

$vba_modUtilitarios = @"
Option Explicit

Function GetNextEmptyRow(ws As Worksheet) As Long
    On Error GoTo ErrorHandler
    GetNextEmptyRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row + 1
    Exit Function
ErrorHandler:
    GetNextEmptyRow = 2 ' Se houver erro, assume a linha 2 (primeira linha de dados)
End Function

Sub LogError(moduleName As String, errorMessage As String, Optional details As String = "")
    On Error Resume Next ' Evita loop de erro se o log falhar
    Dim wsLog As Worksheet
    Set wsLog = ThisWorkbook.Sheets("LOG")
    
    Dim nextRow As Long
    nextRow = GetNextEmptyRow(wsLog)
    
    wsLog.Cells(nextRow, 1).Value = Now
    wsLog.Cells(nextRow, 2).Value = moduleName
    wsLog.Cells(nextRow, 3).Value = errorMessage
    wsLog.Cells(nextRow, 4).Value = details
    
    wsLog.Range("A" & nextRow & ":D" & nextRow).Interior.Color = RGB(255, 240, 240) ' Rosa claro para erros
    wsLog.Range("A" & nextRow).NumberFormat = "dd/mm/yyyy hh:mm:ss"
End Sub
"@

$vba_ThisWorkbook = @"
Private Sub Workbook_Open()
    ' Chama a função de configuração ao abrir a pasta de trabalho
    Call modCore.SetupRibbonAndShortcuts
End Sub

Private Sub Workbook_BeforeClose(Cancel As Boolean)
    ' Limpa os atalhos ao fechar a pasta de trabalho
    Call modCore.CleanUpShortcuts
End Sub
"@

# --- Início do Script PowerShell ---
Write-Host "🚀 Iniciando a criação da planilha financeira automatizada..." -ForegroundColor Cyan

# 1. Verifica instalação do Excel
try {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false # Manter Excel invisível durante a criação
    Write-Host "✅ Excel encontrado e iniciado." -ForegroundColor Green
} catch {
    Write-Host "❌ Erro: Microsoft Excel não está instalado ou não pôde ser iniciado." -ForegroundColor Red
    Write-Host "Por favor, certifique-se de que o Excel 2016 ou superior esteja instalado." -ForegroundColor Yellow
    exit
}

# 2. Cria um novo Workbook
$workbook = $excel.Workbooks.Add()
$sheets = $workbook.Sheets
Write-Host "✅ Novo arquivo Excel criado." -ForegroundColor Green

# 3. Renomeia e cria as 10 abas
$sheetNames = @("DASHBOARD", "DESPESAS", "RECEITAS", "ORÇAMENTO", "ANÁLISE_MENSAL", "MEMBROS", "PARCELAMENTOS", "METAS", "INVESTIMENTOS", "LOG")

# Remove sheets extras se houver (Excel cria 3 por padrão)
while ($sheets.Count -gt $sheetNames.Count) {
    $sheets.Item($sheets.Count).Delete()
}

# Renomeia as existentes e adiciona as que faltam
for ($i = 0; $i -lt $sheetNames.Count; $i++) {
    if ($i -lt $sheets.Count) {
        $sheets.Item($i + 1).Name = $sheetNames[$i]
    } else {
        $sheets.Add().Name = $sheetNames[$i]
    }
}
Write-Host "✅ 10 abas criadas e renomeadas." -ForegroundColor Green

# Reordena as abas para a ordem desejada
for ($i = 0; $i -lt $sheetNames.Count; $i++) {
    $sheets.Item($sheetNames[$i]).Move($sheets.Item($i + 1))
}

# --- Estrutura e Dados de Exemplo ---

# Aba DESPESAS
$wsDespesas = $sheets.Item("DESPESAS")
$wsDespesas.Cells.ClearContents()
$wsDespesas.Range("A1:I1").Value = @("Data", "Mês", "Ano", "Descrição", "Valor", "Categoria", "Subcategoria", "Método_Pagamento", "Responsável")
$wsDespesas.Range("A1:I1").Font.Bold = $true
$wsDespesas.Range("A1:I1").Interior.Color = [System.Drawing.ColorTranslator]::ToOle([System.Drawing.Color]::FromArgb(66, 133, 244)) # Azul Google
$wsDespesas.Range("A1:I1").Font.Color = [System.Drawing.ColorTranslator]::ToOle([System.Drawing.Color]::White)
$wsDespesas.Columns.AutoFit()
$wsDespesas.Range("A:A").NumberFormat = "dd/mm/yyyy"
$wsDespesas.Range("E:E").NumberFormat = "R$ #,##0.00"

$despesasData = @(
    @("2026-01-15", 1, 2026, "Aluguel", 2500.00, "Moradia", "Aluguel", "Boleto", "Dr. Theo Vargas"),
    @("2026-01-16", 1, 2026, "Supermercado", 850.50, "Alimentação", "Compras Mensais", "Cartão de Crédito", "Emanuelly Vieira"),
    @("2026-01-17", 1, 2026, "Gasolina", 200.00, "Transporte", "Combustível", "Débito", "Dr. Theo Vargas"),
    @("2026-01-18", 1, 2026, "Mensalidade Escola", 700.00, "Educação", "Ensino Fundamental", "Boleto", "Maria Isis Leão"),
    @("2026-01-19", 1, 2026, "Netflix", 55.90, "Lazer", "Streaming", "Cartão de Crédito", "Dr. Theo Vargas"),
    @("2026-02-10", 2, 2026, "Conta de Luz", 180.00, "Moradia", "Contas de Consumo", "Boleto", "Emanuelly Vieira"),
    @("2026-02-12", 2, 2026, "Restaurante", 120.00, "Alimentação", "Refeição Fora", "Débito", "Dr. Theo Vargas"),
    @("2026-02-15", 2, 2026, "Academia", 90.00, "Saúde", "Mensalidade", "Cartão de Crédito", "Emanuelly Vieira"),
    @("2026-03-05", 3, 2026, "Consulta Médica", 300.00, "Saúde", "Consulta", "Dinheiro", "Maria Isis Leão"),
    @("2026-03-20", 3, 2026, "Roupas", 450.00, "Vestuário", "Compras Pessoais", "Cartão de Crédito", "Dr. Theo Vargas")
)
$wsDespesas.Range("A2").Resize($despesasData.Count, $despesasData[0].Count).Value = $despesasData

# Aba RECEITAS
$wsReceitas = $sheets.Item("RECEITAS")
$wsReceitas.Cells.ClearContents()
$wsReceitas.Range("A1:F1").Value = @("Data", "Mês", "Ano", "Descrição", "Valor", "Fonte")
$wsReceitas.Range("A1:F1").Font.Bold = $true
$wsReceitas.Range("A1:F1").Interior.Color = [System.Drawing.ColorTranslator]::ToOle([System.Drawing.Color]::FromArgb(52, 168, 83)) # Verde Google
$wsReceitas.Range("A1:F1").Font.Color = [System.Drawing.ColorTranslator]::ToOle([System.Drawing.Color]::White)
$wsReceitas.Columns.AutoFit()
$wsReceitas.Range("A:A").NumberFormat = "dd/mm/yyyy"
$wsReceitas.Range("E:E").NumberFormat = "R$ #,##0.00"

$receitasData = @(
    @("2026-01-05", 1, 2026, "Salário Dr. Theo", 8000.00, "Salário"),
    @("2026-01-05", 1, 2026, "Salário Emanuelly", 5000.00, "Salário"),
    @("2026-01-10", 1, 2026, "Freelance", 1200.00, "Trabalho Extra"),
    @("2026-02-05", 2, 2026, "Salário Dr. Theo", 8000.00, "Salário"),
    @("2026-02-05", 2, 2026, "Salário Emanuelly", 5000.00, "Salário"),
    @("2026-03-05", 3, 2026, "Salário Dr. Theo", 8000.00, "Salário")
)
$wsReceitas.Range("A2").Resize($receitasData.Count, $receitasData[0].Count).Value = $receitasData

# Aba DASHBOARD
$wsDashboard = $sheets.Item("DASHBOARD")
$wsDashboard.Cells.ClearContents()
$wsDashboard.Range("A1").Value = "📊 DASHBOARD FINANCEIRO FAMILIAR"
$wsDashboard.Range("A1").Font.Bold = $true
$wsDashboard.Range("A1").Font.Size = 16
$wsDashboard.Range("A1").Interior.Color = [System.Drawing.ColorTranslator]::ToOle([System.Drawing.Color]::FromArgb(234, 67, 53)) # Vermelho Google
$wsDashboard.Range("A1").Font.Color = [System.Drawing.ColorTranslator]::ToOle([System.Drawing.Color]::White)
$wsDashboard.Range("A1:C1").MergeCells = $true
$wsDashboard.Range("A1").HorizontalAlignment = -4108 # xlCenter

$wsDashboard.Range("A3").Value = "Período:"
$wsDashboard.Range("B3").Value = (Get-Date -Format "MMMM/yyyy") # Mês e ano atual
$wsDashboard.Range("B3").NumberFormat = "MMMM/YYYY"

$wsDashboard.Range("A5").Value = "💰 RECEITAS TOTAIS:"
$wsDashboard.Range("A6").Value = "💸 DESPESAS TOTAIS:"
$wsDashboard.Range("A7").Value = "💵 SALDO MENSAL:"
$wsDashboard.Range("A8").Value = "📈 TAXA DE POUPANÇA:"
$wsDashboard.Range("A10").Value = "🎯 MAIOR CATEGORIA:"

$wsDashboard.Range("A3:A10").Font.Bold = $true
$wsDashboard.Range("B5:B8").NumberFormat = "R$ #,##0.00"
$wsDashboard.Range("B8").NumberFormat = "0.00%"
$wsDashboard.Columns.AutoFit()

# Aba ORÇAMENTO
$wsOrcamento = $sheets.Item("ORÇAMENTO")
$wsOrcamento.Cells.ClearContents()
$wsOrcamento.Range("A1:D1").Value = @("Categoria", "Orçamento Mensal", "Gasto Real", "% Usado")
$wsOrcamento.Range("A1:D1").Font.Bold = $true
$wsOrcamento.Range("A1:D1").Interior.Color = [System.Drawing.ColorTranslator]::ToOle([System.Drawing.Color]::FromArgb(251, 188, 5)) # Amarelo Google
$wsOrcamento.Range("A1:D1").Font.Color = [System.Drawing.ColorTranslator]::ToOle([System.Drawing.Color]::Black)
$wsOrcamento.Columns.AutoFit()
$wsOrcamento.Range("B:C").NumberFormat = "R$ #,##0.00"
$wsOrcamento.Range("D:D").NumberFormat = "0.00%"

$orcamentoData = @(
    @("Alimentação", 1000.00, 0, 0),
    @("Transporte", 300.00, 0, 0),
    @("Moradia", 2800.00, 0, 0),
    @("Saúde", 400.00, 0, 0),
    @("Educação", 750.00, 0, 0),
    @("Lazer", 200.00, 0, 0),
    @("Vestuário", 150.00, 0, 0),
    @("Contas de Consumo", 300.00, 0, 0),
    @("Outros", 100.00, 0, 0)
)
$wsOrcamento.Range("A2").Resize($orcamentoData.Count, $orcamentoData[0].Count).Value = $orcamentoData

# Aba ANÁLISE_MENSAL (apenas cabeçalhos)
$wsAnaliseMensal = $sheets.Item("ANÁLISE_MENSAL")
$wsAnaliseMensal.Cells.ClearContents()
$wsAnaliseMensal.Range("A1:D1").Value = @("Mês/Ano", "Receitas", "Despesas", "Saldo")
$wsAnaliseMensal.Range("A1:D1").Font.Bold = $true
$wsAnaliseMensal.Range("A1:D1").Interior.Color = [System.Drawing.ColorTranslator]::ToOle([System.Drawing.Color]::LightGray)
$wsAnaliseMensal.Columns.AutoFit()
$wsAnaliseMensal.Range("B:D").NumberFormat = "R$ #,##0.00"

# Aba MEMBROS
$wsMembros = $sheets.Item("MEMBROS")
$wsMembros.Cells.ClearContents()
$wsMembros.Range("A1:C1").Value = @("Nome", "Ocupação", "Contribuição (%)")
$wsMembros.Range("A1:C1").Font.Bold = $true
$wsMembros.Range("A1:C1").Interior.Color = [System.Drawing.ColorTranslator]::ToOle([System.Drawing.Color]::LightBlue)
$wsMembros.Columns.AutoFit()
$wsMembros.Range("C:C").NumberFormat = "0.00%"

$membrosData = @(
    @("Dr. Theo Vargas", "Médico", 0.60),
    @("Emanuelly Vieira", "Designer", 0.40),
    @("Maria Isis Leão", "Estudante", 0.00)
)
$wsMembros.Range("A2").Resize($membrosData.Count, $membrosData[0].Count).Value = $membrosData

# Aba PARCELAMENTOS
$wsParcelamentos = $sheets.Item("PARCELAMENTOS")
$wsParcelamentos.Cells.ClearContents()
$wsParcelamentos.Range("A1:G1").Value = @("Descrição", "Valor Total", "Parcelas Totais", "Parcelas Pagas", "Valor Parcela", "Próximo Vencimento", "Responsável")
$wsParcelamentos.Range("A1:G1").Font.Bold = $true
$wsParcelamentos.Range("A1:G1").Interior.Color = [System.Drawing.ColorTranslator]::ToOle([System.Drawing.Color]::LightCoral)
$wsParcelamentos.Columns.AutoFit()
$wsParcelamentos.Range("B:E").NumberFormat = "R$ #,##0.00"
$wsParcelamentos.Range("F:F").NumberFormat = "dd/mm/yyyy"

$parcelamentosData = @(
    @("Geladeira Nova", 3000.00, 10, 2, 300.00, "2026-02-20", "Emanuelly Vieira"),
    @("Celular", 1500.00, 5, 1, 300.00, "2026-02-25", "Dr. Theo Vargas"),
    @("Curso Inglês", 1200.00, 12, 3, 100.00, "2026-02-10", "Maria Isis Leão")
)
$wsParcelamentos.Range("A2").Resize($parcelamentosData.Count, $parcelamentosData[0].Count).Value = $parcelamentosData

# Aba METAS
$wsMetas = $sheets.Item("METAS")
$wsMetas.Cells.ClearContents()
$wsMetas.Range("A1:D1").Value = @("Meta", "Valor Alvo", "Valor Atual", "Prazo (Meses)")
$wsMetas.Range("A1:D1").Font.Bold = $true
$wsMetas.Range("A1:D1").Interior.Color = [System.Drawing.ColorTranslator]::ToOle([System.Drawing.Color]::LightGreen)
$wsMetas.Columns.AutoFit()
$wsMetas.Range("B:C").NumberFormat = "R$ #,##0.00"

$metasData = @(
    @("Reserva de Emergência", 15000.00, 5000.00, 12),
    @("Viagem Férias", 8000.00, 1500.00, 8),
    @("Entrada Carro Novo", 20000.00, 2000.00, 24)
)
$wsMetas.Range("A2").Resize($metasData.Count, $metasData[0].Count).Value = $metasData

# Aba INVESTIMENTOS
$wsInvestimentos = $sheets.Item("INVESTIMENTOS")
$wsInvestimentos.Cells.ClearContents()
$wsInvestimentos.Range("A1:E1").Value = @("Ativo", "Tipo", "Valor Investido", "Valor Atual", "Rentabilidade (%)")
$wsInvestimentos.Range("A1:E1").Font.Bold = $true
$wsInvestimentos.Range("A1:E1").Interior.Color = [System.Drawing.ColorTranslator]::ToOle([System.Drawing.Color]::LightGoldenrodYellow)
$wsInvestimentos.Columns.AutoFit()
$wsInvestimentos.Range("C:D").NumberFormat = "R$ #,##0.00"
$wsInvestimentos.Range("E:E").NumberFormat = "0.00%"

$investimentosData = @(
    @("CDB Banco X", "Renda Fixa", 5000.00, 5200.00, 0.04),
    @("Fundo Imobiliário Y", "Renda Variável", 3000.00, 2900.00, -0.03),
    @("Tesouro Selic", "Renda Fixa", 2000.00, 2050.00, 0.025)
)
$wsInvestimentos.Range("A2").Resize($investimentosData.Count, $investimentosData[0].Count).Value = $investimentosData

# Aba LOG
$wsLog = $sheets.Item("LOG")
$wsLog.Cells.ClearContents()
$wsLog.Range("A1:D1").Value = @("Data/Hora", "Módulo", "Erro", "Detalhes")
$wsLog.Range("A1:D1").Font.Bold = $true
$wsLog.Range("A1:D1").Interior.Color = [System.Drawing.ColorTranslator]::ToOle([System.Drawing.Color]::LightSlateGray)
$wsLog.Range("A1:D1").Font.Color = [System.Drawing.ColorTranslator]::ToOle([System.Drawing.Color]::White)
$wsLog.Columns.AutoFit()
$wsLog.Range("A:A").NumberFormat = "dd/mm/yyyy hh:mm:ss"

Write-Host "✅ Estrutura das abas e dados de exemplo adicionados." -ForegroundColor Green

# --- Injetar Código VBA ---
Write-Host "⚙️ Injetando código VBA na planilha..." -ForegroundColor Yellow

# Habilitar acesso programático ao projeto VBA
$excel.AutomationSecurity = 1 # msoAutomationSecurityForceDisable (temporariamente para injetar VBA)
$excel.DisplayAlerts = $false # Desabilitar alertas para evitar pop-ups de segurança

try {
    # Injetar módulos padrão
    Inject-VBA $workbook "modCore" $vba_modCore
    Inject-VBA $workbook "modDataEntry" $vba_modDataEntry
    Inject-VBA $workbook "modDashboard" $vba_modDashboard
    Inject-VBA $workbook "modUtilitarios" $vba_modUtilitarios

    # Injetar código no módulo ThisWorkbook
    Inject-ThisWorkbookVBA $workbook $vba_ThisWorkbook

    Write-Host "✅ Código VBA injetado com sucesso." -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao injetar código VBA: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Certifique-se de que 'Confiar no acesso ao modelo de objeto do projeto VBA' está habilitado nas configurações de macro do Excel." -ForegroundColor Yellow
    # Reverter configurações de segurança antes de sair
    $excel.AutomationSecurity = 3 # msoAutomationSecurityLow
    $excel.DisplayAlerts = $true
    $excel.Quit()
    Remove-Variable excel
    exit
} finally {
    # Reverter configurações de segurança
    $excel.AutomationSecurity = 3 # msoAutomationSecurityLow (Permitir macros com aviso)
    $excel.DisplayAlerts = $true
}

# --- Salvar e Fechar ---
Write-Host "💾 Salvando a planilha como '$outputPath'..." -ForegroundColor Yellow
$workbook.SaveAs($outputPath, 52) # 52 = xlOpenXMLWorkbookMacroEnabled
$workbook.Close()
$excel.Quit()
Remove-Variable excel
Write-Host "✅ Planilha criada e salva com sucesso em '$outputPath'." -ForegroundColor Green
Write-Host "🎉 Processo de automação concluído!" -ForegroundColor Green
# Fim do Script PowerShell