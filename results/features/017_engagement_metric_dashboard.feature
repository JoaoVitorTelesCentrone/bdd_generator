# Story: Engagement metric dashboard
# Model: flash | Score: 4.7/10

Funcionalidade: Painel de Métricas de Engajamento

Cenário: Visualização inicial do painel com métricas chave
  Dado que o usuário "admin@empresa.com" está logado
  E que o usuário possui a permissão "visualizar_dashboard_engajamento"
  E que existem dados de engajamento disponíveis para o período padrão
  Quando o usuário acessa a URL "https://app.exemplo.com/dashboard/engajamento"
  Então o título "Métricas de Engajamento" é exibido no elemento `h1#dashboard-title`
  E a métrica "Usuários Ativos" é exibida com o valor "15.240" no elemento `div[data-metric="active-users"] .value`
  E a métrica "Duração Média da Sessão" é exibida com o valor "00:05:30" no elemento `div[data-metric="avg-session-duration"] .value`
  E a métrica "Visualizações de Página" é exibida com o valor "87.123" no elemento `div[data-metric="page-views"] .value`
  E um gráfico de linha "Tendência de Usuários Ativos" é exibido no elemento `canvas#active-users-chart`

Cenário: Filtrar métricas por um período específico
  Dado que o usuário "admin@empresa.com" está logado
  E que o usuário está no painel de engajamento "https://app.exemplo.com/dashboard/engajamento"
  E que existem dados de engajamento para "Últimos 30 dias"
  Quando o usuário seleciona a opção "Últimos 30 dias" no dropdown `select#date-range-filter`
  Então a métrica "Usuários Ativos" é exibida com o valor "55.000" no elemento `div[data-metric="active-users"] .value`
  E a métrica "Duração Média da Sessão" é exibida com o valor "00:04:15" no elemento `div[data-metric="avg-session-duration"] .value`
  E a métrica "Visualizações de Página" é exibida com o valor "250.000" no elemento `div[data-metric="page-views"] .value`
  E o gráfico de linha "Tendência de Usuários Ativos" é atualizado para o período selecionado

Cenário: Exibição de estado vazio quando não há dados para o período
  Dado que o usuário "admin@empresa.com" está logado
  E que o usuário está no painel de engajamento "https://app.exemplo.com/dashboard/engajamento"
  E que NÃO existem dados de engajamento para "Ontem"
  Quando o usuário seleciona a opção "Ontem" no dropdown `select#date-range-filter`
  Então a mensagem "Nenhum dado disponível para o período selecionado." é exibida no elemento `div.no-data-message`
  E a métrica "Usuários Ativos" exibe o valor "N/A" no elemento `div[data-metric="active-users"] .value`
  E a métrica "Duração Média da Sessão" exibe o valor "N/A" no elemento `div[data-metric="avg-session-duration"] .value`
  E nenhum gráfico é exibido no elemento `div.chart-container`

Cenário: Acesso negado para usuário sem permissão
  Dado que o usuário "editor@empresa.com" está logado
  E que o usuário NÃO possui a permissão "visualizar_dashboard_engajamento"
  Quando o usuário tenta acessar a URL "https://app.exemplo.com/dashboard/engajamento"
  Então o usuário é redirecionado para a URL "https://app.exemplo.com/acesso-negado"
  E a mensagem "Você não tem permissão para acessar esta página." é exibida no elemento `div.alert-danger`

Cenário: Visualização de métricas de interação específicas
  Dado que o usuário "admin@empresa.com" está logado
  E que o usuário está no painel de engajamento "https://app.exemplo.com/dashboard/engajamento"
  E que existem dados de interação disponíveis para o período padrão
  Quando o painel de métricas é completamente carregado
  Então a métrica "Total de Curtidas" é exibida com o valor "2.500" no elemento `div[data-metric="total-likes"] .value`
  E a métrica "Total de Comentários" é exibida com o valor "750" no elemento `div[data-metric="total-comments"] .value`
  E a métrica "Total de Compartilhamentos" é exibida com o valor "320" no elemento `div[data-metric="total-shares"] .value`
  E um gráfico de barras "Interações por Tipo" é exibido no elemento `canvas#interactions-chart`

Cenário: Indicador de carregamento durante a atualização de dados
  Dado que o usuário "admin@empresa.com" está logado
  E que o usuário está no painel de engajamento "https://app.exemplo.com/dashboard/engajamento"
  Quando o usuário seleciona uma nova opção no dropdown `select#date-range-filter`
  Então um indicador de carregamento é exibido no elemento `div.loading-spinner`
  E o indicador de carregamento não é mais exibido após "3" segundos
  E as métricas atualizadas são exibidas no painel