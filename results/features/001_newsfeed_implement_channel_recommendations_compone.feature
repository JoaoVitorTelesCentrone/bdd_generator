# Story: Newsfeed: Implement channel recommendations component - web
# Model: flash | Score: 4.8/10

Funcionalidade: Recomendações de Canais no Newsfeed

Cenário: Exibição inicial do componente de recomendações
  Dado que o usuário está logado e possui 5 canais para serem recomendados
  E nenhum desses canais está sendo seguido pelo usuário
  Quando o usuário navega para a URL "https://exemplo.com/newsfeed"
  Então o componente com o seletor `[data-testid="channel-recommendations-component"]` é visível
  E o título "Recomendações de Canais" é exibido dentro de `[data-testid="channel-recommendations-component"]`
  E 3 itens de recomendação com o seletor `[data-testid="channel-recommend