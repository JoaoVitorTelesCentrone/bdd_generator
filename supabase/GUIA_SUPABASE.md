# Guia de Configuração — Supabase

## 1. Criar projeto

1. Acesse [supabase.com](https://supabase.com) → **New project**
2. Escolha nome, senha do banco e região (preferencialmente **South America (São Paulo)**)
3. Aguarde o projeto inicializar (~2 min)

---

## 2. Executar o schema SQL

1. No dashboard, vá em **SQL Editor** → **New query**
2. Cole o conteúdo de `supabase/schema.sql` e clique em **Run**
3. Cole o conteúdo de `supabase/stripe_schema.sql` e clique em **Run**
4. Confirme que as tabelas aparecem em **Table Editor**: `profiles`, `generations`, `subscriptions`

---

## 3. Configurar autenticação com Google

### 3.1 Google Cloud Console

1. Acesse [console.cloud.google.com](https://console.cloud.google.com)
2. Crie um projeto (ou use um existente)
3. Vá em **APIs & Services → OAuth consent screen**
   - User Type: **External**
   - Preencha nome do app, e-mail de suporte
   - Scopes: adicione `email` e `profile`
4. Vá em **APIs & Services → Credentials → Create Credentials → OAuth Client ID**
   - Application type: **Web application**
   - Authorized redirect URIs: adicione exatamente:
     ```
     https://<SEU_PROJETO>.supabase.co/auth/v1/callback
     ```
5. Copie o **Client ID** e **Client Secret**

### 3.2 Supabase Dashboard

1. Vá em **Authentication → Providers → Google**
2. Ative o toggle
3. Cole o **Client ID** e **Client Secret** do passo anterior
4. Clique em **Save**

---

## 4. Configurar variáveis de ambiente

1. No dashboard, vá em **Settings → API**
2. Copie:
   - **Project URL** → `NEXT_PUBLIC_SUPABASE_URL`
   - **anon public** → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
3. Cole em `web/.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 5. Configurar URL de redirecionamento

1. No dashboard, vá em **Authentication → URL Configuration**
2. **Site URL**: `http://localhost:3001` (dev) ou seu domínio em produção
3. **Redirect URLs**: adicione:
   ```
   http://localhost:3001/auth/callback
   https://seu-dominio.com/auth/callback
   ```

---

## 6. Row Level Security (RLS)

O schema já configura RLS automaticamente. Verifique em **Authentication → Policies** que existem políticas para:

| Tabela        | Política                  |
|---------------|---------------------------|
| profiles      | select own, update own    |
| generations   | select own, insert own, delete own |
| subscriptions | select own                |

---

## 7. Testar

```bash
cd web && npm run dev
```

Acesse `http://localhost:3001` → deve redirecionar para `/login` → clique em **Continuar com Google** → autentica → volta para `/`

Verifique em **Table Editor → profiles** que o registro foi criado automaticamente pelo trigger.

---

## Estrutura criada no código

```
web/src/
├── middleware.ts                   # Protege rotas, redireciona para /login
├── app/
│   ├── login/page.tsx              # Página de login (botão Google)
│   ├── auth/callback/route.ts      # Troca code OAuth por sessão
│   └── auth/signout/route.ts       # POST → logout
└── lib/supabase/
    ├── client.ts                   # createClient() — Client Components
    ├── server.ts                   # createClient() — Server Components
    ├── types.ts                    # Tipos TypeScript das tabelas
    ├── useUser.ts                  # Hook { user, loading }
    └── generations.ts              # saveGeneration(), fetchHistory()
```
