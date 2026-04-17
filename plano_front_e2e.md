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
