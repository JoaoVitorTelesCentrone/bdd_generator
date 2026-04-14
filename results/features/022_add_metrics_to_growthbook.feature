# Story: Add metrics to GrowthBook
# Model: flash | Score: 4.6/10

Funcionalidade: Gerenciamento de Métricas e Dimensões do GrowthBook

Cenário: Adicionar Métrica "Retenção de 2 Horas" com sucesso
  Dado que o usuário "admin@growthbook.com" está logado
  E que estou na página de adicionar métrica "https://app.growthbook.com/metrics/add"
  Quando preencho o campo input[name="metricName"] com "Retenção de 2 Horas"
  E preencho o campo textarea[name="metricDescription"] com "Retenção de usuários após 2 horas."
  E seleciono a opção "Retenção" no dropdown select[name="metricType"]
  E clico no botão button[data-testid="saveMetricButton"]
  Então vejo a mensagem ".alert-success" com "Métrica adicionada com sucesso!"
  E sou redirecionado para a URL "https://app.growthbook.com/metrics"