# Story: Show posts from subscribed Groups in Newsfeed
# Model: flash | Score: 3.8/10

Funcionalidade: Exibição de Publicações de Grupos Assinados no Feed de Notícias

Cenário: Usuário vê nova publicação de grupo assinado no Feed de Notícias
  Dado que o usuário "Alice" está logado
  E que o usuário "Alice" está assinado no grupo "Programação"
  E que o Feed de Notícias `div[data-testid="newsfeed-list"]` de "Alice" foi carregado
  Quando o usuário "Bob" cria uma nova publicação "Melhores IDEs de 2023" no grupo "Programação"
  Então o Feed de Notícias `div[data-testid="newsfeed-list"]` de "Alice" exibe a publicação "Melhores IDEs de 2023"
  E a publicação "Melhores IDEs de 2023" tem o rótulo `span[data-testid="group-origin"]` "Grupo: Programação"

Cenário: Usuário não vê publicação de grupo não assinado no Feed de Notícias
  Dado que o usuário "Alice" está logado
  E que o usuário "Alice" NÃO está assinado no grupo "Culinária"
  E que o Feed de Notícias `div[data-testid="newsfeed-list"]` de "Alice" foi carregado
  Quando o usuário "Carol" cria uma nova publicação "Receitas Veganas Rápidas" no grupo "Culinária"
  Então o Feed de Notícias `div[data-testid="newsfeed-list"]` de "Alice" NÃO exibe a publicação "Receitas Veganas Rápidas"

Cenário: Usuário vê publicações de múltiplos grupos assinados no Feed de Notícias
  Dado que o usuário "Alice" está logado
  E que o usuário "Alice" está assinado no grupo "Programação"
  E que o usuário "Alice" está assinado no grupo "Design Gráfico"
  E que o Feed de Notícias `div[data-testid="newsfeed-list"]` de "Alice" foi carregado
  Quando o usuário "Bob" cria a publicação "Novidades Python 3