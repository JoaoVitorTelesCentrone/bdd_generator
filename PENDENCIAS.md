# Pendências — BDD Generator

> Auditoria completa do projeto. Organizado por prioridade.

---

## 🔴 Alta Prioridade

### 1. RunPanel não está integrado às páginas de resultado
- `GeneratePanel.tsx` não exibe RunPanel após gerar o BDD
- `StoryCreatorPanel.tsx` não exibe RunPanel após criar a história
- O componente `RunPanel.tsx` existe mas não é usado nessas telas
- Mencionado em `plano_front_e2e.md` como pendente

### 2. Página `/planos` não existe
- `web/src/app/api/stripe/checkout/route.ts:47` redireciona para `/planos`
- O arquivo `web/src/app/planos/page.tsx` não existe
- Stripe retorna 404 após checkout bem-sucedido

### 3. Stripe com dados placeholder
- `web/.env.local` tem `pk_test_COLOQUE_AQUI`, `sk_test_COLOQUE_AQUI` etc.
- Billing não funciona até as chaves reais serem inseridas
- Handler do webhook Stripe (`/api/webhooks/stripe`) provavelmente incompleto

### 4. Autenticação Google desabilitada na UI
- `web/src/app/login/page.tsx:70-77` — botão Google com `cursor-not-allowed` e texto "em breve"
- `web/src/middleware.ts` — todas as rotas são públicas (auth comentada)
- Infraestrutura Supabase/OAuth está pronta, só a UI está bloqueada

---

## 🟡 Média Prioridade

### 5. Histórico só salva no localStorage (sem usuário logado)
- `web/src/lib/history.ts` — usa `localStorage`
- `GeneratePanel.tsx:54` chama `saveGeneration()` (Supabase) apenas se houver usuário
- Sem login, nenhuma geração persiste no banco

### 6. Sem timeout nas requisições da API
- `web/src/lib/api.ts:18-28` — `fetch` sem timeout
- Geração de BDD pode levar minutos; sem timeout o usuário fica travado
- Sem cancelamento de request ao navegar para outra página

### 7. WebSocket sem lógica de reconexão
- `web/src/app/runs/[id]/page.tsx:47` — `onerror` apenas adiciona texto ao log
- Se a conexão cair no meio de um run, não há retry
- `LiveLog` cria o WebSocket imediatamente, sem aguardar o run existir

### 8. CLI integration incompleta
- `web/src/app/api/cli/me/route.ts` — provavelmente incompleto
- `web/src/app/api/cli/quota/route.ts` — provavelmente incompleto
- Funções `getQuota` e `trackUsage` referenciadas mas não validadas end-to-end

### 9. Migração de banco com falha silenciosa
- `bist/bist_database.py:83-86` — `except Exception: pass`
- Novas colunas/tabelas podem não ser criadas sem qualquer aviso
- Dificulta diagnóstico em produção

### 10. Página de configurações (`/settings`) não existe
- Não há UI para gerenciar chaves de API do tenant
- Não há UI para ver uso/quota
- Rotas backend existem (`GET /api/tenants/{id}/api-keys` etc.) mas sem tela

---

## 🟢 Baixa Prioridade / Polish

### 11. SSO/SAML sem interface
- `bist/bist_sso.py` — rotas SAML implementadas no backend
- Nenhum frontend para configurar ou testar SAML
- Provavelmente só relevante para clientes enterprise

### 12. Mensagens de erro genéricas
- Vários `catch (e: any)` apenas usam `e.message`
- Backend tem `except Exception as exc: str(exc)` sem estrutura
- Usuário não sabe o que fazer com "Internal server error"

### 13. Sem exibição de quota/limite na UI
- Backend tem sistema de tiers e limites
- Frontend não mostra quanto o usuário já usou
- Usuário só descobre o limite quando recebe erro 402

### 14. Acessibilidade
- Botões sem `aria-label`
- Live log sem `aria-live="polite"`
- Foco de teclado não gerenciado em modais

### 15. Sem validação de variáveis de ambiente na inicialização
- App sobe sem checar se `GEMINI_API_KEY`, `ANTHROPIC_API_KEY` etc. estão presentes
- Falha apenas na primeira chamada, com erro confuso

---

## 📋 Resumo por área

| Área                    | Status | Principal pendência                        |
|-------------------------|--------|--------------------------------------------|
| Geração de BDD          | ✅ OK  | —                                          |
| Avaliação de BDD        | ✅ OK  | —                                          |
| Criação de histórias    | ✅ OK  | Falta integrar RunPanel ao final do fluxo  |
| Execução de testes      | ⚠️ 90% | RunPanel não aparece após gerar BDD        |
| Histórico & Stats       | ✅ OK  | —                                          |
| Autenticação            | ⚠️ 50% | UI do Google desabilitada                  |
| Billing / Stripe        | ⚠️ 40% | Chaves placeholder, página /planos ausente |
| CLI                     | ⚠️ 60% | Endpoints me/quota incompletos             |
| Multi-tenant / API Keys | ⚠️ 70% | Backend pronto, sem tela de configurações  |
| SSO / SAML              | ⚠️ 70% | Backend pronto, sem frontend               |
| Confiabilidade          | ⚠️ 70% | Sem timeout, sem reconexão WS              |
