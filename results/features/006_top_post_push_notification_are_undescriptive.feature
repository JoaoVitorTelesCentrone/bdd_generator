# Story: Top post push notification are undescriptive
# Model: flash | Score: 4.5/10

Funcionalidade: Notificações de Push para Top Posts

Cenário: Postagem se torna Top Post e gera notificação descritiva
  Dado que o usuário "Alice" (ID: #user-alice) publicou um post "Minha Viagem Incrível à Praia" (ID: #post-123)
  E que o post (ID: #post-123) atingiu 100 curtidas em 5 minutos
  E que o usuário "Bob" (ID: #user-bob) está logado em seu dispositivo móvel
  E que o usuário "Bob" (ID: #user-bob) tem notificações de "Top Post" ativadas
  Quando o post (ID: #post-123) atinge o limiar de engajamento para "Top Post"
  Então o usuário "Bob" (ID: #user-bob) recebe uma notificação push contendo "Top Post: Alice postou 'Minha Viagem Incrível à Praia'"

Cenário: Postagem com conteúdo longo se torna Top Post e gera notificação truncada
  Dado que o usuário "Charlie" (ID: #user-charlie) publicou um post com título "Novas Descobertas Científicas Revolucionárias"
  E que o conteúdo do post (ID: #post-456) possui mais de 500 caracteres
  E que o post (ID: #post-456) atingiu 200 curtidas em 10 minutos
  E que o usuário "Diana" (ID: #user-diana) está logada em seu dispositivo móvel
  E que o usuário "Diana" (ID: #user-diana) tem notificações de "Top Post" ativadas
  Quando o post (ID: #post-456) atinge o limiar de engajamento para "Top Post"
  Então o usuário "Diana" (ID: #user-diana) recebe uma notificação push contendo "Top Post: Charlie postou 'Novas Descobertas Científicas Revolucionárias...'"

Cenário: Usuário desabilita notificações de Top Post e não as recebe
  Dado que o usuário "Eve" (ID: #user-eve) está logada em seu dispositivo móvel
  E que o usuário "Eve" (ID: #user-eve) desabilitou as notificações de "Top Post" em "Configurações" (URL: https://app.exemplo.com/configuracoes-notificacoes)
  E que um post de "Frank" (ID: #user-frank) (ID: #post-789) se tornou um "Top Post"
  Quando o post (ID: #post-789) atinge o limiar de engajamento para "Top Post"
  Então o usuário "Eve" (ID: #user-eve) não recebe nenhuma notificação push

Cenário: Postagem com apenas imagem se torna Top Post e gera notificação genérica
  Dado que o usuário "Grace" (ID: #user-grace) publicou um post contendo apenas uma imagem (ID: #post-101)
  E que o post (ID: #post-101) atingiu 500 visualizações em 15 minutos
  E que o usuário "Heidi" (ID: #user-heidi) está logada em seu dispositivo móvel
  E que o usuário "Heidi" (ID: #user-heidi) tem notificações de "Top Post" ativadas
  Quando o post (ID: #post-101) atinge o limiar de engajamento para "Top Post"
  Então o usuário "Heidi" (ID: #user-heidi) recebe uma notificação push contendo "Top Post: Grace postou uma imagem popular"