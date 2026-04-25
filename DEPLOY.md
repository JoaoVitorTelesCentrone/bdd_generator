# Deploy — BDD Generator

Arquitetura de produção:

```
Vercel (Next.js)  →  Railway (FastAPI)  →  Gemini API
     grátis              ~$5/mês             ~$5/mês
                    ↕
               Supabase (Auth + DB)
                   grátis
```

---

## Pré-requisitos

- Conta no [Railway](https://railway.app)
- Conta no [Vercel](https://vercel.com)
- Conta no [Supabase](https://supabase.com)
- Chave da [Gemini API](https://aistudio.google.com/app/apikey)
- Repositório no GitHub com o código

---

## 1. Supabase

### 1.1 Criar projeto
1. Acesse [supabase.com](https://supabase.com) → **New Project**
2. Escolha um nome e senha para o banco
3. Região: **South America (São Paulo)**

### 1.2 Rodar migrations
1. No painel do Supabase, vá em **SQL Editor**
2. Cole e execute o conteúdo de `web/supabase/migrations/001_init.sql`

### 1.3 Pegar as chaves
Vá em **Settings > API**:

```
NEXT_PUBLIC_SUPABASE_URL      → "Project URL"
NEXT_PUBLIC_SUPABASE_ANON_KEY → "anon public"
SUPABASE_SERVICE_ROLE_KEY     → "service_role" (⚠️ nunca exponha no frontend)
```

---

## 2. Railway (Backend)

### 2.1 Criar projeto
1. Acesse [railway.app](https://railway.app) → **New Project**
2. Escolha **Deploy from GitHub repo**
3. Selecione o repositório

### 2.2 Configurar variáveis de ambiente
Vá em **Settings > Variables** e adicione:

```
GEMINI_API_KEY        → sua chave do Google AI Studio
GROQ_API_KEY          → sua chave do Groq (opcional)
FRONTEND_URL          → URL do Vercel (preencha depois do passo 3)
```

> Após configurar o Vercel, volte aqui e preencha `FRONTEND_URL`.

### 2.3 Configurar domínio
1. Vá em **Settings > Networking**
2. Clique em **Generate Domain**
3. Anote a URL gerada (ex: `https://bdd-generator-production.up.railway.app`)

### 2.4 Verificar deploy
Acesse `https://<sua-url-railway>/health` — deve retornar:
```json
{ "status": "ok", "version": "1.0.0" }
```

---

## 3. Vercel (Frontend)

### 3.1 Criar projeto
1. Acesse [vercel.com](https://vercel.com) → **Add New Project**
2. Importe o repositório do GitHub
3. Em **Root Directory**, coloque: `web`
4. Framework: **Next.js** (detectado automaticamente)

### 3.2 Configurar variáveis de ambiente
Em **Settings > Environment Variables**, adicione todas para os ambientes **Production**, **Preview** e **Development**:

```
# Backend
NEXT_PUBLIC_API_URL              → https://<sua-url-railway>/api

# Supabase
NEXT_PUBLIC_SUPABASE_URL         → https://<ref>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY    → eyJ...
SUPABASE_SERVICE_ROLE_KEY        → eyJ...  (⚠️ marcar como "Sensitive")

# Stripe (preencha quando tiver conta no Stripe)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY → pk_live_...
STRIPE_SECRET_KEY                  → sk_live_...
STRIPE_WEBHOOK_SECRET              → whsec_...
NEXT_PUBLIC_STRIPE_PRICE_PRO       → price_...
```

### 3.3 Deploy
Clique em **Deploy**. A Vercel vai buildar e publicar automaticamente.

Anote a URL gerada (ex: `https://bdd-generator.vercel.app`).

### 3.4 Voltar ao Railway
Preencha `FRONTEND_URL` no Railway com a URL do Vercel:
```
FRONTEND_URL = https://bdd-generator.vercel.app
```

---

## 4. Stripe (Pagamentos)

> Pode deixar para depois. Sem as chaves Stripe o sistema funciona normalmente, apenas sem cobrança.

### 4.1 Criar conta e produto
1. Acesse [dashboard.stripe.com](https://dashboard.stripe.com)
2. Vá em **Products** → **Add Product**
3. Nome: `Pro`, Preço: `R$ 97/mês` (recorrente)
4. Anote o **Price ID** (ex: `price_1ABC...`)

### 4.2 Configurar webhook
1. Vá em **Developers > Webhooks** → **Add endpoint**
2. URL: `https://<sua-url-vercel>/api/webhooks/stripe`
3. Eventos a escutar:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_failed`
4. Anote o **Signing secret** (`whsec_...`)

### 4.3 Atualizar variáveis no Vercel
Preencha as variáveis Stripe que ficaram em branco no passo 3.2.

---

## 5. Checklist final

Antes de anunciar o produto, verifique:

- [ ] `https://<railway>/health` retorna `200 OK`
- [ ] Login com Supabase funciona no frontend
- [ ] Geração de BDD funciona end-to-end
- [ ] `FRONTEND_URL` no Railway aponta para o domínio Vercel correto
- [ ] `.env` e `.env.local` estão no `.gitignore` e **não** foram commitados

---

## 6. Deploys futuros

Todo `git push` para a branch `main`:
- **Vercel** faz redeploy do frontend automaticamente
- **Railway** faz redeploy do backend automaticamente

Não é necessário nenhum comando manual.
