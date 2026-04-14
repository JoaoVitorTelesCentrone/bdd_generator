# Story: Boost inventory: Add boosts to Discovery
# Model: flash | Score: 4.5/10

Funcionalidade: Exibição de Conteúdo Promovido na Descoberta

Cenário: Um post promovido é exibido na Descoberta
  Dado que o usuário "user@example.com" está logado
  E que o post "ID_DO_POST_123" está ativo como promoção
  Quando o usuário acessa a página "https://app.minds.com/discovery"
  Então o post "ID_DO_POST_123" é exibido na lista de conteúdo `div[data-testid="discovery-feed"]`
  E o post "ID_DO_POST_123" possui um rótulo "Promovido" `span[data-testid="boost-label"]`

Cenário: Múltiplos posts promovidos são exibidos na Descoberta
  Dado que o usuário "user@example.com" está logado
  E que o post "ID_DO_POST_456" está ativo como promoção
  E que o post "ID_DO_POST_789" está ativo como promoção
  Quando o usuário acessa a página "https://app.minds.com/discovery"
  Então o post "ID_DO_POST_456" é exibido na lista de conteúdo `div[data-testid="discovery-feed"]`
  E o post "ID_DO_POST_456" possui um rótulo "Promovido" `span[data-testid="boost-label"]`
  E o post "ID_DO_POST_789" é exibido na lista de conteúdo `div[data-testid="discovery-feed"]`
  E o post "ID_DO_POST_789" possui um rótulo "Promovido" `span[data-testid="boost-label"]`

Cenário: Nenhum post promovido é exibido quando não há promoções ativas
  Dado que o usuário "user@example.com" está logado
  E que não há posts ativos como promoção
  Quando o usuário acessa a página "https://app.minds.com/discovery"
  Então nenhum rótulo "Promovido" `span[data-testid="boost-label"]` é exibido na lista de conteúdo `div[data-testid="discovery-feed"]`
  E o feed de descoberta `div[data-testid="discovery-feed"]` exibe apenas conteúdo orgânico

Cenário: Interação com um post promovido redireciona para o post completo
  Dado que o usuário "user@example.com" está logado
  E que o post "ID_DO_POST_101" está ativo como promoção
  E que o post "ID_DO_POST_101" é exibido na página "https://app.minds.com/discovery"
  Quando o usuário clica no post "ID_DO_POST_101" `div[data-testid="post-ID_DO_POST_101"]`
  Então o usuário é redirecionado para a página "https://app.minds.com/view/ID_DO_POST_101"

Cenário: Post promovido não é exibido como promovido após o término da promoção
  Dado que o usuário "user@example.com" está logado
  E que o post "ID_DO_POST_202" teve uma promoção que já