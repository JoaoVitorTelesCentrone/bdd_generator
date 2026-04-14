# Guia de Configuração — Stripe

## 1. Criar conta e projeto

1. Acesse [dashboard.stripe.com](https://dashboard.stripe.com)
2. Crie sua conta (use **modo Test** para desenvolvimento)
3. Confirme o e-mail

---

## 2. Criar o produto e preço

1. Vá em **Products → Add product**
2. Preencha:
   - **Name**: BDD Generator Pro
   - **Description**: Gerações ilimitadas, todos os modelos, auto-research
3. Em **Pricing**:
   - **Pricing model**: Standard pricing
   - **Price**: R$ 29,00 / month (ou o valor que quiser)
   - **Currency**: BRL
   - **Billing period**: Monthly
4. Clique em **Save product**
5. Copie o **Price ID** (começa com `price_`) → vai para `NEXT_PUBLIC_STRIPE_PRICE_PRO`

---

## 3. Obter as chaves de API

1. Vá em **Developers → API keys**
2. Copie:
   - **Publishable key** (`pk_test_...`) → `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`
   - **Secret key** (`sk_test_...`) → `STRIPE_SECRET_KEY`

---

## 4. Configurar Webhook

### 4.1 Em desenvolvimento (com Stripe CLI)

```bash
# Instalar Stripe CLI
# Windows: https://github.com/stripe/stripe-cli/releases

stripe login
stripe listen --forward-to localhost:3001/api/webhooks/stripe
```

O CLI vai imprimir o **webhook signing secret** (`whsec_...`) → cole em `STRIPE_WEBHOOK_SECRET`

### 4.2 Em produção

1. Vá em **Developers → Webhooks → Add endpoint**
2. **Endpoint URL**: `https://seu-dominio.com/api/webhooks/stripe`
3. **Events to send** — selecione:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_failed`
4. Clique em **Add endpoint**
5. Abra o endpoint criado → copie o **Signing secret** → `STRIPE_WEBHOOK_SECRET`

---

## 5. Configurar variáveis de ambiente

Cole em `web/.env.local`:

```env
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_COLOQUE_AQUI
STRIPE_SECRET_KEY=sk_test_COLOQUE_AQUI
STRIPE_WEBHOOK_SECRET=whsec_COLOQUE_AQUI
NEXT_PUBLIC_STRIPE_PRICE_PRO=price_COLOQUE_AQUI
```

---

## 6. Configurar Billing Portal (portal do cliente)

1. Vá em **Settings → Billing → Customer portal**
2. Ative o toggle **Allow customers to manage their subscriptions**
3. Marque: cancelar assinatura, atualizar método de pagamento
4. Clique em **Save**

---

## 7. Executar o schema SQL

No Supabase **SQL Editor**, execute `supabase/stripe_schema.sql` (caso ainda não tenha feito).

Isso cria a tabela `subscriptions` com:
- `stripe_customer_id`
- `stripe_subscription_id`
- `plan_id` (`free` | `pro`)
- `status` (`free` | `active` | `past_due` | `cancelled`)
- Trigger que cria entrada `free` automaticamente no primeiro login

---

## 8. Testar o fluxo completo

```bash
# Terminal 1 — Stripe webhook (dev)
stripe listen --forward-to localhost:3001/api/webhooks/stripe

# Terminal 2 — Next.js
cd web && npm run dev
```

1. Faça login com Google
2. Chame `redirectToCheckout(PLANS.pro.priceId)` de qualquer componente
3. Use o cartão de teste: `4242 4242 4242 4242`, qualquer data futura, qualquer CVC
4. Verifique em **Table Editor → subscriptions** que `plan_id` mudou para `pro`
5. Para cancelar: chame `redirectToPortal()`

---

## Estrutura criada no código

```
web/src/
├── app/api/
│   ├── stripe/
│   │   ├── checkout/route.ts      # POST → cria Checkout Session, retorna { url }
│   │   └── portal/route.ts        # POST → cria Portal Session, retorna { url }
│   └── webhooks/
│       └── stripe/route.ts        # POST → processa eventos do Stripe
└── lib/stripe/
    ├── client.ts                  # getStripe() — loadStripe singleton para o browser
    ├── server.ts                  # stripe (instância Stripe SDK), constructWebhookEvent()
    ├── config.ts                  # PLANS, getPlan(), canUseModel(), canUseResearch()
    └── useSubscription.ts         # useSubscription(user), redirectToCheckout(), redirectToPortal()
```

---

## Como usar nos componentes

```tsx
import { useUser }          from "@/lib/supabase/useUser";
import { useSubscription, redirectToCheckout, redirectToPortal } from "@/lib/stripe/useSubscription";
import { PLANS, canUseResearch } from "@/lib/stripe/config";

function MyComponent() {
  const { user }           = useUser();
  const { planId, loading } = useSubscription(user);

  // Verificar se pode usar research
  const researchAllowed = canUseResearch(planId);

  // Upgrade para Pro
  function handleUpgrade() {
    redirectToCheckout(PLANS.pro.priceId!);
  }

  // Gerenciar assinatura existente
  function handleManage() {
    redirectToPortal();
  }
}
```

---

## Cartões de teste

| Número                | Resultado        |
|-----------------------|------------------|
| `4242 4242 4242 4242` | Pagamento OK     |
| `4000 0000 0000 9995` | Cartão recusado  |
| `4000 0025 0000 3155` | Requer 3D Secure |

Data de validade: qualquer data futura. CVC: qualquer 3 dígitos.
