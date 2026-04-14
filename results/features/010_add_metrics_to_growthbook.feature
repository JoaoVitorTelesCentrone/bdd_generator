# Story: Add metrics to GrowthBook
# Model: flash | Score: 5.2/10

Funcionalidade: Gerenciamento de Métricas e Dimensões no GrowthBook

Cenário: Adicionar Métrica de Crescimento "Retenção de 2 horas"
  Dado que o usuário "admin@growthbook.com" está logado e na página de gerenciamento de métricas "https://app.growthbook.com/metrics"
  Quando o usuário clica no botão `button[data-testid="add-new-metric-button"]`
  E seleciona a opção "Métrica de Crescimento" no campo `select[id="metric-type-select"]`
  E preenche o campo `input[id="metric-name-input"]` com "Retenção de 2 horas"
  E preenche o campo `textarea[id="metric-description-textarea"]` com "Porcentagem de usuários que retornam em 2 horas"
  E clica no botão `button[data-testid="save-metric-button"]`
  Então a métrica "Retenção de 2 horas" aparece na lista de métricas `div[data-testid="metrics-list"]`
  E a métrica "Retenção de 2 horas" está disponível para seleção em novos experimentos `select[data-testid="experiment-metric-selector"]`

Cenário: Adicionar Métrica de Crescimento "Retenção de 3 dias"
  Dado que o usuário "admin@growthbook.com" está logado e na página de gerenciamento de métricas "https://app.growthbook.com/metrics"
  Quando o usuário clica no botão `button[data-testid="add-new-metric-button"]`
  E seleciona a opção "Métrica de Crescimento" no campo `select[id="metric-type-select"]`
  E preenche o campo `input[id="metric-name-input"]` com "Retenção de 3 dias"
  E preenche o campo `textarea[id="metric-description-textarea"]` com "Porcentagem de usuários que retornam em 3 dias"
  E clica no botão `button[data-testid="save-metric-button"]`
  Então a métrica "Retenção de 3 dias" aparece na lista de métricas `div[data-testid="metrics-list"]`
  E a métrica "Retenção de 3 dias" está disponível para seleção em novos experimentos `select[data-testid="experiment-metric-selector"]`

Cenário: Adicionar Métrica de Crescimento "Canal seguido"
  Dado que o usuário "admin@growthbook.com" está logado e na página de gerenciamento de métricas "https://app.growthbook.com/metrics"
  Quando o usuário clica no botão `button[data-testid="add-new-metric-button"]`
  E seleciona a opção "Métrica de Crescimento" no campo `select[id="metric-type-select"]`
  E preenche o campo `input[id="metric-name-input"]` com "Canal seguido"
  E preenche o campo `textarea[id="metric-description-textarea"]` com "Número de canais que um usuário seguiu"
  E clica no botão `button[data-testid="save-metric-button"]`
  Então a métrica "Canal seguido" aparece na lista de métricas `div[data-testid="metrics-list"]`
  E a métrica "Canal seguido" está disponível para seleção em novos experimentos `select[data-testid="experiment-metric-selector"]`

Cenário: Adicionar Métrica de Engajamento "Fez um comentário / resposta"
  Dado que o usuário "admin@growthbook.com" está logado e na página de gerenciamento de métricas "https://app.growthbook.com/metrics"
  Quando o usuário clica no botão `button[data-testid="add-new-metric-button"]`
  E seleciona a opção "Métrica de Engajamento" no campo `select[id="metric-type-select"]`
  E preenche o campo `input[id="metric-name-input"]` com "Fez um comentário / resposta"
  E preenche o campo `textarea[id="metric-description-textarea"]` com "Usuários que fizeram um comentário ou resposta"
  E clica no botão `button[data-testid="save-metric-button"]`
  Então a métrica "Fez um comentário / resposta