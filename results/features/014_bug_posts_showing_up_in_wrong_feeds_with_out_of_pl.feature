# Story: (bug) Posts showing up in wrong feeds, with out of place timestamps
# Model: flash | Score: 4.5/10

Funcionalidade: Correção da Ordem e Timestamp de Posts na Timeline

Cenário: Postagem fixada permanece no topo da timeline após impulsionamento de outras postagens
  Dado que o usuário "qa.tester@minds.com" está logado
  E que o usuário possui uma postagem fixada `div[data-post-id="post-fixado-1"]`
  E que o usuário possui as postagens `div[data-post-id="post-boost-A"]`, `div[data-post-id="post-boost-B"]`, `div[data-post-id="post-boost-C"]`
  Quando o usuário navega para a console de impulsionamento "https://www