# BDD Generator com Auto-Refinamento

Gerador de cenários BDD a partir de User Stories com validação automática por métricas objetivas e loop de refinamento.

## 🎯 Objetivo

Gerar cenários BDD de alta qualidade a partir de User Stories, utilizando:
- **3 modelos Claude** (Opus 4 / Sonnet 4 / Haiku 4)
- **4 métricas objetivas** (Cobertura, Clareza, Estrutura GWT, Executabilidade)
- **Loop de auto-refinamento** até atingir threshold de qualidade

## 📊 Dataset

Utiliza o [neodataset](https://github.com/giseldo/neodataset): 40.000+ User Stories reais de projetos GitLab com Story Points.

## 🏗️ Estrutura do Projeto

```
bdd-generator/
├── src/
│   ├── cli.py                    # Interface CLI (Typer)
│   ├── generators/
│   │   ├── base.py              # Interface abstrata LLM
│   │   └── claude_generator.py  # Implementação Claude API
│   ├── evaluators/
│   │   ├── coverage.py          # Métrica 1: Cobertura
│   │   ├── clarity.py           # Métrica 2: Clareza
│   │   ├── structure.py         # Métrica 3: Estrutura GWT
│   │   ├── executability.py     # Métrica 4: Executabilidade
│   │   └── scorer.py            # Agregador de scores
│   ├── refinement/
│   │   └── loop.py              # Loop de refinamento automático
│   └── utils/
│       ├── prompts.py           # Templates de prompts
│       └── logger.py            # Logging de tentativas
├── datasets/
│   └── neodataset/              # Clone do repositório
├── results/
│   └── experiments/             # CSVs com resultados
├── tests/
│   └── test_metrics.py          # Testes das métricas
├── requirements.txt
├── setup.py
└── README.md
```

## 🚀 Instalação

```bash
# Clone o repositório
git clone <seu-repo>
cd bdd-generator

# Instale dependências
pip install -r requirements.txt

# Configure sua API key da Anthropic
export ANTHROPIC_API_KEY="sua-key-aqui"

# Clone o neodataset
cd datasets
git clone https://github.com/giseldo/neodataset.git
cd ..
```

## 💻 Uso Básico

### Gerar BDD de uma User Story

```bash
# Usando Claude Sonnet (padrão)
python -m src.cli generate --story "Como usuário, quero fazer login no sistema para acessar minha conta"

# Especificando modelo
python -m src.cli generate --story "..." --model opus

# Com threshold customizado
python -m src.cli generate --story "..." --threshold 8.0

# Verbose mode (mostra todas as tentativas)
python -m src.cli generate --story "..." --verbose
```

### Processar Dataset Completo

```bash
# Processar arquivo CSV do neodataset
python -m src.cli batch --input datasets/neodataset/csv/minds.csv --output results/minds_results.csv

# Comparar 3 modelos
python -m src.cli compare --input datasets/neodataset/csv/minds.csv --models opus,sonnet,haiku
```

### Avaliar BDD Existente

```bash
# Apenas avaliar (sem gerar)
python -m src.cli evaluate --story "..." --bdd cenarios.feature
```

## 📊 Métricas

### 1. Cobertura (0-10)
Percentual de critérios de aceitação cobertos pelos cenários.

**Exemplo:**
```
User Story: Login com 4 critérios
Cenários: Cobrem 3 critérios
Score: (3/4) * 10 = 7.5/10
```

### 2. Clareza (0-10)
Legibilidade + ausência de ambiguidade + tamanho adequado dos steps.

**Fatores:**
- Flesch Reading Ease (legibilidade)
- Tamanho dos steps (ideal: 7-15 palavras)
- Ausência de termos vagos

### 3. Estrutura GWT (0-10)
Aderência ao padrão Given-When-Then.

**Valida:**
- Presença de Given/When/Then
- Given: apenas contexto (sem ações)
- When: uma ação clara do usuário
- Then: resultado observável

### 4. Executabilidade (0-10)
Steps podem ser traduzidos em código de automação?

**Verifica:**
- Dados concretos (não "um valor qualquer")
- Seletores específicos (CSS, IDs)
- Ações mapeáveis (clicar, preencher, etc)

### Score Final

```python
score_final = (
    cobertura * 0.30 +       # 30%
    clareza * 0.20 +          # 20%
    estrutura * 0.30 +        # 30%
    executabilidade * 0.20    # 20%
)

# Threshold padrão: 7.0/10
```

## 🔄 Loop de Refinamento

Se o score inicial < threshold:
1. Sistema gera **crítica automática** baseada nas métricas
2. Envia novo prompt com feedback específico
3. Regenera BDD melhorado
4. Re-avalia métricas
5. Repete até passar (máx 5 tentativas)

## 🧪 Experimento Científico

### Variáveis Independentes
- Modelo (Opus vs Sonnet vs Haiku)
- Tamanho da User Story (pequena/média/grande)
- Presença de critérios explícitos

### Variáveis Dependentes
- Score final (0-10)
- Número de tentativas até passar
- Custo (tokens consumidos)
- Tempo de execução

### Executar Experimento

```bash
python -m src.cli experiment \
  --dataset datasets/neodataset/csv/minds.csv \
  --models opus,sonnet,haiku \
  --sample-size 100 \
  --output results/experiment_results.csv
```

## 📈 Resultados

Os resultados são salvos em CSV com as colunas:

```csv
story_id,title,description,model,score_final,cobertura,clareza,estrutura,executabilidade,tentativas,tokens_usados,tempo_segundos,aprovado
```

## 🛠️ Desenvolvimento

### Executar Testes

```bash
pytest tests/
```

### Adicionar Novo Modelo

```python
# Em src/generators/base.py
class NovoModelo(BaseLLMGenerator):
    def generate(self, prompt: str) -> str:
        # Implementação
        pass
```

## 📝 TODO

- [ ] Adicionar suporte a modelos OpenAI (GPT-4)
- [ ] Implementar Scenario Outline automático
- [ ] Parser de código (TSX/Python) além de User Stories
- [ ] Integração com Playwright para validar executabilidade
- [ ] Dashboard web para visualização de resultados
- [ ] Export para Cucumber/Behave

## 📄 Licença

MIT

## 👤 Autor

[Seu Nome] - QA Professional & Entrepreneur

## 🔗 Links

- [neodataset](https://github.com/giseldo/neodataset)
- [Documentação Claude API](https://docs.anthropic.com)