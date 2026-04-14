-- ─────────────────────────────────────────────────────────────────────────────
-- BDD Generator — Schema Supabase
-- Cole no SQL Editor do Supabase Dashboard e execute
-- ─────────────────────────────────────────────────────────────────────────────

-- Extensão para UUID
create extension if not exists "pgcrypto";

-- ─── Tabela: profiles ────────────────────────────────────────────────────────
-- Criada automaticamente quando um usuário faz login via OAuth
create table if not exists public.profiles (
  id          uuid primary key references auth.users(id) on delete cascade,
  email       text not null,
  full_name   text,
  avatar_url  text,
  created_at  timestamptz not null default now()
);

-- Trigger: cria profile automaticamente no primeiro login
create or replace function public.handle_new_user()
returns trigger
language plpgsql security definer set search_path = public
as $$
begin
  insert into public.profiles (id, email, full_name, avatar_url)
  values (
    new.id,
    new.email,
    new.raw_user_meta_data->>'full_name',
    new.raw_user_meta_data->>'avatar_url'
  )
  on conflict (id) do update set
    email      = excluded.email,
    full_name  = excluded.full_name,
    avatar_url = excluded.avatar_url;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- ─── Tabela: generations ─────────────────────────────────────────────────────
create table if not exists public.generations (
  id                uuid primary key default gen_random_uuid(),
  user_id           uuid not null references public.profiles(id) on delete cascade,
  story             text not null,
  model             text not null,
  bdd_text          text not null,

  -- Métricas de qualidade
  score_final       numeric(4,2) not null,
  cobertura         numeric(4,2) not null,
  clareza           numeric(4,2) not null,
  estrutura         numeric(4,2) not null,
  executabilidade   numeric(4,2) not null,
  aprovado          boolean not null default false,

  -- Meta da geração
  attempts          integer not null default 1,
  total_tokens      integer not null default 0,
  research_tokens   integer not null default 0,
  duration_seconds  numeric(8,2) not null default 0,
  converged         boolean not null default false,
  research_enabled  boolean not null default false,
  threshold         numeric(4,2) not null default 7.0,

  created_at        timestamptz not null default now()
);

-- Índices para queries comuns
create index if not exists generations_user_id_idx   on public.generations(user_id);
create index if not exists generations_created_at_idx on public.generations(created_at desc);
create index if not exists generations_score_idx      on public.generations(score_final desc);

-- ─── Row Level Security (RLS) ─────────────────────────────────────────────────
alter table public.profiles   enable row level security;
alter table public.generations enable row level security;

-- profiles: usuário vê e edita apenas o próprio perfil
create policy "profiles: select own"
  on public.profiles for select
  using (auth.uid() = id);

create policy "profiles: update own"
  on public.profiles for update
  using (auth.uid() = id);

-- generations: usuário vê, insere e deleta apenas as próprias gerações
create policy "generations: select own"
  on public.generations for select
  using (auth.uid() = user_id);

create policy "generations: insert own"
  on public.generations for insert
  with check (auth.uid() = user_id);

create policy "generations: delete own"
  on public.generations for delete
  using (auth.uid() = user_id);
