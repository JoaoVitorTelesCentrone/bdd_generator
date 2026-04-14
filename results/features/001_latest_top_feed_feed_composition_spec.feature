# Story: Latest / Top feed: Feed composition spec
# Model: flash | Score: 7.0/10

Funcionalidade: Gerenciamento de Visualizações do Feed de Notícias

Cenário: Usuário é padronizado para a visualização "Mais Recentes" ao acessar o feed
  Dado que o usuário "usuario@example.com" está logado
  Quando o usuário acessa a página inicial "https://www.minds.com/feed"
  Então o seletor de visualização "Mais Recentes" `button[data-testid="toggle-latest-view"]` está ativo
  E o feed `div[data-testid="latest-feed-view"]` da visualização "Mais Recentes" é exibido
  E o feed `div[data-testid="top-feed-view"]` da visualização "Principais" não é exibido

Cenário: Componentes da visualização "Mais Recentes" são exibidos corretamente
  Dado que o usuário está na página inicial "https://www.minds.com/feed"
  E que a visualização "Mais Recentes" `div[data-testid="latest-feed-view"]` está ativa
  Quando a página é carregada
  Então o módulo "Boost Rotator" `div[data-testid="boost-rotator"]` é exibido
  E a seção "Mais Recentes" `div[data-testid="latest-posts-section"]` exibe "3" posts
  E a seção "Principais Posts" `div[data-testid="top-posts-section"]` exibe "3" posts
  E o link "Ver mais" `a[data-testid="see-more-top-posts"]` para posts principais é exibido

Cenário: Usuário pode alternar para a visualização "Principais"
  Dado que o usuário está na página inicial "https://www.minds.com/feed"
  E que a visualização "Mais Recentes" `div[data-testid="latest-feed-view"]` está ativa
  Quando o usuário clica no botão "Principais" `button[data-testid="toggle-top-view"]`
  Então o seletor de visualização "Principais" `button[data-testid="toggle-top-view"]` está ativo
  E o feed `div[data-testid="top-feed-view"]` da visualização "Principais" é exibido
  E o feed `div[data-testid="latest-feed-view"]` da visualização "Mais Recentes" não é exibido

Cenário: Componentes da visualização "Principais" são exibidos corretamente
  Dado que o usuário está na página inicial "https://www.minds.com/feed"
  E que a visualização "Principais" `div[data-testid="top-feed-view"]` está ativa
  Quando a página é carregada
  Então o módulo "Boost Rotator" `div[data-testid="boost-rotator"]` é exibido
  E o feed `div[data-testid="top-feed-view"]` contém posts
  E a seção "Mais Recentes" `div[data-testid="latest-posts-section"]` não é exibida
  E a seção "Principais Posts" `div[data-testid="top-posts-section"]` não é exibida
  E o link "Ver mais" `a[data-testid="see-more-top-posts"]` não é exibido

Cenário: Usuário pode alternar de volta para a visualização "Mais Recentes"
  Dado que o usuário está na página inicial "https://www.minds.com/feed"
  E que a visualização "Principais" `div[data-testid="top-feed-view"]` está ativa
  Quando o usuário clica no botão "Mais Recentes" `button[data-testid="toggle-latest-view"]`
  Então o seletor de visualização "Mais Recentes" `button[data-testid="toggle-latest-view"]` está ativo
  E o feed `div[data-testid="latest-feed-view"]` da visualização "Mais Recentes" é exibido
  E o feed `div[data-testid="top-feed-view"]` da visualização "Principais" não é exibido

Cenário: Rolagem infinita funciona na visualização "Mais Recentes"
  Dado que o usuário está na página inicial "https://www.minds.com/feed"
  E que a visualização "Mais Recentes" `div[data-testid="latest-feed-view"]` está ativa
  E que "10" posts estão visíveis no feed `div[data-testid="latest-feed-view"]`
  Quando o usuário rola a página para baixo `body`
  Então mais posts são carregados automaticamente
  E o feed `div[data-testid="latest-feed-view"]` contém mais de "10" posts

Cenário: Rolagem infinita funciona na visualização "Principais"
  Dado que o usuário está na página inicial "https://www.minds.com/feed"
  E que a visualização "Principais" `div[data-testid="top-feed-view"]` está ativa
  E que "10" posts estão visíveis no feed `div[data-testid="top-feed-view"]`
  Quando o usuário rola a página para baixo `body`
  Então mais posts são carregados automaticamente
  E o feed `div[data-testid="top-feed-view"]` contém mais de "10" posts