# Story: Latest / Top feed: Feed composition spec
# Model: flash | Score: 7.0/10

Funcionalidade: Gerenciamento de Visualizações do Feed de Notícias

Cenário: Visualização padrão "Mais Recentes" ao acessar o feed
  Dado que o usuário está logado
  Quando o usuário acessa a URL "https://app.exemplo.com/feed"
  Então o botão `button[data-feed-type="latest"]` possui a classe CSS "active"
  E o botão `button[data-feed-type="top"]` não possui a classe CSS "active"
  E a seção `div[data-feed-container="latest"]` é visível
  E a seção `div[data-feed-container="top"]` não é visível

Cenário: Composição da visualização "Mais Recentes"
  Dado que o usuário está na visualização "Mais Recentes" do feed
  Quando o feed é completamente carregado
  Então o elemento `div[data-component="boost-rotator"]` é visível
  E a seção `section[data-feed-section="latest-posts"]` exibe "3" posts
  E a seção `section[data-feed-section="top-posts-latest-view"]` exibe "3" posts
  E o link `a[data-action="see-more-top-posts"]` é visível
  E a seção `div[data-feed-container="latest"]` exibe mais de "3" posts no total

Cenário: Composição da visualização "Mais Populares"
  Dado que o usuário está logado
  E que o usuário acessa a URL "https://app.exemplo.com/feed"
  Quando o usuário clica no botão `button[data-feed-type="top"]`
  Então o elemento `div[data-component="boost-rotator"]` é visível
  E a seção `div[data-feed-container="top"]` exibe mais de "5" posts
  E a seção `div[data-feed-container="latest"]` não é visível

Cenário: Alternar da visualização "Mais Recentes" para "Mais Populares"
  Dado que o usuário está na visualização "Mais Recentes" do feed
  Quando o usuário clica no botão `button[data-feed-type="top"]`
  Então o botão `button[data-feed-type="top"]` possui a classe CSS "active"
  E o botão `button[data-feed-type="latest"]` não possui a classe CSS "active"
  E a seção `div[data-feed-container="top"]` é visível
  E a seção `div[data-feed-container="latest"]` não é visível

Cenário: Alternar da visualização "Mais Populares" para "Mais Recentes"
  Dado que o usuário está na visualização "Mais Populares" do feed
  Quando o usuário clica no botão `button[data-feed-type="latest"]`
  Então o botão `button[data-feed-type="latest"]` possui a classe CSS "active"
  E o botão `button[data-feed-type="top"]` não possui a classe CSS "active"
  E a seção `div[data-feed-container="latest"]` é visível
  E a seção `div[data-feed-container="top"]` não é visível

Cenário: Carregamento de mais posts via infinite scroll na visualização "Mais Recentes"
  Dado que o usuário está na visualização "Mais Recentes" do feed
  E o feed exibe "10" posts iniciais no elemento `div[data-feed-container="latest"]`
  Quando o usuário rola a página para baixo até o final
  Então o feed `div[data-feed-container="latest"]` exibe mais de "10" posts
  E os novos posts são do tipo "Mais Recentes"

Cenário: Carregamento de mais posts via infinite scroll na visualização "Mais Populares"
  Dado que o usuário está na visualização "Mais Populares" do feed
  E o feed exibe "10" posts iniciais no elemento `div[data-feed-container="top"]`
  Quando o usuário rola a página para baixo até o final
  Então o feed `div[data-feed-container="top"]` exibe mais de "10" posts
  E os novos posts são do tipo "Mais Populares"