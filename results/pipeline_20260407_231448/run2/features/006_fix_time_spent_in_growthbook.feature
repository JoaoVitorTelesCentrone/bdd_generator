# Story: Fix time spent in growthbook
# Model: flash | Score: 7.1/10

Funcionalidade: Correção do Tempo Gasto na Plataforma Growthbook

Cenário: Cálculo preciso do tempo ativo em um experimento
  Dado que um usuário autenticado está na página do experimento "Teste A/B de Layout"
  Quando o usuário interage com a página por "30" segundos
  Então o sistema registra o tempo gasto para o experimento "Teste A/B de Layout" como "00:00:30"

Cenário: Cálculo preciso do tempo ativo em um relatório
  Dado que um usuário autenticado está na página do relatório "Performance da Campanha X"
  Quando o usuário interage com a página por "1 minuto e 15 segundos"
  Então o sistema registra o tempo gasto para o relatório "Performance da Campanha X" como "00:01:15"

Cenário: Exibição consistente do tempo gasto no dashboard e relatório
  Dado que o sistema registrou "00:02:45" de tempo gasto para o experimento "Novo Onboarding" de um usuário autenticado
  Quando o usuário navega para o "Dashboard de Experimentos"
  Então o sistema exibe o tempo gasto para o experimento "Novo Onboarding" como "00:02:45"
  E Quando o usuário navega para o "Relatório de Experimentos"
  Então o sistema exibe o tempo gasto para o experimento "Novo Onboarding" como "00:02:45"

Cenário: Pausa na contagem de tempo por inatividade do usuário
  Dado que um usuário autenticado está na página do experimento "Teste de Inatividade"
  E que o sistema já registrou "00:01:00" de tempo ativo para este experimento
  Quando o usuário não interage com a página por "5" minutos
  Então o sistema pausa a contagem do tempo gasto
  E o tempo gasto registrado para o experimento "Teste de Inatividade" permanece "00:01:00"

Cenário: Registro de tempo gasto ao navegar para outra página
  Dado que um usuário autenticado está na página do experimento "Experimento de Navegação"
  E que o usuário interagiu com a página por "2" minutos
  Quando o usuário navega para a página "Visão Geral"
  Então o sistema registra o tempo gasto para o experimento "Experimento de Navegação" como "00:02:00"

Cenário: Contagem de tempo