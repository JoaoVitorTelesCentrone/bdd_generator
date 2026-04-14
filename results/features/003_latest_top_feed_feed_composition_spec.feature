# Story: Latest / Top feed: Feed composition spec
# Model: flash | Score: 7.4/10

Cenário: Visualização padrão do feed como "Últimas" ao acessar
  Dado que um usuário está logado na plataforma e acessa a URL "/feed"
  Quando a página do feed de notícias é carregada
  Então a aba "#tab-latest" deve estar selecionada
  E o elemento "#boost-rotator" deve ser exibido
  E a seção "#latest-posts-section" deve exibir 3 posts
  E a seção "#top-posts-preview" deve exibir 3 posts
  E o link "Ver mais" com o seletor "#see-more-top-posts" deve estar visível
  E a lista de posts do feed principal "#feed-list-latest" deve carregar posts

Cenário: Alternar para a visualização "Principais"
  Dado que o usuário está na visualização "Últimas" do feed
  Quando o usuário clica na aba "#tab-top"
  Então a aba "#tab-top" deve estar selecionada
  E o elemento "#boost-rotator" deve ser exibido
  E a seção "#latest-posts-section" não deve ser exibida
  E a seção "#top-posts-preview" não deve ser exibida
  E o link "Ver mais" com o seletor "#see-more-top-posts" não deve ser exibido
  E a lista de posts do feed principal "#feed-list-top" deve carregar posts principais

Cenário: Alternar de volta para a visualização "Últimas"
  Dado que o usuário está na visualização "Principais" do feed
  Quando o usuário clica na aba "#tab-latest"
  Então a aba "#tab-latest" deve estar selecionada
  E o elemento "#boost-rotator" deve ser exibido
  E a seção "#latest-posts-section" deve exibir 3 posts
  E a seção "#top-posts-preview" deve exibir 3 posts
  E o link "Ver mais" com o seletor "#see-more-top-posts" deve estar visível
  E a lista de posts do feed principal "#feed-list-latest" deve carregar posts

Cenário: Carregamento de mais posts em "Últimas" ao rolar
  Dado que o usuário está na visualização "Últimas" do feed
  E a lista "#feed-list-latest" exibe 10 posts
  Quando o usuário rola a página para baixo até o final
  Então a lista "#feed-list-latest" deve exibir mais de 10 posts
  E os novos posts carregados devem ser do tipo "Últimas"

Cenário: Carregamento de mais posts em "Principais" ao rolar
  Dado que o usuário está na visualização "Principais" do feed
  E a lista "#feed-list-top" exibe 10 posts
  Quando o usuário rola a página para baixo até o final
  Então a lista "#feed-list-top" deve exibir mais de 10 posts
  E os novos posts carregados devem ser do tipo "Principais"

Cenário: Interação com o link "Ver mais" na visualização "Últimas"
  Dado que o usuário está na visualização "Últimas" do feed
  Quando o usuário clica no link "#see-more-top-posts"
  Então o usuário deve ser redirecionado para a URL "/feed/top-posts"