# SISTEMA DE ATUALIZAÇÃO DE VALORES E CALCULADORA DE JUROS

## Visão Geral

Sistema completo para cálculo automático de juros e correção monetária de precatórios,
com histórico de atualizações e detalhamento mês a mês.

## Funcionalidades Implementadas

### 1. Calculadora Avançada

**Cálculos disponíveis:**
- Juros Simples
- Juros Compostos
- Correção Monetária (IPCA, INPC, TR)
- Detalhamento mês a mês

**Parâmetros configuráveis:**
- Valor Principal
- Data Base
- Data Final
- Taxa de Juros Mensal (%)
- Índice de Correção
- Tipo de Juros

### 2. Índices de Correção

**IPCA (Índice Nacional de Preços ao Consumidor Amplo):**
- 2020: 4,52%
- 2021: 10,06%
- 2022: 5,79%
- 2023: 4,62%
- 2024: 4,50%
- 2025: 4,20%
- 2026: 4,00%

**INPC (Índice Nacional de Preços ao Consumidor):**
- 2020: 5,45%
- 2021: 10,16%
- 2022: 5,93%
- 2023: 3,71%
- 2024: 4,30%
- 2025: 4,10%
- 2026: 3,90%

**TR (Taxa Referencial):**
- 2020: 0,00%
- 2021: 0,00%
- 2022: 0,73%
- 2023: 0,85%
- 2024: 0,60%
- 2025: 0,50%
- 2026: 0,40%

### 3. Histórico de Atualizações

Cada atualização registra:
- Data e hora
- Valor principal
- Juros calculados
- Correção monetária
- Valor total
- Taxa de juros utilizada
- Índice de correção
- Período do cálculo
- Usuário responsável

### 4. Detalhamento Mensal

Exibe mês a mês:
- Valor inicial do mês
- Juros do período
- Correção do período
- Valor final do mês

## Como Usar

### Passo 1: Acessar Calculadora

1. Vá para detalhes do processo
2. Localize o card "Atualização de Valores"
3. Clique em "Calcular Valores"

### Passo 2: Preencher Dados

1. **Valor Principal**: Valor base do precatório
2. **Data Base**: Data inicial para cálculo
3. **Data Final**: Data final (geralmente hoje)
4. **Taxa de Juros**: Taxa mensal (padrão: 0,5%)
5. **Índice de Correção**: IPCA, INPC ou TR
6. **Tipo de Juros**: Simples ou Compostos

### Passo 3: Calcular

1. Clique em "🧮 CALCULAR VALORES"
2. Aguarde o resultado
3. Verifique os valores calculados

### Passo 4: Salvar

1. Clique em "Salvar Atualização"
2. Confirme a operação
3. Os valores serão salvos no processo e no histórico

### Passo 5: Ver Detalhamento (Opcional)

1. Clique em "Ver Detalhamento Mensal"
2. Analise a evolução mês a mês
3. Exporte se necessário

## Exemplos de Cálculo

### Exemplo 1: Precatório Alimentar

**Dados:**
- Valor Principal: R\$ 100.000,00
- Data Base: 01/01/2020
- Data Final: 05/01/2026
- Taxa Juros: 0,5% ao mês
- Índice: IPCA
- Tipo: Juros Simples

**Resultado:**
- Período: 73 meses
- Juros: R\$ 36.500,00 (73 × 0,5% × 100.000)
- Correção IPCA: ~R\$ 38.000,00
- **Valor Total: R\$ 174.500,00**

### Exemplo 2: Precatório Tributário

**Dados:**
- Valor Principal: R\$ 500.000,00
- Data Base: 01/01/2022
- Data Final: 05/01/2026
- Taxa Juros: 1,0% ao mês
- Índice: INPC
- Tipo: Juros Compostos

**Resultado:**
- Período: 49 meses
- Juros Compostos: ~R\$ 320.000,00
- Correção INPC: ~R\$ 85.000,00
- **Valor Total: R\$ 905.000,00**

## Campos Adicionados ao Banco

### Tabela processos:
- alor_principal (FLOAT)
- alor_juros (FLOAT)
- alor_correcao_monetaria (FLOAT)
- 	axa_juros_mensal (FLOAT)
- indice_correcao (VARCHAR)
- data_base_calculo (DATE)
- data_ultima_atualizacao_valor (DATETIME)

### Tabela historico_valores:
- id (INTEGER PRIMARY KEY)
- processo_id (INTEGER)
- data_atualizacao (DATETIME)
- alor_principal (FLOAT)
- alor_juros (FLOAT)
- alor_correcao (FLOAT)
- alor_total (FLOAT)
- 	axa_juros (FLOAT)
- indice_correcao (VARCHAR)
- periodo_inicio (DATE)
- periodo_fim (DATE)
- observacoes (TEXT)
- usuario (VARCHAR)

## APIs Disponíveis

### POST /api/calcular-valores

Calcula valores de juros e correção.

**Request:**
\\\json
{
  "processo_id": 1,
  "valor_principal": 100000.00,
  "data_base": "2020-01-01",
  "data_final": "2026-01-05",
  "taxa_juros": 0.5,
  "indice_correcao": "IPCA",
  "tipo_juros": "SIMPLES"
}
\\\

**Response:**
\\\json
{
  "valor_principal": 100000.00,
  "valor_juros": 36500.00,
  "valor_correcao": 38000.00,
  "valor_total": 174500.00,
  "meses_calculados": 73,
  "taxa_juros_mensal": 0.5,
  "indice_correcao": "IPCA",
  "tipo_juros": "SIMPLES",
  "data_base": "01/01/2020",
  "data_final": "05/01/2026"
}
\\\

### POST /api/detalhamento-mensal

Gera detalhamento mês a mês.

**Request:**
\\\json
{
  "valor_principal": 100000.00,
  "data_base": "2020-01-01",
  "data_final": "2026-01-05",
  "taxa_juros": 0.5,
  "indice_correcao": "IPCA"
}
\\\

**Response:**
\\\json
[
  {
    "mes": "01/2020",
    "valor_inicial": 100000.00,
    "juros": 500.00,
    "correcao": 376.67,
    "valor_final": 100876.67
  },
  ...
]
\\\

## Fórmulas Utilizadas

### Juros Simples

\\\
Juros = Principal × (Taxa / 100) × Meses
\\\

### Juros Compostos

\\\
Montante = Principal × (1 + Taxa/100)^Meses
Juros = Montante - Principal
\\\

### Correção Monetária

\\\
Valor Corrigido = Principal × ∏(1 + Índice_Ano/100)
Correção = Valor Corrigido - Principal
\\\

## Manutenção

### Atualizar Índices

Edite o arquivo src/calculadora_juros.py:

\\\python
INDICES_IPCA = {
    2026: 4.00,  # Atualizar com valor real
    2027: 0.00   # Adicionar novo ano
}
\\\

### Backup

O histórico de valores é preservado na tabela historico_valores.

### Auditoria

Todas as atualizações são registradas com data, hora e usuário.

## Troubleshooting

### Erro ao calcular

- Verifique se as datas são válidas
- Certifique-se de que data final > data base
- Verifique se o valor principal é positivo

### Valores inconsistentes

- Verifique os índices de correção
- Confirme a taxa de juros
- Revise o tipo de juros (simples vs compostos)

### Erro ao salvar

- Verifique permissões do banco de dados
- Confirme que o processo existe
- Revise os logs do servidor

## Próximas Melhorias

1. **Importação de Índices**: Buscar índices automaticamente de APIs oficiais
2. **Múltiplos Índices**: Permitir usar diferentes índices por período
3. **Exportação**: Gerar PDF com cálculo detalhado
4. **Gráficos**: Visualizar evolução dos valores
5. **Comparação**: Comparar diferentes cenários de cálculo

---

**Versão:** 1.0  
**Data:** 05/01/2026 20:04:52
