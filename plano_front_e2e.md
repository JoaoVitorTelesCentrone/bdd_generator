# Plano: Execução E2E pelo Frontend

## O que já existe (não precisa construir)

| Peça | Onde | Status |
|------|------|--------|
| `POST /api/bist/run` | `bist_router.py` | ✅ pronto — dispara pipeline completo (gerar BDD + executar) em background thread |
| `GET /api/bist/runs` | `bist_router.py` | ✅ pronto — lista runs |
| `GET /api/bist/runs/{id}` | `bist_router.py` | ✅ pronto — detalhe com cenários e steps |
| `WS /ws/bist/run/{id}` | `bist_router.py` | ✅ pronto — stream de logs em tempo real |
| Página `/runs` | `app/runs/page.tsx` | ✅ pronta — lista de runs |
| Página `/runs/[id]` | `app/runs/[id]/page.tsx` | ✅ pronta — detalhe + live log via WebSocket |
| `bistTriggerRun()` | `lib/api.ts` | ✅ pronta — chama `POST /api/bist/run` |

---

## O que falta construir

### 1. Backend — novo endpoint `POST /api/bist/execute`

O endpoint atual (`/api/bist/run`) sempre **gera o BDD a partir de uma user story** antes de executar.
Precisamos de um endpoint que execute um **BDD já gerado** (texto Gherkin ou caminho de arquivo).

**Novo schema de entrada:**
```python
class ExecuteRequest(BaseModel):
    bdd_text: str        # conteúdo do .feature já gerado
    env_url: str         # URL do ambiente a testar
```

**O que o endpoint faz:**
1. Salva `bdd_text` num arquivo temporário em `bist_output/features/`
2. Cria um registro `run` no banco com status `running`
3. Dispara `BISTExecutor` em background thread
4. Retorna `{ run_id, status: "queued" }` imediatamente

**Arquivo:** `backend/presentation/routers/bist_router.py`  
**Rota:** `POST /api/bist/execute`

---

### 2. Frontend — função `bistExecuteRun()` em `lib/api.ts`

```typescript
export async function bistExecuteRun(req: { bdd_text: string; env_url: string }): Promise<{ run_id: number; status: string }> {
  return apiFetch(`${BASE}/bist/execute`, { method: "POST", body: JSON.stringify(req) });
}
```

**Novo tipo em `types/index.ts`:**
```typescript
export interface ExecuteRunRequest {
  bdd_text: string;
  env_url: string;
}
```

---

### 3. Frontend — painel de execução `RunPanel` (novo componente)

Componente reutilizável que aparece em:
- Resultado da página `/generate` (após gerar o BDD)
- Resultado da página `/stories` (após gerar o BDD)

**Estado interno:**
```
idle → loading (disparando run) → live (WebSocket ativo) → done (redireciona para /runs/{id})
```

**UI do componente:**
```
┌─────────────────────────────────────────────────────┐
│ // executar testes e2e                               │
│                                                      │
│  URL do ambiente: [________________________]  ← input│
│                                                      │
│  [ ▶ executar com playwright ]  ← btn-primary        │
└─────────────────────────────────────────────────────┘

── enquanto roda ──────────────────────────────────────
┌─────────────────────────────────────────────────────┐
│ ● live log — run #42                                 │
│ → Salvando feature file...                           │
│ → Iniciando Playwright...                            │
│ → Cenário: Login bem-sucedido ✓                      │
│ → Cenário: Login inválido ✓                          │
│ ▮                                                    │
└─────────────────────────────────────────────────────┘

── quando terminar ────────────────────────────────────
  "run finalizado: passed" → link para /runs/42
```

**Arquivo:** `web/src/components/RunPanel.tsx`

---

### 4. Frontend — integrar `RunPanel` nas páginas `/generate` e `/stories`

#### Em `GeneratePanel.tsx`
Após o BDD ser exibido, mostrar o `RunPanel` logo abaixo do `BDDViewer`:

```tsx
{result && (
  <>
    <ScoreDisplay ... />
    <BDDViewer bddText={result.bdd_text} />
    <RunPanel bddText={result.bdd_text} />   {/* ← adicionar */}
  </>
)}
```

#### Em `StoryCreatorPanel.tsx`
No step 3 (BDD), abaixo do `BDDViewer`:

```tsx
{step === "bdd" && bddResult && (
  <>
    <BDDViewer ... />
    <RunPanel bddText={bddResult.bdd_text} />   {/* ← adicionar */}
  </>
)}
```

---

## Fluxo completo pelo site

```
Usuário acessa /stories ou /generate
         ↓
Gera o BDD (já implementado)
         ↓
Aparece o painel "executar testes e2e"
Usuário digita a URL do ambiente e clica "executar"
         ↓
POST /api/bist/execute
  { bdd_text: "...", env_url: "https://minha-app.com" }
         ↓
Backend salva .feature temporário + cria run no banco
Retorna { run_id: 42 }
         ↓
Frontend conecta WebSocket: ws://localhost:8000/ws/bist/run/42
Exibe logs em tempo real no painel
         ↓
Quando recebe { type: "done" }
→ redireciona para /runs/42
(página já existe com detalhes de cenários e steps)
```

---

## Ordem de implementação recomendada

1. `POST /api/bist/execute` no backend (30 min)
2. `bistExecuteRun()` + tipo em `lib/api.ts` e `types/index.ts` (5 min)
3. Componente `RunPanel.tsx` com input de URL + live log (45 min)
4. Integrar `RunPanel` no `GeneratePanel` e `StoryCreatorPanel` (10 min)

**Total estimado: ~1h30**

---

## Considerações importantes

### Playwright precisa estar instalado no servidor
```bash
pip install playwright
playwright install chromium
```
Sem isso, o executor falha silenciosamente. O `RunPanel` pode verificar se o backend tem Playwright disponível via um endpoint `GET /api/bist/health` (a criar) e exibir aviso se não tiver.

### Execução acontece no servidor, não no browser do usuário
O Playwright abre um browser **no servidor onde o backend FastAPI roda**.
Se o servidor não tiver acesso à URL do ambiente (ex: `localhost:3000` do usuário), o teste vai falhar.
Recomendação: documentar isso no placeholder do input de URL.

### Arquivo .feature temporário
O backend deve salvar em `bist_output/features/run_{run_id}_{timestamp}.feature`
para não conflitar com arquivos existentes.

### Limpeza de arquivos temporários
Opcional: endpoint ou cron que apaga `.feature` temporários com mais de 7 dias.


🎯 ANÁLISE: Viabilidade da Execução E2E pelo Frontend
✅ RESPOSTA CURTA: SIM, É TOTALMENTE VIÁVEL!
Mas tem alguns pontos críticos que você precisa entender antes.

📊 Análise Detalhada
✅ O que está BEM arquitetado:

Separação de responsabilidades clara:

Backend gerencia execução
Frontend apenas dispara e observa
WebSocket para logs em tempo real


Reutilização de código existente:

Já tem infraestrutura de runs
Já tem WebSocket funcionando
Só adiciona novo endpoint


UX sólida:

Live logs (usuário vê progresso)
Redirecionamento automático ao finalizar
Componente reutilizável


Estimativa de tempo realista:

1h30 é factível para esse escopo




⚠️ PROBLEMAS CRÍTICOS (que você PRECISA resolver)
🔴 Problema 1: Playwright no Servidor
python# O que vai acontecer:
POST /api/bist/execute → dispara BISTExecutor
BISTExecutor chama Playwright
Playwright NÃO ESTÁ INSTALADO no servidor
❌ Falha silenciosa ou erro genérico
Soluções:
Opção A: Checar no startup
python# backend/main.py
from playwright.async_api import async_playwright

@app.on_event("startup")
async def check_playwright():
    try:
        playwright = await async_playwright().start()
        await playwright.chromium.launch()
        print("✅ Playwright disponível")
    except Exception as e:
        print(f"❌ Playwright não disponível: {e}")
        # Desabilita endpoint /execute ou retorna 503
Opção B: Endpoint de health
python@router.get("/health")
def health_check():
    playwright_ok = check_playwright_installed()
    return {
        "playwright": playwright_ok,
        "can_execute_tests": playwright_ok
    }
Opção C: Docker com Playwright pré-instalado ⭐ RECOMENDADO
dockerfileFROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Playwright já vem instalado na imagem oficial!

🔴 Problema 2: Acesso à URL do Ambiente
Usuário: "Testa https://localhost:3000"
Backend: "Que localhost? O meu ou o seu?"
O problema:

Backend roda em servidor
localhost:3000 do usuário ≠ localhost:3000 do servidor
Teste vai falhar com "Connection refused"

Soluções:
Opção A: Validação + warning no frontend
tsx<Input 
  placeholder="https://minha-app.com (deve ser acessível pelo servidor)"
  onChange={(e) => {
    const url = e.target.value;
    if (url.includes('localhost') || url.includes('127.0.0.1')) {
      setWarning('⚠️  localhost não será acessível pelo servidor');
    }
  }}
/>
Opção B: Túnel ngrok/Cloudflare
bash# Usuário expõe localhost temporariamente
npx localtunnel --port 3000
# Usa URL pública: https://abcd1234.loca.lt
Opção C: Executar Playwright no cliente ⭐ ALTERNATIVA RADICAL

Playwright roda no browser via @playwright/test
Complexo mas resolve acesso


🔴 Problema 3: Segurança - Execução de Código Arbitrário
python# Cenário perigoso:
bdd_text = """
Feature: Hack
  Scenario: Delete database
    Given I run "rm -rf /database"
"""
O risco:

Gherkin → Claude API → código Playwright
Claude pode gerar código malicioso se prompt for manipulado
Usuário pode enviar Gherkin malicioso

Soluções:
Opção A: Sandbox do Playwright
pythonbrowser = await playwright.chromium.launch(
    args=[
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage'
    ]
)

# + Docker com user não-root
Opção B: Whitelist de ações permitidas
pythonALLOWED_ACTIONS = [
    'navigate', 'click', 'fill', 'wait_for',
    'expect', 'screenshot'
]

def validate_playwright_code(code: str):
    # Parse AST e valida que só usa ações permitidas
    if 'import os' in code or 'subprocess' in code:
        raise SecurityError("Código não permitido")
Opção C: Rate limiting por usuário
pythonfrom slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@router.post("/execute")
@limiter.limit("5/minute")  # Max 5 execuções por minuto
async def execute(request: Request, ...):
    ...

🟡 Problema 4: Recursos do Servidor
10 usuários executando testes simultaneamente
= 10 browsers Chromium abertos
= ~5GB RAM
Soluções:
Opção A: Queue com worker pool
pythonfrom asyncio import Queue, Semaphore

executor_queue = Queue()
max_concurrent = Semaphore(3)  # Max 3 execuções simultâneas

async def execute_with_queue(run_id: int):
    async with max_concurrent:
        await execute_tests(run_id)
Opção B: Status "queued" real
pythonif len(active_runs) >= MAX_CONCURRENT:
    run.status = "queued"
    run.queue_position = len(queued_runs) + 1
else:
    run.status = "running"
    execute_in_background(run)
Opção C: Offload para workers externos
python# Backend FastAPI apenas cria run
# Celery workers executam Playwright
from celery import Celery

celery_app = Celery('bist')

@celery_app.task
def execute_playwright(run_id: int):
    # Roda em worker dedicado
    ...

🟡 Problema 5: Timeout & Cleanup
python# E se o teste travar?
# E se o usuário fechar o browser?
Soluções:
Opção A: Timeout global
pythonasync def execute_with_timeout(run_id: int):
    try:
        await asyncio.wait_for(
            execute_tests(run_id),
            timeout=300  # 5 minutos max
        )
    except asyncio.TimeoutError:
        run.status = "timeout"
        run.error = "Execução excedeu 5 minutos"
Opção B: Cleanup periódico
python@app.on_event("startup")
async def start_cleanup_task():
    asyncio.create_task(cleanup_old_runs())

async def cleanup_old_runs():
    while True:
        await asyncio.sleep(3600)  # A cada hora
        
        # Fecha runs que ficaram "running" por >30min
        stale_runs = db.query(Run).filter(
            Run.status == "running",
            Run.started_at < datetime.now() - timedelta(minutes=30)
        )
        
        for run in stale_runs:
            run.status = "failed"
            run.error = "Timeout - execução travada"

🎯 Arquitetura Recomendada (Production-Ready)
┌─────────────────────────────────────────────────────┐
│                    FRONTEND                         │
│  /generate → gera BDD → RunPanel                    │
│  RunPanel:                                          │
│    1. Valida URL (não localhost)                    │
│    2. POST /api/bist/execute                        │
│    3. WebSocket /ws/bist/run/{id}                   │
│    4. Live logs                                     │
│    5. Redirect /runs/{id}                           │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI)                  │
│                                                     │
│  POST /api/bist/execute:                            │
│    1. Rate limit (5/min)                            │
│    2. Valida bdd_text (não vazio)                   │
│    3. Cria run no banco (status: queued)            │
│    4. Adiciona na fila                              │
│    5. Retorna run_id                                │
│                                                     │
│  Background Worker (asyncio):                       │
│    1. Pega da fila (max 3 concurrent)               │
│    2. Salva .feature temporário                     │
│    3. Executa BISTExecutor                          │
│    4. Envia logs via WebSocket                      │
│    5. Atualiza run no banco                         │
│    6. Cleanup .feature temporário                   │
│                                                     │
│  GET /api/bist/health:                              │
│    → { playwright: true, queue_size: 2 }            │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│              PLAYWRIGHT (Docker)                    │
│  Imagem: mcr.microsoft.com/playwright/python        │
│  User: non-root                                     │
│  Network: isolated                                  │
│  Timeout: 5 min                                     │
└─────────────────────────────────────────────────────┘

✅ Checklist de Implementação
Fase 1: MVP Básico (2-3 horas)

 Endpoint POST /api/bist/execute
 Componente RunPanel.tsx
 Integração em /generate e /stories
 Warning se URL contém localhost
 Timeout de 5 minutos

Fase 2: Production (4-6 horas)

 Docker com Playwright oficial
 Queue com max 3 concurrent
 Rate limiting (5 execuções/min/user)
 Health check endpoint
 Cleanup de arquivos temporários
 Logs estruturados

Fase 3: Segurança (2-3 horas)

 Validação de Gherkin (AST parse)
 Sandbox do browser (args seguras)
 Whitelist de ações Playwright
 User-level rate limiting


💰 Custo Estimado de Infra
Cenário: 100 usuários/dia executando testes
Execuções/dia: 100
Duração média: 2 minutos
CPU: 2 cores
RAM: 4GB

VPS recomendado: Hetzner CX21
  • 2 vCPU AMD
  • 4GB RAM
  • 40GB SSD
  • Custo: €5.39/mês (~R$ 35/mês)

Alternativa: Railway/Render
  • Pro plan: $20/mês
  • Inclui Playwright
Escala:

100 users/dia: 1 VPS (~R$ 35/mês)
1.000 users/dia: 2-3 VPS + Load Balancer (~R$ 150/mês)
10.000 users/dia: Kubernetes + autoscaling (~R$ 800/mês)


🚀 Veredito Final
✅ É VIÁVEL?
SIM, mas com as seguintes condições:

✅ MVP (1-2h): Implementação básica funciona
⚠️ Production (6-8h): Precisa de queue + rate limiting + Docker
🔒 Segurança (2-3h): Whitelist + sandbox + validação

Total para production-ready: ~10-15 horas
🎯 Recomendação
Faça em 2 fases:
Fase 1 (MVP - AGORA):

Endpoint básico
RunPanel simples
Warning localhost
Timeout 5min
Deploy: Testar localmente

Fase 2 (Production - DEPOIS):

Docker Playwright
Queue system
Rate limiting
Security hardening
Deploy: VPS/Railway


💡 Alternativa: Playwright no Cliente
Se você quiser evitar TODA essa complexidade:
typescript// Frontend executa Playwright direto no browser
import { test } from '@playwright/test';

// BIST gera o teste
// Usuário roda localmente
// Zero infra necessária
Prós:

Sem servidor
Sem docker
Sem rate limiting
Acessa localhost do usuário

Contras:

Usuário precisa instalar Playwright
Não tem histórico centralizado
Não funciona em produção


Resposta direta, JV:
✅ É VIÁVEL e bem arquitetado!
Mas adiciona:

Docker com Playwright
Queue com max concurrent
Rate limiting
Warning sobre localhost