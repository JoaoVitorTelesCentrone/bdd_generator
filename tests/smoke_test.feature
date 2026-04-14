# language: pt

Funcionalidade: Smoke Test — BDD Generator
  Como desenvolvedor ou pesquisador de QA
  Quero verificar que todas as funcionalidades principais do BDD Generator estão operacionais
  Para garantir que nenhuma regressão crítica foi introduzida no sistema

  # ─────────────────────────────────────────────────────────────────────────────
  # COMANDO: generate
  # ─────────────────────────────────────────────────────────────────────────────

  Contexto:
    Dado que o ambiente Python está configurado com as dependências instaladas
    E que as variáveis de ambiente GEMINI_API_KEY ou ANTHROPIC_API_KEY estão definidas

  Esquema do Cenário: Geração básica de cenários BDD por modelo
    Dado que o comando "generate" é invocado com a story "<story>"
    E o modelo "<modelo>" está selecionado
    Quando o sistema executa o loop de geração
    Então o arquivo "bdd.feature" deve ser criado na pasta de saída
    E o conteúdo deve conter pelo menos uma palavra-chave Gherkin como "Cenário" ou "Funcionalidade"
    E o score final deve ser um número entre 0.0 e 10.0

    Exemplos:
      | story                                              | modelo     |
      | Login com usuário e senha válidos                  | flash      |
      | Cadastro de novo cliente com dados obrigatórios    | flash-lite |
      | Recuperação de senha via e-mail                    | pro        |
      | Login com usuário e senha válidos                  | sonnet     |

  Cenário: Geração com threshold padrão (7.0)
    Dado que o comando "generate" é invocado com a story "Realizar checkout de pedido no e-commerce"
    E nenhum threshold é informado
    Quando o sistema executa o loop de geração
    Então o threshold utilizado deve ser "7.0"
    E o resultado deve exibir o status "APROVADO" ou "REPROVADO" conforme o score obtido

  Cenário: Geração com threshold customizado
    Dado que o comando "generate" é invocado com a story "Pesquisar produto por categoria"
    E o threshold é definido como "9.0"
    Quando o score final obtido for inferior a "9.0"
    Então o resultado deve exibir o status "REPROVADO"
    E o arquivo "bdd.feature" ainda deve ser salvo com o melhor resultado obtido

  Cenário: Geração com pasta de saída customizada
    Dado que o comando "generate" é invocado com "--output results/smoke_out"
    E a story informada é "Filtrar relatório por data de competência"
    Quando o sistema conclui a geração
    Então o arquivo "results/smoke_out/bdd.feature" deve existir no sistema de arquivos

  Cenário: Geração com flag --verbose ativa
    Dado que o comando "generate" é invocado com "--verbose"
    E a story informada é "Emitir nota fiscal eletrônica"
    Quando o sistema executa o loop de geração
    Então a saída deve exibir "Tentativa 1" antes do resultado final

  Cenário: Geração com máximo de tentativas customizado
    Dado que o comando "generate" é invocado com "--max-attempts 2"
    E a story informada é "Aprovar solicitação de reembolso"
    Quando o loop de geração for executado
    Então o número de tentativas registradas deve ser no máximo "2"

  # ─────────────────────────────────────────────────────────────────────────────
  # AUTO-RESEARCH
  # ─────────────────────────────────────────────────────────────────────────────

  Cenário: Geração com auto-research habilitado via flag --research
    Dado que o comando "generate" é invocado com "--research"
    E a story informada é "Aprovar solicitação de férias pelo gestor"
    Quando o sistema executa a fase de pesquisa antes da geração
    Então a saída deve exibir "Pesquisando user story..."
    E o campo "tokens_research" no resultado deve ser maior que zero
    E o arquivo "bdd.feature" deve ser criado com cenários cobrindo critérios de aceitação

  Cenário: Pesquisa de user story extrai critérios de aceitação, regras e edge cases
    Dado que o AutoResearcher é instanciado com um gerador válido
    E a user story "Transferência bancária entre contas do mesmo banco" é fornecida
    Quando o método "research" é chamado
    Então o resultado deve conter um contexto não vazio
    E o campo "success" deve ser "True"
    E o contexto deve conter seções como "CRITÉRIOS DE ACEITAÇÃO" ou "REGRAS DE NEGÓCIO"

  Cenário: Falha na fase de pesquisa não interrompe a geração
    Dado que o AutoResearcher está configurado com um gerador que retorna erro
    E a flag "--research" está ativa
    Quando o loop de geração é executado
    Então a geração deve continuar sem a fase de pesquisa
    E o campo "research_tokens" deve ser zero no resultado

  # ─────────────────────────────────────────────────────────────────────────────
  # UNTIL-CONVERGED
  # ─────────────────────────────────────────────────────────────────────────────

  Cenário: Geração com --until-converged respeita o teto de 50 tentativas
    Dado que o comando "generate" é invocado com "--until-converged"
    E a story informada é "Bloquear cartão de crédito imediatamente"
    Quando o score nunca atingir o threshold após múltiplas tentativas
    Então o loop deve encerrar com no máximo "50" tentativas
    E o resultado deve conter o melhor BDD obtido nas tentativas anteriores
    E o campo "converged" deve ser "False"

  Cenário: Geração com --until-converged converge antes do teto
    Dado que o comando "generate" é invocado com "--until-converged"
    E a story informada possui critérios de aceitação claros e objetivos
    Quando o score atingir ou superar o threshold em alguma tentativa
    Então o loop deve encerrar imediatamente nessa tentativa
    E o campo "converged" deve ser "True"

  # ─────────────────────────────────────────────────────────────────────────────
  # LOOP DE REFINAMENTO
  # ─────────────────────────────────────────────────────────────────────────────

  Cenário: Primeira tentativa usa prompt de geração inicial
    Dado que o RefinementLoop é instanciado com max_attempts igual a "3"
    E a user story "Cancelar assinatura do plano mensal" é fornecida
    Quando a tentativa "1" é executada
    Então o prompt enviado ao gerador deve conter o template "generate_bdd"
    E não deve conter termos de refinamento como "refine_bdd"

  Cenário: Tentativas subsequentes usam prompt de refinamento com fraquezas
    Dado que o RefinementLoop está na tentativa "2" ou superior
    E o score da tentativa anterior foi inferior ao threshold
    Quando a próxima tentativa é executada
    Então o prompt enviado ao gerador deve conter o resumo do score anterior
    E deve listar as dimensões com pontuação abaixo do threshold como "fraquezas"

  Cenário: Loop preserva o melhor BDD entre tentativas
    Dado que o RefinementLoop executa "3" tentativas
    E os scores obtidos são "6.5", "7.2" e "6.8" respectivamente
    Quando o loop encerrar sem convergência
    Então o BDD retornado deve ser o da tentativa com score "7.2"
    E o campo "converged" deve ser "False"

  # ─────────────────────────────────────────────────────────────────────────────
  # SISTEMA DE AVALIAÇÃO (4 MÉTRICAS)
  # ─────────────────────────────────────────────────────────────────────────────

  Cenário: Score final é calculado com os pesos corretos
    Dado que um BDD foi avaliado com as seguintes métricas:
      | Métrica         | Valor |
      | cobertura       | 8.0   |
      | clareza         | 7.0   |
      | estrutura       | 9.0   |
      | executabilidade | 6.0   |
    Quando o BDDScorer calcula o score final
    Então o score final deve ser "7.90" (pesos: 30%, 20%, 30%, 20%)

  Cenário: BDD aprovado quando score_final >= threshold
    Dado que o threshold configurado é "7.0"
    E o score_final calculado é "7.5"
    Quando o BDDScorer avalia o resultado
    Então o campo "aprovado" deve ser "True"

  Cenário: BDD reprovado quando score_final < threshold
    Dado que o threshold configurado é "7.0"
    E o score_final calculado é "6.9"
    Quando o BDDScorer avalia o resultado
    Então o campo "aprovado" deve ser "False"

  Cenário: Método weaknesses retorna apenas dimensões abaixo do threshold
    Dado que um ScoreResult possui cobertura "9.0", clareza "5.0", estrutura "8.0" e executabilidade "4.0"
    E o threshold é "7.0"
    Quando o método "weaknesses()" é chamado
    Então a lista retornada deve conter exatamente "2" itens
    E os itens devem corresponder a "Clareza" e "Executabilidade"

  Cenário: Avaliação de cobertura usa critérios do research quando disponíveis
    Dado que a user story possui critérios de aceitação implícitos
    E o research_context fornecido contém uma seção "CRITÉRIOS DE ACEITAÇÃO" explícita
    Quando o CoverageEvaluator avalia o BDD
    Então o score de cobertura deve ponderar "60%" para critérios da story e "40%" para critérios do research

  # ─────────────────────────────────────────────────────────────────────────────
  # COMANDO: evaluate
  # ─────────────────────────────────────────────────────────────────────────────

  Cenário: Avaliação de arquivo .feature existente
    Dado que existe um arquivo "tests/sample.feature" com cenários BDD válidos
    E o comando "evaluate" é invocado com "--story" e "--bdd tests/sample.feature"
    Quando o sistema executa a avaliação
    Então a saída deve exibir o score final formatado com as 4 métricas
    E deve mostrar "APROVADO" ou "REPROVADO"

  Cenário: Avaliação de BDD passado como texto inline
    Dado que o BDD é fornecido diretamente como string no argumento "--bdd"
    E a string contém "Funcionalidade:", "Cenário:", "Dado", "Quando" e "Então"
    Quando o comando "evaluate" é executado
    Então a avaliação deve ser concluída sem erros
    E o score final deve ser retornado corretamente

  # ─────────────────────────────────────────────────────────────────────────────
  # COMANDO: batch
  # ─────────────────────────────────────────────────────────────────────────────

  Cenário: Processamento em lote de CSV com múltiplas histórias
    Dado que o arquivo "neodataset.csv" existe na raiz do projeto
    E o comando "batch" é invocado com "--input neodataset.csv --sample 3"
    Quando o sistema processa as histórias
    Então o arquivo "batch_results.csv" deve ser criado na pasta de saída
    E deve conter uma linha por história processada com os campos:
      | Campo           |
      | story_id        |
      | title           |
      | model           |
      | score_final     |
      | cobertura       |
      | clareza         |
      | estrutura       |
      | executabilidade |
      | tentativas      |
      | tokens_usados   |
      | aprovado        |
      | convergiu       |
      | feature_file    |

  Cenário: Batch salva arquivos .feature para cada história processada
    Dado que o comando "batch" é executado com "--sample 2"
    Quando o sistema conclui o processamento
    Então para cada história um arquivo ".feature" deve existir em "features/"
    E um arquivo ".txt" com a user story original deve existir junto ao feature

  Cenário: Batch com flag --research habilita auto-research por história
    Dado que o comando "batch" é invocado com "--research --sample 2"
    Quando o sistema processa cada história
    Então a coluna "tokens_research" no CSV deve ser maior que zero para cada linha

  Cenário: Batch com --sample processa exatamente N histórias aleatórias
    Dado que o dataset contém mais de "10" histórias
    E o comando "batch" é invocado com "--sample 5"
    Quando o processamento é concluído
    Então o CSV de saída deve conter exatamente "5" linhas de dados (excluindo o cabeçalho)

  Cenário: Batch com --until-converged só avança após atingir threshold
    Dado que o comando "batch" é invocado com "--until-converged --sample 2"
    Quando o sistema processa uma história
    Então o loop deve continuar refinando até o score atingir o threshold ou esgotar "50" tentativas
    E o campo "convergiu" deve refletir o resultado correto em cada linha

  Cenário: Batch com --learn-from injeta contexto de insights no prompt
    Dado que existe um arquivo "insights.json" gerado previamente pelo comando "study"
    E o comando "batch" é invocado com "--learn-from insights.json --sample 2"
    Quando o sistema processa cada história
    Então o contexto de guia de estilo deve ser incluído no prompt de geração
    E a saída deve exibir "Insights carregados de: insights.json"

  Cenário: Batch falha com mensagem de erro quando CSV não é encontrado
    Dado que o arquivo "arquivo_inexistente.csv" não existe
    E o comando "batch" é invocado com "--input arquivo_inexistente.csv"
    Quando o sistema tenta carregar o dataset
    Então a saída deve exibir "Arquivo não encontrado: arquivo_inexistente.csv"
    E o processo deve encerrar com código de saída "1"

  # ─────────────────────────────────────────────────────────────────────────────
  # COMANDO: compare
  # ─────────────────────────────────────────────────────────────────────────────

  Cenário: Comparação de múltiplos modelos no mesmo dataset
    Dado que o comando "compare" é invocado com "--models flash,pro --sample-size 3"
    E o dataset "neodataset.csv" é informado
    Quando o sistema processa cada modelo nas mesmas histórias amostradas
    Então o arquivo "compare_results.csv" deve ser criado
    E deve conter linhas para cada combinação de modelo x história
    E a coluna "model" deve conter os valores "flash" e "pro"

  Cenário: Comparação usa o mesmo sample de histórias para todos os modelos
    Dado que o comando "compare" é invocado com "--models flash,flash-lite --sample-size 5"
    Quando o sistema amosta as histórias
    Então as "5" histórias selecionadas devem ser idênticas para ambos os modelos

  # ─────────────────────────────────────────────────────────────────────────────
  # COMANDO: experiment
  # ─────────────────────────────────────────────────────────────────────────────

  Cenário: Experimento científico completo gera CSV com todas as colunas
    Dado que o comando "experiment" é invocado com "--dataset neodataset.csv --sample-size 5"
    E os modelos padrão "flash,pro,flash-lite" são utilizados
    Quando o experimento é executado
    Então o arquivo "experiment_results.csv" deve ser criado
    E deve conter as colunas "story_id", "storypoints", "description" além das métricas padrão
    E deve haver uma linha por combinação de história x modelo

  Cenário: Experimento exibe progresso a cada 10 histórias
    Dado que o comando "experiment" é invocado com "--sample-size 15"
    Quando o sistema processa a décima história de um modelo
    Então a saída deve exibir o percentual de aprovações acumuladas

  # ─────────────────────────────────────────────────────────────────────────────
  # COMANDO: study
  # ─────────────────────────────────────────────────────────────────────────────

  Cenário: Study analisa resultados de batch e gera insights.json
    Dado que existe um arquivo "batch_results.csv" válido com coluna "feature_file" preenchida
    E o comando "study" é invocado com "--results batch_results.csv"
    Quando o sistema analisa os BDDs de alta e baixa qualidade
    Então o arquivo "insights.json" deve ser criado
    E deve conter as chaves "insights", "top_examples", "low_examples" e "meta"

  Cenário: Study carrega os top-N e bottom-N BDDs conforme configurado
    Dado que o comando "study" é invocado com "--top-n 3 --bottom-n 2"
    Quando o BatchAnalyzer processa o CSV
    Então "top_examples" no JSON deve conter no máximo "3" entradas
    E "low_examples" deve conter no máximo "2" entradas

  Cenário: Study falha com mensagem de erro quando CSV não existe
    Dado que o arquivo "resultados_inexistentes.csv" não existe
    E o comando "study" é invocado com "--results resultados_inexistentes.csv"
    Quando o sistema tenta carregar o arquivo
    Então a saída deve exibir "Arquivo não encontrado: resultados_inexistentes.csv"
    E o processo deve encerrar com código de saída "1"

  Cenário: load_study_context constrói string de contexto few-shot a partir do JSON
    Dado que existe um "insights.json" com "insights" e "top_examples" preenchidos
    Quando a função "load_study_context" é chamada com o caminho do arquivo
    Então a string retornada deve conter "GUIA DE ESTILO"
    E deve conter "EXEMPLOS DE REFERÊNCIA"
    E deve listar no máximo "3" exemplos de referência por padrão

  # ─────────────────────────────────────────────────────────────────────────────
  # COMANDO: pipeline
  # ─────────────────────────────────────────────────────────────────────────────

  Cenário: Pipeline completo executa as 3 fases em sequência
    Dado que o comando "pipeline" é invocado com "--input neodataset.csv --sample 3"
    Quando o sistema executa o pipeline completo
    Então a saída deve exibir "Fase 1/3 — Geração inicial"
    E deve exibir "Fase 2/3 — Estudo e extração de insights"
    E deve exibir "Fase 3/3 — Re-geração com insights aprendidos"
    E os arquivos "run1/batch_results.csv", "study_insights.json" e "run2/batch_results.csv" devem existir

  Cenário: Pipeline exibe comparativo de scores entre fase 1 e fase 3
    Dado que o pipeline concluiu todas as 3 fases com "--sample 3"
    Quando o resumo comparativo é exibido
    Então a saída deve conter "Score médio Fase 1:" e "Score médio Fase 3:"
    E deve exibir a variação de score com sinal positivo ou negativo

  Cenário: Pipeline aceita modelo diferente para a fase de study
    Dado que o comando "pipeline" é invocado com "--model flash --study-model pro"
    Quando a fase de estudo é executada
    Então o modelo utilizado na análise de insights deve ser "pro"
    E o modelo utilizado nas gerações deve ser "flash"

  Cenário: Pipeline com --research habilita auto-research em ambas as fases de geração
    Dado que o comando "pipeline" é invocado com "--research --sample 2"
    Quando as fases 1 e 3 são executadas
    Então a coluna "tokens_research" nos CSVs de ambas as fases deve conter valores maiores que zero

  # ─────────────────────────────────────────────────────────────────────────────
  # SELEÇÃO DE MODELOS
  # ─────────────────────────────────────────────────────────────────────────────

  Esquema do Cenário: Modelos Gemini são reconhecidos corretamente
    Dado que o alias de modelo "<alias>" é fornecido ao sistema
    Quando a função "_is_gemini" é avaliada
    Então o resultado deve ser "True"
    E uma instância de "GeminiGenerator" deve ser criada

    Exemplos:
      | alias          |
      | flash          |
      | pro            |
      | flash-lite     |
      | flash-1.5      |
      | gemini-2.0-flash |

  Esquema do Cenário: Modelos Claude são reconhecidos corretamente
    Dado que o alias de modelo "<alias>" é fornecido ao sistema
    Quando a função "_is_gemini" é avaliada
    Então o resultado deve ser "False"
    E uma instância de "ClaudeGenerator" deve ser criada

    Exemplos:
      | alias  |
      | sonnet |
      | opus   |
      | haiku  |

  # ─────────────────────────────────────────────────────────────────────────────
  # LOGGER E RASTREAMENTO DE TENTATIVAS
  # ─────────────────────────────────────────────────────────────────────────────

  Cenário: AttemptLogger registra todas as tentativas em CSV
    Dado que o AttemptLogger está configurado com um diretório de saída válido
    E o RefinementLoop executa "3" tentativas para uma story
    Quando o processo é concluído
    Então deve existir um arquivo CSV em "results/experiments/"
    E cada tentativa deve estar registrada como uma linha com modelo, score e tokens

  Cenário: Tokens de geração são rastreados corretamente no resultado
    Dado que o RefinementLoop executa "2" tentativas
    E cada tentativa consome tokens de entrada e saída
    Quando o RefinementResult é retornado
    Então "total_tokens" deve ser a soma de todos os tokens de entrada e saída das tentativas
    E "total_input_tokens" e "total_output_tokens" devem ser rastreados separadamente

  # ─────────────────────────────────────────────────────────────────────────────
  # CARREGAMENTO DE DATASET
  # ─────────────────────────────────────────────────────────────────────────────

  Cenário: Dataset CSV é carregado com colunas title, description e storypoints
    Dado que o arquivo "neodataset.csv" contém colunas "title", "description" e "storypoints"
    Quando a função "_load_dataset" é chamada com o caminho do arquivo
    Então cada item da lista retornada deve conter as chaves "title", "description" e "storypoints"
    E itens sem "title" devem ser ignorados

  Cenário: Dataset aceita variações de nome de coluna (case-insensitive)
    Dado que o CSV contém colunas nomeadas como "Title" e "Description" com maiúsculas
    Quando a função "_load_dataset" é chamada
    Então os dados devem ser carregados corretamente sem erros de KeyError
