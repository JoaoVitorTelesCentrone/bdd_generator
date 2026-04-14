# Story: Fix time spent in growthbook
# Model: flash | Score: 7.7/10

Funcionalidade: Correção do Tempo Gasto no GrowthBook

  Cenário: Contagem precisa de tempo gasto durante interação ativa contínua
    Dado que o usuário está logado no GrowthBook
    E que a página "Relatório de Experimento X" está carregada
    Quando o usuário permanece ativamente na página por "15" segundos
    E navega para "outra página do GrowthBook"
    Então o tempo gasto registrado para "Relatório de Experimento X" deve ser "15" segundos
    E o sistema exibe o tempo como "00:00:15" em relatórios

  Cenário: Pausa e retomada da contagem por inatividade do usuário
    Dado que o usuário está logado no GrowthBook
    E que a página "Relatório de Experimento Y" está carregada
    Quando o usuário permanece ativamente na página por "10" segundos
    E permanece inativo na página por "40" segundos
    E permanece ativamente na página por "10" segundos
    E fecha a aba do navegador
    Então o tempo gasto registrado para "Relatório de Experimento Y" deve ser "20" segundos
    E o sistema exibe o tempo como "00:00:20"

  Cenário: Pausa e retomada da contagem por foco da aba do navegador
    Dado que o usuário está logado no GrowthBook
    E que a página "Painel de Métricas" está carregada na aba "A"
    Quando o usuário interage na aba "A" por "10" segundos
    E muda o foco do navegador para "outra aba" por "20" segundos
    E retorna o foco para a aba "A"
    E interage na aba "A" por "10" segundos
    E navega para "uma URL externa"
    Então o tempo gasto registrado para "Painel de Métricas" deve ser "20" segundos
    E o sistema exibe o tempo como "00:00:20"