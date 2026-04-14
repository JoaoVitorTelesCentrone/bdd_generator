# Story: Discovery feed paginated loading issue
# Model: flash | Score: 4.3/10

Funcionalidade: Carregamento Paginado do Feed de Descoberta

Cenário: Carregamento automático de mais posts ao rolar para o final do feed
  Dado que o usuário acessa o feed de descoberta "https://www.minds.com/discover"
  E que o feed exibe "10" posts `div[data-testid="feed-post"]` na tela inicial
  Quando o usuário rola a página até o final do feed `div[data-testid="feed-container"]`
  Então o indicador de carregamento `span[data-testid="loading-indicator"]` aparece
  E o indicador de carregamento `span[data-testid="loading-indicator"]` desaparece após "3" segundos
  E o feed exibe um total de "20" posts `div[data-testid="feed-post"]`

Cenário: Exibição de mensagem quando não há mais posts para carregar
  Dado que o usuário acessa o feed de descoberta "https://www.minds.com/discover"
  E que o feed exibe "15" posts `div[data-testid="feed-post"]`
  E que não há mais posts disponíveis para carregar
  Quando o usuário rola a página até o final do feed `div[data-testid="feed-container"]`
  Então o indicador de carregamento `span[data-testid="loading-indicator"]` aparece
  E o indicador de carregamento `span[data-testid="loading-indicator"]` desaparece
  E o feed exibe a mensagem "Sem mais posts para exibir" `div[data-testid="no-more-posts-message"]`
  E o feed continua exibindo "15" posts `div[data-testid="feed-post"]`

Cenário: Falha no carregamento devido a erro de rede
  Dado que o usuário acessa o feed de descoberta "https://www.minds.com/discover"
  E que o feed exibe "10" posts `div[data-testid="feed-post"]`
  E que ocorre um erro de rede ao tentar carregar mais posts
  Quando o usuário rola a página até o final do feed `div[data-testid="feed-container"]`
  Então o indicador de carregamento `span[data-testid="loading-indicator"]` aparece
  E o indicador de carregamento `span[data-testid="loading-indicator"]` desaparece
  E o feed exibe uma mensagem de erro "Erro ao carregar mais posts. Tentar novamente?" `div[data-testid="error-message"]`
  E um botão "Tentar Novamente" `button[data-testid="retry-button"]` é exibido

Cenário: Retentar carregamento após erro de rede
  Dado que o usuário acessa o feed de descoberta "https://www.minds.com/discover"
  E que o feed exibe "10" posts `div[data-testid="feed-post"]`
  E que uma mensagem de erro "Erro ao carregar mais posts. Tentar novamente?" `div[data-testid="error-message"]` é exibida
  E que um botão "Tentar Novamente" `button[data-testid="retry-button"]` é exibido
  E que a rede está agora funcional
  Quando o usuário clica no botão "Tentar Novamente" `button[data-testid="retry-button"]`
  Então o indicador de carregamento `span[data-testid="loading-indicator"]` aparece
  E o indicador de carregamento `span[data-testid="loading-indicator"]` desaparece após "3" segundos
  E a mensagem de erro `div[data-testid="error-message"]` desaparece
  E o feed exibe um total de "20" posts `div[data-testid="feed-post"]`

Cenário: Feed de descoberta inicialmente vazio
  Dado que o usuário acessa o feed de descoberta "https://www.minds.com/discover"
  E que não há posts disponíveis para o feed de descoberta
  Quando a página