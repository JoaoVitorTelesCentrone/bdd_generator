-- ═══════════════════════════════════════════════════════════════════════════
-- CLI SCHEMA — api_keys + cli_usage
-- Execute no Supabase SQL Editor após schema.sql e stripe_schema.sql
-- ═══════════════════════════════════════════════════════════════════════════

-- ── api_keys ─────────────────────────────────────────────────────────────────
-- Tokens gerados pelo dashboard para uso no CLI (modo managed)

CREATE TABLE IF NOT EXISTS public.api_keys (
  id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  token       text        NOT NULL UNIQUE,  -- Bearer token enviado pelo CLI
  name        text        NOT NULL DEFAULT 'default',  -- apelido do token (ex: "laptop")
  expires_at  timestamptz,                  -- NULL = não expira
  revoked     boolean     NOT NULL DEFAULT false,
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- Índice para lookup rápido pelo token (auth hot path)
CREATE INDEX IF NOT EXISTS api_keys_token_idx ON public.api_keys (token);
CREATE INDEX IF NOT EXISTS api_keys_user_id_idx ON public.api_keys (user_id);

-- RLS
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;

-- Usuário só vê e gerencia seus próprios tokens
CREATE POLICY "api_keys: owner select"
  ON public.api_keys FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "api_keys: owner insert"
  ON public.api_keys FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "api_keys: owner update"
  ON public.api_keys FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "api_keys: owner delete"
  ON public.api_keys FOR DELETE
  USING (auth.uid() = user_id);

-- Service role (Next.js server-side) pode fazer lookup sem restrição de auth.uid()
-- Isso é necessário porque a rota /api/cli/* autentica via Bearer, não via cookie
CREATE POLICY "api_keys: service_role full access"
  ON public.api_keys FOR ALL
  USING (auth.role() = 'service_role');


-- ── cli_usage ─────────────────────────────────────────────────────────────────
-- Registro de tokens consumidos por geração (modo managed)

CREATE TABLE IF NOT EXISTS public.cli_usage (
  id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  tokens_used integer     NOT NULL CHECK (tokens_used > 0),
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- Índice composto para a query de uso mensal:
-- SELECT SUM(tokens_used) WHERE user_id = ? AND created_at >= ?
CREATE INDEX IF NOT EXISTS cli_usage_user_month_idx
  ON public.cli_usage (user_id, created_at DESC);

-- RLS
ALTER TABLE public.cli_usage ENABLE ROW LEVEL SECURITY;

CREATE POLICY "cli_usage: owner select"
  ON public.cli_usage FOR SELECT
  USING (auth.uid() = user_id);

-- Inserção só pelo service_role (via Next.js route handler trackUsage)
-- O usuário não insere diretamente
CREATE POLICY "cli_usage: service_role insert"
  ON public.cli_usage FOR INSERT
  WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "cli_usage: service_role select"
  ON public.cli_usage FOR SELECT
  USING (auth.role() = 'service_role');


-- ── Função utilitária — uso do mês atual ─────────────────────────────────────
-- Retorna (tokens_used, generations_used) para um user_id no mês corrente

CREATE OR REPLACE FUNCTION public.get_monthly_usage(p_user_id uuid)
RETURNS TABLE (tokens_used bigint, generations_used bigint)
LANGUAGE sql STABLE
SECURITY DEFINER
AS $$
  SELECT
    COALESCE(SUM(u.tokens_used), 0)::bigint AS tokens_used,
    COUNT(*)::bigint                         AS generations_used
  FROM public.cli_usage u
  WHERE u.user_id = p_user_id
    AND u.created_at >= date_trunc('month', now());
$$;
