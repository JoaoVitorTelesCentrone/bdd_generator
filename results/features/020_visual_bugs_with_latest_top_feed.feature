# Story: Visual bugs with latest top feed
# Model: flash | Score: 5.9/10

Funcionalidade: Correção de Bugs Visuais no Feed

  Cenário: Verificar cores corretas para o rótulo "Top Feed" e ícone em Modo Claro
    Dado que o usuário está no "Modo Claro"
    E que o usuário acessou a página do feed "https://app.exemplo.com/feed"
    Quando o usuário acessa a página do feed
    Então o rótulo "#top-feed-label" exibe a cor "rgb(0, 0, 0)"
    E o ícone de alternância de feed "#feed-toggle-icon" exibe a cor "rgb(0, 0, 0)"

  Cenário: Verificar cores corretas para o rótulo "Latest Feed" e ícone em Modo Claro
    Dado que o usuário está no "Modo Claro"
    E que o usuário acessou a página do feed "https://app.exemplo.com/feed"
    Quando o usuário clica no ícone de alternância "#feed-toggle-icon"
    Então o rótulo "#latest-feed-label" exibe a cor "rgb(0, 0, 0)"
    E o ícone de alternância de feed "#feed-toggle-icon" exibe a cor "rgb(0, 0, 0)"

  Cenário: O tooltip do alternador de feed persiste até o clique
    Dado que o usuário acessou a página do feed "https://app.exemplo.com/feed"
    E que o tooltip do alternador de feed "#feed-toggle-tooltip" está visível
    Quando o usuário espera por "5" segundos
    Então o tooltip do alternador de feed "#feed-toggle-tooltip" ainda está visível

  Cenário: O tooltip do alternador de feed desaparece após o clique
    Dado que o usuário acessou a página do feed "https://app.exemplo.com/feed"
    E que o tooltip do alternador de feed "#feed-toggle-tooltip" está visível
    Quando o usuário clica no ícone de alternância "#feed-toggle-icon"
    Então o tooltip do alternador de feed "#feed-toggle-tooltip" não está visível