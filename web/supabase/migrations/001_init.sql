-- ============================================================
-- BDD Generator — Schema Supabase
-- Execute no SQL Editor do painel Supabase:
--   https://supabase.com/dashboard/project/<seu-ref>/sql/new
-- ============================================================

-- ── Subscriptions ────────────────────────────────────────────
-- Mapeamento entre usuário Supabase e assinatura Stripe.
-- Criada/atualizada automaticamente pelo webhook em:
--   /api/webhooks/stripe
CREATE TABLE IF NOT EXISTS public.subscriptions (
  id                      BIGSERIAL PRIMARY KEY,
  user_id                 UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  stripe_customer_id      TEXT        NOT NULL,
  stripe_subscription_id  TEXT        NOT NULL,
  plan_id                 TEXT        NOT NULL DEFAULT 'free',  -- 'free' | 'pro'
  status                  TEXT        NOT NULL DEFAULT 'active', -- 'active' | 'inactive' | 'cancelled' | 'past_due'
  current_period_end      TIMESTAMPTZ,
  updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id)
);

ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuário vê própria subscription"
  ON public.subscriptions FOR SELECT
  USING (auth.uid() = user_id);

-- Service role pode inserir/atualizar (webhook)
CREATE POLICY "Service role gerencia subscriptions"
  ON public.subscriptions FOR ALL
  USING (true)
  WITH CHECK (true);

-- ── CLI Usage ────────────────────────────────────────────────
-- Registra consumo de tokens por geração (para quota/billing).
CREATE TABLE IF NOT EXISTS public.cli_usage (
  id           BIGSERIAL   PRIMARY KEY,
  user_id      UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  tokens_used  INTEGER     NOT NULL DEFAULT 0,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.cli_usage ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuário vê próprio uso"
  ON public.cli_usage FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Service role gerencia uso"
  ON public.cli_usage FOR ALL
  USING (true)
  WITH CHECK (true);

-- Índice para queries de uso mensal (WHERE created_at >= ...)
CREATE INDEX IF NOT EXISTS idx_cli_usage_user_created
  ON public.cli_usage (user_id, created_at DESC);

-- ── Generations ──────────────────────────────────────────────
-- Histórico de gerações BDD salvas por usuários autenticados.
CREATE TABLE IF NOT EXISTS public.generations (
  id               BIGSERIAL   PRIMARY KEY,
  user_id          UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  story            TEXT        NOT NULL,
  model            TEXT        NOT NULL,
  bdd_text         TEXT        NOT NULL,
  score            JSONB,
  attempts         INTEGER,
  total_tokens     INTEGER,
  research_tokens  INTEGER,
  converged        BOOLEAN,
  duration_seconds FLOAT,
  options          JSONB,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.generations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuário vê próprias gerações"
  ON public.generations FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Usuário insere próprias gerações"
  ON public.generations FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE INDEX IF NOT EXISTS idx_generations_user_created
  ON public.generations (user_id, created_at DESC);
