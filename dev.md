# Como rodar o projeto web

## 1. Backend (FastAPI)

```bash
# Instalar dependências (caso ainda não tenha)
pip install fastapi "uvicorn[standard]"

# Rodar o backend (na raiz do projeto)
python -m uvicorn backend.main:app --reload --port 8000
```

O backend estará em: http://localhost:8000
Docs interativas (Swagger): http://localhost:8000/docs

## 2. Frontend (Next.js)

```bash
cd web
npm install
npm run dev
```

O frontend estará em: http://localhost:3000

## Arquitetura

```
BDD-GENERATOR/
├── backend/
│   └── main.py          # FastAPI — endpoints /api/generate, /api/evaluate, /api/models
├── web/
│   └── src/
│       ├── app/
│       │   ├── page.tsx          # Página Gerar BDD
│       │   └── evaluate/
│       │       └── page.tsx      # Página Avaliar BDD
│       ├── components/
│       │   ├── GeneratePanel.tsx  # Formulário + resultados de geração
│       │   ├── EvaluatePanel.tsx  # Formulário + resultados de avaliação
│       │   ├── ScoreDisplay.tsx   # Ring chart + 4 barras de métricas
│       │   ├── BDDViewer.tsx      # Viewer com syntax highlighting
│       │   ├── MetricBar.tsx      # Barra individual de métrica
│       │   └── Navbar.tsx         # Navegação
│       └── lib/
│           └── api.ts             # fetchModels, generateBDD, evaluateBDD
└── src/                 # Módulos Python existentes (não alterados)
```

## Endpoints da API

| Método | Rota             | Descrição                        |
|--------|------------------|----------------------------------|
| GET    | /health          | Health check                     |
| GET    | /api/models      | Lista de modelos disponíveis     |
| POST   | /api/generate    | Gera BDD com auto-refinamento    |
| POST   | /api/evaluate    | Avalia BDD existente             |
