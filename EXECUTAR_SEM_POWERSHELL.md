# TAX MASTER v2.0 - EXECUTAR SEM POWERSHELL ABERTO

## Problema
O servidor Flask precisa do PowerShell/CMD aberto porque está rodando em modo de desenvolvimento.

## Soluções Disponíveis

### 🚀 SOLUÇÃO 1: Background (Mais Simples)

**Execute:** `start_background.bat`

- Inicia o servidor em segundo plano usando `pythonw.exe`
- Você pode fechar o PowerShell
- O servidor continua rodando
- Para parar: execute `stop_server.bat`

**Vantagens:**
- ✅ Simples e rápido
- ✅ Não precisa instalar nada
- ✅ Funciona imediatamente

**Desvantagens:**
- ❌ Precisa iniciar manualmente após reiniciar o PC
- ❌ Não reinicia automaticamente se travar

### 🏆 SOLUÇÃO 2: Serviço do Windows (Recomendado para Produção)

**Pré-requisito:** Instalar NSSM
1. Baixe: https://nssm.cc/download
2. Extraia `nssm.exe` para `C:\Windows\System32`

**Execute:** `install_service.bat`

- Instala o Tax Master como serviço do Windows
- Inicia automaticamente com o Windows
- Reinicia automaticamente se travar
- Gerenciável pelo Windows Services

**Vantagens:**
- ✅ Inicia automaticamente com Windows
- ✅ Reinicia automaticamente
- ✅ Robusto e profissional
- ✅ Logs automáticos

**Gerenciar Serviço:**
\\\atch
nssm start TaxMaster      # Iniciar
nssm stop TaxMaster       # Parar
nssm restart TaxMaster    # Reiniciar
nssm remove TaxMaster confirm  # Remover
\\\

### 📌 SOLUÇÃO 3: Atalho no Desktop

**Execute:** `create_shortcut.ps1` no PowerShell

Cria atalho na área de trabalho:
- Duplo clique inicia o servidor em background
- Mais fácil para usuários finais

### 🔄 SOLUÇÃO 4: Inicialização Automática

**Execute:** `enable_autostart.bat`

- Adiciona o Tax Master na pasta de inicialização do Windows
- Servidor inicia automaticamente ao fazer login

**Para desabilitar:**
- Vá para: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`
- Delete o atalho `TaxMaster.lnk`

## Menu Principal

**Execute:** `TaxMaster_Menu.bat`

Menu interativo com todas as opções:
1. Iniciar em background
2. Iniciar normal
3. Parar servidor
4. Verificar status
5. Abrir navegador
6-9. Outras opções

## Verificar Status

**Execute:** `status_server.bat`

Mostra:
- Processos Python rodando
- Status do servidor (online/offline)
- Status do serviço (se instalado)

## Como Usar (Passo a Passo)

### Para Uso Diário (Simples):

1. Execute `start_background.bat`
2. Acesse: http://localhost:8080
3. Para parar: execute `stop_server.bat`

### Para Produção (Recomendado):

1. Instale NSSM (uma vez)
2. Execute `install_service.bat` (uma vez)
3. Pronto! O servidor rodará sempre

### Para Computador Pessoal:

1. Execute `enable_autostart.bat` (uma vez)
2. Reinicie o PC
3. O Tax Master iniciará automaticamente

## Troubleshooting

### Erro: "pythonw não encontrado"
- Instale Python corretamente
- Certifique-se de que Python está no PATH

### Erro: "NSSM não encontrado"
- Baixe NSSM de: https://nssm.cc/download
- Coloque em C:\Windows\System32

### Servidor não responde
1. Execute `status_server.bat`
2. Verifique os logs em `logs/`
3. Execute `stop_server.bat` e inicie novamente

### Porta 8080 em uso
- Outro aplicativo está usando a porta
- Pare o outro aplicativo ou altere a porta no `app.py`

## Comparação das Soluções

| Solução | Simplicidade | Auto-Start | Robustez | Produção |
|---------|--------------|------------|----------|----------|
| Background | ⭐⭐⭐⭐⭐ | ❌ | ⭐⭐⭐ | ❌ |
| Serviço Windows | ⭐⭐⭐ | ✅ | ⭐⭐⭐⭐⭐ | ✅ |
| Autostart | ⭐⭐⭐⭐ | ✅ | ⭐⭐⭐ | ❌ |
| Atalho Desktop | ⭐⭐⭐⭐⭐ | ❌ | ⭐⭐⭐ | ❌ |

## Recomendações

**Para Desenvolvimento:**
- Use `start_background.bat` ou `TaxMaster_Menu.bat`

**Para Produção Local:**
- Use **Serviço do Windows** (`install_service.bat`)

**Para Servidor Dedicado:**
- Use **Gunicorn + Nginx** (veja `GUIA_PRODUCAO_COMPLETO.md`)

## Logs

**Servidor normal:**
- Console output

**Background:**
- Sem logs visíveis (use Task Manager)

**Serviço Windows:**
- `logs/service_output.log`
- `logs/service_error.log`

## Comandos Úteis

\\\atch
# Listar processos Python
tasklist | findstr python

# Matar processos Python
taskkill /F /IM python.exe
taskkill /F /IM pythonw.exe

# Verificar porta 8080
netstat -ano | findstr 8080

# Gerenciar serviços Windows
services.msc
\\\

---

**Versão:** 2.0  
**Data:** 06/01/2026
