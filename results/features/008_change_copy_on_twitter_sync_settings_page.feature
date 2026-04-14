# Story: Change copy on Twitter Sync settings page
# Model: flash | Score: 7.5/10

Funcionalidade: Atualização do Texto na Página de Configurações de Sincronização com Twitter

Cenário: Exibição da mensagem sobre tweets excluídos na página de configurações
  Dado que o usuário "usuario@example.com" está logado
  Quando o usuário acessa a página de configurações "https://www.minds.com/settings/other/twitter-sync"
  Então o elemento `div[data-testid="twitter-sync-deleted-tweet-info"]` é exibido
  E o texto do elemento `div[data-testid="twitter-sync-deleted-tweet-info"]` é "Se um tweet for excluído no Twitter, ele não será automaticamente excluído no Minds."

Cenário: Mensagem sobre tweets excluídos visível com a sincronização do Twitter ativada
  Dado que o usuário "usuario@example.com" está logado
  E que a sincronização com o Twitter está ativada para o usuário
  Quando o usuário acessa a página de configurações "https://www.minds.com/settings/other/twitter-sync"
  Então o elemento `div[data-testid="twitter-sync-deleted-tweet-info"]` é exibido
  E o texto do elemento `div[data-testid="twitter-sync-deleted-tweet-info"]` é "Se um tweet for excluído no Twitter, ele não será automaticamente excluído no Minds."

Cenário: Mensagem sobre tweets excluídos visível com a sincronização do Twitter desativada
  Dado que o usuário "usuario@example.com" está logado
  E que a sincronização com o Twitter está desativada para o usuário
  Quando o usuário acessa a página de configurações "https://www.minds.com/settings/other/twitter-sync"
  Então o elemento `div[data-testid="twitter-sync-deleted-tweet-info"]` é exibido
  E o texto do elemento `div[data-testid="twitter-sync-deleted-tweet-info"]` é "Se um tweet for excluído no Twitter, ele não será automaticamente excluído no Minds."

Cenário: Exibição da segunda mensagem de aviso sobre posts do Minds não refletidos no Twitter
  Dado que o usuário "usuario@example.com" está logado
  Quando o usuário acessa a página de configurações "https://www.minds.com/settings/other/twitter-sync"
  Então o elemento `div[data-testid="twitter-sync-minds-post-update-info"]` é exibido
  E o texto do elemento `div[data-testid="twitter-sync-minds-post-update-info"]` é "Alterações em posts no Minds não são automaticamente refletidas no Twitter."