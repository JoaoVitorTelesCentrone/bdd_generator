# Pendências — BDD Generator

> Auditoria completa do projeto. Organizado por prioridade.

---

## ✅ Resolvido

| Item | Como foi resolvido |
|------|--------------------|
| RunPanel não integrado | Já estava integrado em `GeneratePanel.tsx:225` e `StoryCreatorPanel.tsx:253` |
| Login Google desabilitado | Já estava funcional em `login/page.tsx` |
| API URL hardcoded | Já era dinâmico via `NEXT_PUBLIC_API_URL` em `api.ts:16` |
| Página `/planos` inexistente | Já existia em `web/src/app/planos/page.tsx` |
| Botão "Assinar Pro" (GET em vez de POST) | Corrigido com `PlanCheckoutButton.tsx` (client component com fetch POST) |
| CORS sem suporte à URL de produção | Corrigido em `backend/main.py` via `FRONTEND_URL` env var |
| `ANTHROPIC_API_KEY` ausente no `.env` | Adicionado como placeholder |
| Sem arquivos de exemplo para env vars | Criados: `.env.example` e `web/.env.local.example` |
| Sem migration SQL do Supabase | Criado: `web/supabase/migrations/001_init.sql` |

---

## 🔴 Alta Prioridade — Falta só preencher credenciais

### 1. Stripe — 4 valores para preencher
- **Arquivo:** `web/.env.local`
- **O que preencher:**
  - `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` → Stripe Dashboard > API Keys > Publishable key
  - `STRIPE_SECRET_KEY` → Stripe Dashboard > API Keys > Secret key
  - `STRIPE_WEBHOOK_SECRET` → Stripe Dashboard > Webhooks > Signing secret
  - `NEXT_PUBLIC_STRIPE_PRICE_PRO` → Stripe Dashboard > Products > Pro > Price ID
- **Referência:** `web/.env.local.example`

### 2. Anthropic API Key
- **Arquivo:** `.env`
- **O que preencher:** `ANTHROPIC_API_KEY` → console.anthropic.com/settings/keys

### 3. Migration SQL do Supabase
- **Arquivo:** `web/supabase/migrations/001_init.sql`
- **O que fazer:** Executar no SQL Editor do painel Supabase
  - URL: `https://supabase.com/dashboard/project/<ref>/sql/new`
  - Cria as tabelas: `subscriptions`, `cli_usage`, `generations`

### 4. URL de produção
- **Backend:** adicionar `FRONTEND_URL=https://seudominio.com` no `.env`
- **Frontend:** descomentar `NEXT_PUBLIC_API_URL=https://api.seudominio.com/api` no `.env.local`

---

## 🟡 Média Prioridade

### 5. Histórico só salva no localStorage (sem usuário logado)
- `web/src/lib/history.ts` — usa `localStorage`
- `GeneratePanel.tsx:56` chama `saveGeneration()` (Supabase) apenas se houver usuário
- Sem login, nenhuma geração persiste no banco

### 6. WebSocket sem lógica de reconexão robusta
- `web/src/app/runs/[id]/page.tsx:47` — `onerror` apenas adiciona texto ao log
- Se a conexão cair no meio de um run, não há retry automático

### 7. CLI integration incompleta
- `web/src/app/api/cli/me/route.ts` — provavelmente incompleto
- `web/src/app/api/cli/quota/route.ts` — provavelmente incompleto
- Funções `getQuota` e `trackUsage` não validadas end-to-end

### 8. Migração de banco com falha silenciosa
- `bist/bist_database.py:83-86` — `except Exception: pass`
- Novas colunas/tabelas podem não ser criadas sem qualquer aviso

### 9. Página de configurações (`/settings`) incompleta
- Não há UI para gerenciar chaves de API do tenant
- Não há UI para gerar novo token CLI

---

## 🟢 Baixa Prioridade / Polish

### 10. SSO/SAML sem interface
- `bist/bist_sso.py` — rotas SAML implementadas no backend
- Nenhum frontend para configurar ou testar SAML

### 11. Mensagens de erro genéricas
- Backend tem `except Exception as exc: str(exc)` sem estrutura
- Usuário não sabe o que fazer com "Internal server error"

### 12. Sem exibição de quota/limite na UI durante geração
- Backend tem sistema de tiers e limites
- Usuário só descobre o limite quando recebe erro 402

### 13. Acessibilidade
- Botões sem `aria-label`
- Live log sem `aria-live="polite"`
- Foco de teclado não gerenciado em modais

---

## 📋 Resumo por área

| Área                    | Status | Principal pendência                        |
|-------------------------|--------|--------------------------------------------|
| Geração de BDD          | ✅ OK  | —                                          |
| Avaliação de BDD        | ✅ OK  | —                                          |
| Criação de histórias    | ✅ OK  | —                                          |
| Execução de testes      | ✅ OK  | RunPanel integrado                         |
| Histórico & Stats       | ✅ OK  | —                                          |
| Autenticação            | ✅ OK  | Login Google funcional                     |
| Billing / Stripe        | ⚠️ 90% | Só falta chaves reais + migration Supabase |
| CLI                     | ⚠️ 60% | Endpoints me/quota incompletos             |
| Multi-tenant / API Keys | ⚠️ 70% | Backend pronto, sem tela de configurações  |
| SSO / SAML              | ⚠️ 70% | Backend pronto, sem frontend               |
| Confiabilidade          | ⚠️ 70% | Sem reconexão WS robusta                   |
