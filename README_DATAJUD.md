# Tax Master V3 - Busca Real CNJ DataJud

## 🔐 Configurar Credenciais DataJud

### Passo 1: Criar Conta
Acesse: https://www.cnj.jus.br/sistemas/datajud/api-publica/
E siga as instruções para criar uma conta.

### Passo 2: Obter Credenciais
Após criar a conta, você receberá:
- Usuário
- Senha

### Passo 3: Configurar no Railway
No Railway Dashboard:
1. Acesse seu projeto
2. Vá em "Variables"
3. Adicione:
   - `DATAJUD_USER` = seu_usuario
   - `DATAJUD_PASS` = sua_senha

### Passo 4: Redeploy
Após adicionar as variáveis, faça um novo deploy.

## ✅ Como Usar

1. Faça login: admin@taxmaster.com / admin123
2. Clique em "Buscar no TJ-SP"
3. Configure os filtros (Valor, Natureza, Ano)
4. Os processos REAIS aparecerão!

## 📋 Funcionalidades

✅ Busca REAL na API DataJud CNJ (oficial)
✅ Filtros: Valor, Tribunal, Natureza, Ano LOA
✅ Cache de 30 minutos (performance)
✅ Importação de planilhas Excel/CSV
✅ Sistema de autenticação JWT
✅ Multiusuário

## 🔗 Links Úteis

- API DataJud: https://www.cnj.jus.br/sistemas/datajud/api-publica/
- Documentação: https://datajud-wiki.cnj.jus.br/api-publica/
- Tutorial PDF: https://www.cnj.jus.br/wp-content/uploads/2023/05/tutorial-api-publica-datajud-beta.pdf
