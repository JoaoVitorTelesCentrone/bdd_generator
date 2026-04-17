# BIST — Guia de Execução: Fase 1 e Fase 2

## Pré-requisitos

```bash
# Instale as dependências
pip install -r bist/requirements.txt

# Instale o browser do Playwright
playwright install chromium

# Configure sua chave da Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."   # Linux/macOS
set ANTHROPIC_API_KEY=sk-ant-...        # Windows CMD
$env:ANTHROPIC_API_KEY="sk-ant-..."     # Windows PowerShell
```

> **Todos os comandos abaixo devem ser executados a partir da raiz do projeto** (`BDD-GENERATOR/`).

---

## Fase 1 — CLI Core

### 1. Gerar cenários BDD a partir de uma user story

```bash
# Texto direto
python -m bist.bist generate \
  --user-story "Como usuário quero fazer login com email e senha" \
  --output bist_output/features/login.feature

# A partir de um arquivo .md
python -m bist.bist generate \
  --user-story stories/login.md \
  --output bist_output/features/login.feature \
  --model sonnet \
  --threshold 7.5 \
  --verbose
```

| Flag | Padrão | Descrição |
|------|--------|-----------|
| `--user-story` / `-s` | obrigatório | Texto da story ou caminho para .md/.txt |
| `--output` / `-o` | auto-nomeado | Caminho do .feature gerado |
| `--model` / `-m` | `sonnet` | Modelo LLM: `sonnet`, `opus`, `haiku` |
| `--threshold` / `-t` | `7.0` | Score mínimo de qualidade (0–10) |
| `--max-attempts` | `5` | Máximo de iterações de refinamento |
| `--until-converged` | — | Refina até atingir o threshold (max 50) |
| `--research` | — | Ativa pesquisa automática antes da geração |
| `--verbose` / `-v` | — | Exibe detalhes de cada iteração |

---

### 2. Executar um .feature contra um ambiente

```bash
python -m bist.bist execute \
  --feature bist_output/features/login.feature \
  --env https://staging.meuapp.com \
  --report all
```

| Flag | Padrão | Descrição |
|------|--------|-----------|
| `--feature` / `-f` | obrigatório | Caminho para o .feature |
| `--env` / `-e` | obrigatório | URL do ambiente alvo |
| `--headless` / `--headed` | `--headless` | Modo do browser |
| `--no-heal` | — | Desativa self-healing por IA |
| `--report` | `html` | Formato: `html`, `json`, `github`, `all` |
| `--output-dir` | `bist_output` | Diretório de saída |

**Saída gerada:**
```
bist_output/
├── screenshots/   # capturas de falha por step
├── videos/        # vídeo de cada cenário
└── reports/
    ├── report_YYYYMMDD_HHMMSS.html
    └── report_YYYYMMDD_HHMMSS.json
```

---

### 3. Pipeline completo: story → feature → execução

```bash
python -m bist.bist full \
  --user-story stories/checkout.md \
  --env https://staging.meuapp.com \
  --model sonnet \
  --threshold 7.0 \
  --verbose
```

---

### 4. Avaliar qualidade de um .feature existente

```bash
python -m bist.bist evaluate \
  --story "Como usuário quero fazer login" \
  --bdd bist_output/features/login.feature \
  --threshold 7.0
```

---

### 5. Ver histórico de execuções (SQLite)

```bash
python -m bist.bist stats
python -m bist.bist stats --limit 50
```

O banco fica em `~/.bist/bist.db` e é criado automaticamente na primeira execução.

---

### 6. Gerar relatório de uma execução anterior

```bash
# Relatório da última execução
python -m bist.bist report

# Execução específica por ID
python -m bist.bist report --run-id 3 --format html
python -m bist.bist report --run-id 3 --format json --output meu_relatorio.json
```

---

## Fase 2 — Features Avançadas

### 2.1 Execução paralela

Roda múltiplos cenários ao mesmo tempo usando Playwright async.

```bash
# Executa até 3 cenários em paralelo
python -m bist.bist execute \
  --feature bist_output/features/suite.feature \
  --env https://staging.meuapp.com \
  --parallel 3

# Pipeline completo com paralelismo
python -m bist.bist full \
  --user-story stories/suite.md \
  --env https://staging.meuapp.com \
  --parallel 4
```

> **Dica:** Para CI, valores entre 2 e 5 costumam ser o sweet spot.  
> Acima de 5 pode causar throttling dependendo do ambiente alvo.

---

### 2.2 Visual Regression Testing

**Passo 1 — Capturar baselines (primeira vez)**

```bash
python -m bist.bist baseline \
  --feature bist_output/features/login.feature \
  --env https://staging.meuapp.com
```

Salva screenshots em `bist_output/baselines/`.  
**Execute este comando sempre que o design mudar intencionalmente.**

**Passo 2 — Comparar contra os baselines**

```bash
# Threshold padrão: 1% de pixels diferentes
python -m bist.bist visual-diff \
  --feature bist_output/features/login.feature \
  --env https://staging.meuapp.com

# Threshold mais tolerante (5%)
python -m bist.bist visual-diff \
  --feature bist_output/features/login.feature \
  --env https://staging.meuapp.com \
  --threshold 0.05
```

**Saída gerada:**
```
bist_output/
├── baselines/          # referências capturadas com `baseline`
├── visual_current/     # screenshots da execução atual
└── visual_diffs/       # imagens de diff (pixels alterados em destaque)
```

O comando retorna exit code `1` se qualquer cenário exceder o threshold, permitindo uso em CI:

```yaml
# GitHub Actions
- run: |
    python -m bist.bist visual-diff \
      --feature tests/critical.feature \
      --env ${{ secrets.STAGING_URL }}
```

---

### 2.3 Self-healing com cache de seletores

O self-healing já está ativo por padrão (`--no-heal` para desativar).

Na Fase 2 o executor passou a **cachear seletores bem-sucedidos** no SQLite.  
Em execuções futuras, seletores do cache são testados **antes** de chamar a API Claude — reduzindo latência e custo.

O audit trail de cada cura fica na tabela `healing_log`. Para consultá-lo:

```bash
sqlite3 ~/.bist/bist.db \
  "SELECT step_text, failed_selector, healed_selector, datetime(timestamp,'unixepoch','localtime') FROM healing_log ORDER BY timestamp DESC LIMIT 20;"
```

---

### 2.4 Retry com backoff exponencial

Configure no `.bist.yml` na raiz do projeto (copie de `bist/.bist.yml.example`):

```yaml
retry:
  max_attempts: 3
  backoff_seconds: [2, 5, 10]
  on: [selector_timeout, network_error]
```

| Campo | Descrição |
|-------|-----------|
| `max_attempts` | Quantas vezes cada step pode ser reexecutado |
| `backoff_seconds` | Intervalo entre tentativas (índice = número da tentativa) |

Sem `.bist.yml`, o comportamento padrão é 1 tentativa sem espera.

---

### 2.5 Notificações Slack / Discord

Defina as webhooks como variáveis de ambiente:

```bash
export BIST_SLACK_WEBHOOK="https://hooks.slack.com/services/XXX/YYY/ZZZ"
export BIST_DISCORD_WEBHOOK="https://discord.com/api/webhooks/XXX/YYY"
```

Quando definidas, o BIST envia automaticamente um resumo ao final de `execute` e `full`:

```
✅ BIST Run PASSED — https://staging.meuapp.com
Scenarios: 4 | Passed: 4 | Failed: 0 | Pass Rate: 100% | Duration: 12,340ms
```

Para desativar pontualmente, basta não setar as variáveis.

---

## Configuração via .bist.yml

Crie um `.bist.yml` na raiz do projeto para persistir configurações:

```bash
cp bist/.bist.yml.example .bist.yml
```

```yaml
model: sonnet
threshold: 7.5
max_attempts: 5

executor:
  headless: true
  timeout_ms: 15000
  self_heal: true
  screenshots_dir: bist_output/screenshots
  videos_dir: bist_output/videos

reports:
  output_dir: bist_output/reports
  formats: [html, json]

retry:
  max_attempts: 3
  backoff_seconds: [2, 5, 10]
  on: [selector_timeout, network_error]

visual:
  baselines_dir: bist_output/baselines
  diffs_dir: bist_output/visual_diffs
  threshold: 0.01

parallel: 2

notifications:
  # slack_webhook: https://hooks.slack.com/services/...
  # discord_webhook: https://discord.com/api/webhooks/...
```

---

## Exemplo completo: do zero ao relatório

```bash
# 1. Instalar
pip install -r bist/requirements.txt
playwright install chromium

# 2. Configurar API key
export ANTHROPIC_API_KEY="sk-ant-..."

# 3. Gerar e executar
python -m bist.bist full \
  --user-story "Como usuário quero fazer login com email e senha e ver o dashboard" \
  --env https://demo.playwright.dev/todomvc \
  --model sonnet \
  --threshold 7.0 \
  --parallel 2 \
  --verbose

# 4. Capturar baselines para visual regression
python -m bist.bist baseline \
  --feature bist_output/features/*.feature \
  --env https://demo.playwright.dev/todomvc

# 5. Rodar visual diff após um deploy
python -m bist.bist visual-diff \
  --feature bist_output/features/*.feature \
  --env https://demo.playwright.dev/todomvc \
  --threshold 0.02

# 6. Ver histórico
python -m bist.bist stats

# 7. Abrir relatório HTML
start bist_output/reports/report_*.html    # Windows
open  bist_output/reports/report_*.html    # macOS
```

---

## Referência rápida de comandos

| Comando | Fase | O que faz |
|---------|------|-----------|
| `bist generate` | 1 | Gera .feature a partir de user story |
| `bist execute` | 1 | Executa .feature com Playwright |
| `bist full` | 1 | Pipeline completo (generate + execute) |
| `bist evaluate` | 1 | Avalia qualidade de BDD existente |
| `bist stats` | 1 | Histórico de execuções (SQLite) |
| `bist report` | 1 | Gera relatório HTML/JSON de execução passada |
| `bist execute --parallel N` | 2 | Execução paralela de cenários |
| `bist full --parallel N` | 2 | Pipeline completo com paralelismo |
| `bist baseline` | 2 | Captura screenshots de referência |
| `bist visual-diff` | 2 | Compara screenshots com baselines |

---

## Fase 4 — SaaS / Multi-tenancy

### Pré-requisitos adicionais

```bash
pip install stripe python3-saml httpx
```

### Variáveis de ambiente (Fase 4)

```bash
# Proteção das rotas de admin
export BIST_ADMIN_KEY="minha-chave-secreta"

# Stripe (billing)
export STRIPE_SECRET_KEY="sk_live_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."
export STRIPE_PRICE_PRO="price_XXXX"        # ID do price Pro no Stripe
export STRIPE_PRICE_BUSINESS="price_YYYY"   # ID do price Business no Stripe

# OAuth2 (padrão Google — substitua para outro IdP)
export OAUTH2_CLIENT_ID="..."
export OAUTH2_CLIENT_SECRET="..."
export OAUTH2_REDIRECT_URI="http://localhost:8000/api/sso/oauth2/callback"
# Opcional: sobrescreva as URLs para IdPs não-Google
# export OAUTH2_AUTHORIZE_URL="https://..."
# export OAUTH2_TOKEN_URL="https://..."
# export OAUTH2_USERINFO_URL="https://..."

# SAML (enterprise)
export SAML_ACS_URL_BASE="https://meuapp.com/api/sso/saml"
```

---

### 4.1 Gerenciamento de Tenants

Todos os endpoints de admin exigem o header `X-Admin-Key: <BIST_ADMIN_KEY>`.

**Criar tenant:**

```bash
curl -X POST http://localhost:8000/api/tenants \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: minha-chave-secreta" \
  -d '{"name": "Acme Corp", "tier": "pro"}'
# → {"id": 1, "name": "Acme Corp", "tier": "pro"}
```

**Listar tenants:**

```bash
curl http://localhost:8000/api/tenants \
  -H "X-Admin-Key: minha-chave-secreta"
```

**Mudar tier:**

```bash
curl -X PATCH http://localhost:8000/api/tenants/1/tier \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: minha-chave-secreta" \
  -d '{"tier": "business"}'
```

Tiers disponíveis:

| Tier | Runs/mês | Chamadas API/mês |
|------|----------|-----------------|
| `free` | 50 | 500 |
| `pro` | 1 000 | 10 000 |
| `business` | ilimitado | ilimitado |

---

### 4.2 API Keys

**Criar chave (mostrada apenas uma vez):**

```bash
curl -X POST http://localhost:8000/api/tenants/1/api-keys \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: minha-chave-secreta" \
  -d '{"label": "CI pipeline"}'
# → {"raw_key": "bist_...", "key_prefix": "bist_Xk9p...", "label": "CI pipeline"}
```

**Listar chaves do tenant:**

```bash
curl http://localhost:8000/api/tenants/1/api-keys \
  -H "X-Admin-Key: minha-chave-secreta"
```

**Revogar chave:**

```bash
curl -X DELETE http://localhost:8000/api/tenants/1/api-keys/bist_Xk9p \
  -H "X-Admin-Key: minha-chave-secreta"
```

**Usar a chave nas chamadas BIST:**

Passe o header `X-Api-Key` em qualquer rota `/api/bist/*`. O backend valida o tenant, verifica o limite do tier e registra o uso automaticamente.

```bash
# Disparar um run autenticado
curl -X POST http://localhost:8000/api/bist/run \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: bist_..." \
  -d '{
    "user_story": "Como usuário quero fazer login",
    "env_url": "https://staging.meuapp.com"
  }'

# Listar runs do tenant
curl http://localhost:8000/api/bist/runs \
  -H "X-Api-Key: bist_..."

# Stats isolados por tenant
curl http://localhost:8000/api/bist/stats \
  -H "X-Api-Key: bist_..."
```

Se o tenant atingir o limite do tier, a API retorna `402 Payment Required`.

---

### 4.3 Uso e Consumo

```bash
# Ver consumo dos últimos 30 dias do tenant 1
curl http://localhost:8000/api/tenants/1/usage

# Período customizado (últimos 7 dias)
curl "http://localhost:8000/api/tenants/1/usage?days=7"
```

Resposta:

```json
{
  "tenant_id": 1,
  "period_days": 30,
  "runs": 23,
  "api_calls": 0
}
```

---

### 4.4 Billing — Stripe Webhook

No Stripe Dashboard, configure o webhook apontando para:

```
POST https://meuapp.com/api/billing/webhook
```

Eventos tratados automaticamente:
- `customer.subscription.created` → atualiza tier do tenant
- `customer.subscription.updated` → atualiza tier do tenant
- `customer.subscription.deleted` → downgrade para `free`

O endpoint verifica a assinatura do Stripe via `STRIPE_WEBHOOK_SECRET`. Payloads sem assinatura válida retornam `400`.

Para testar localmente com Stripe CLI:

```bash
stripe listen --forward-to localhost:8000/api/billing/webhook
stripe trigger customer.subscription.created
```

---

### 4.5 SSO — OAuth2 (Google / qualquer IdP)

**Fluxo completo:**

```
1. Redirecionar o usuário para:
   GET /api/sso/oauth2/authorize?tenant_id=1

2. O IdP redireciona de volta para o callback com ?code=...&state=...
   GET /api/sso/oauth2/callback?code=XXXX&state=YYYY

3. Resposta:
   {
     "user_info": {"email": "...", "name": "...", "sub": "..."},
     "tenant_id": 1
   }
```

Para usar outro IdP (Okta, Azure AD, etc.), sobrescreva as variáveis `OAUTH2_*`.

---

### 4.6 SSO — SAML (Enterprise)

**1. Configurar IdP do tenant:**

```bash
curl -X POST http://localhost:8000/api/sso/saml/1/configure \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: minha-chave-secreta" \
  -d '{
    "idp_entity_id":   "https://idp.empresa.com/saml",
    "idp_sso_url":     "https://idp.empresa.com/saml/sso",
    "idp_cert":        "MIIC...base64cert...==",
    "sp_entity_id":    "bist_sp_1",
    "attribute_email": "email",
    "attribute_name":  "displayName"
  }'
```

**2. Redirecionar usuário para login SAML:**

```
GET /api/sso/saml/1/login
→ redireciona para idp_sso_url
```

**3. IdP posta a resposta SAML no ACS:**

```
POST /api/sso/saml/1/acs
Body (form): SAMLResponse=<base64>
→ {"tenant_id": 1, "email": "user@empresa.com", "name": "João", "attributes": {...}}
```

Para verificação completa de assinatura SAML, instale `python3-saml` e o endpoint usará `OneLogin_Saml2_Auth` automaticamente. Sem o pacote, o parsing básico de atributos ainda funciona (adequado para IdPs confiáveis em ambiente interno).

---

### 4.7 Consulta direta ao banco (SQLite)

```bash
# Ver todos os tenants
sqlite3 ~/.bist/bist.db "SELECT * FROM tenants;"

# Ver API keys ativas por tenant
sqlite3 ~/.bist/bist.db \
  "SELECT tenant_id, key_prefix, label, datetime(created_at,'unixepoch','localtime') FROM api_keys WHERE active=1;"

# Ver consumo por tenant no mês
sqlite3 ~/.bist/bist.db \
  "SELECT tenant_id, event_type, SUM(quantity) FROM usage_events GROUP BY tenant_id, event_type;"

# Ver assinaturas Stripe
sqlite3 ~/.bist/bist.db "SELECT tenant_id, tier, status FROM stripe_subscriptions;"

# Ver runs por tenant
sqlite3 ~/.bist/bist.db \
  "SELECT tenant_id, status, COUNT(*) FROM test_runs GROUP BY tenant_id, status;"
```

---

### Migração Alembic (PostgreSQL)

Para ambientes PostgreSQL, aplique a migration da Fase 4:

```bash
cd bist
alembic upgrade 002
# ou para subir todas as fases de uma vez:
alembic upgrade head
```
