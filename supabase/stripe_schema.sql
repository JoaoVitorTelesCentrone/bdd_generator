-- ─────────────────────────────────────────────────────────────────────────────
-- Stripe — Schema de assinaturas
-- Execute APÓS o schema.sql principal
-- ─────────────────────────────────────────────────────────────────────────────

-- ─── Tabela: subscriptions ───────────────────────────────────────────────────
create table if not exists public.subscriptions (
  id                      uuid primary key default gen_random_uuid(),
  user_id                 uuid not null unique references public.profiles(id) on delete cascade,

  -- IDs do Stripe
  stripe_customer_id      text unique,
  stripe_subscription_id  text unique,

  -- Estado da assinatura
  plan_id                 text not null default 'free',  -- 'free' | 'pro'
  status                  text not null default 'free',  -- 'free' | 'active' | 'past_due' | 'cancelled'
  current_period_end      timestamptz,

  created_at              timestamptz not null default now(),
  updated_at              timestamptz not null default now()
);

-- Índices
create index if not exists subscriptions_user_id_idx             on public.subscriptions(user_id);
create index if not exists subscriptions_stripe_customer_id_idx  on public.subscriptions(stripe_customer_id);

-- ─── Trigger: cria subscription 'free' automaticamente no primeiro login ─────
create or replace function public.handle_new_subscription()
returns trigger
language plpgsql security definer set search_path = public
as $$
begin
  insert into public.subscriptions (user_id, plan_id, status)
  values (new.id, 'free', 'free')
  on conflict (user_id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_profile_created_subscription on public.profiles;
create trigger on_profile_created_subscription
  after insert on public.profiles
  for each row execute procedure public.handle_new_subscription();

-- ─── RLS ─────────────────────────────────────────────────────────────────────
alter table public.subscriptions enable row level security;

-- Usuário vê apenas a própria assinatura
create policy "subscriptions: select own"
  on public.subscriptions for select
  using (auth.uid() = user_id);

-- Apenas o service_role (webhook) pode escrever
-- O webhook usa a chave service_role via Supabase Admin Client
create policy "subscriptions: insert service_role"
  on public.subscriptions for insert
  with check (auth.uid() = user_id);

-- ─── View: user_plan (conveniência) ──────────────────────────────────────────
create or replace view public.user_plan as
  select
    p.id          as user_id,
    p.email,
    p.full_name,
    coalesce(s.plan_id, 'free')  as plan_id,
    coalesce(s.status,  'free')  as status,
    s.current_period_end,
    s.stripe_customer_id
  from public.profiles p
  left join public.subscriptions s on s.user_id = p.id;
