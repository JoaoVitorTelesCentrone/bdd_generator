# Story: (bug): URL - target="_blank" rel="noopener noreferrer" Issues
# Model: flash | Score: 4.6/10

Cenário: URL externa em uma nova postagem não exibe atributos
  Dado que um usuário está autenticado e na tela de criação de postagem
  Quando o usuário insere "Confira: https://www.example.com" no corpo da postagem
  E o usuário clica no botão "Publicar Postagem"
  Então a postagem é exibida sem o texto "target="_blank" rel="noopener noreferrer""

Cenário: URL externa em um novo comentário não exibe atributos
  Dado que um usuário está autenticado e visualizando uma postagem com ID "post-123"
  Quando o usuário adiciona "Mais detalhes aqui: https://www.anothersite.org/info" no campo de comentário
  E o usuário clica no botão "Comentar"
  Então o comentário é exibido sem o texto "target="_blank" rel="noopener noreferrer""

Cenário: URL externa na descrição do perfil de canal não exibe atributos
  Dado que um usuário está autenticado e na tela de edição do perfil do canal "Canal Teste ABC"
  Quando o usuário insere "Meu site: https://channel.example.net/about" na descrição do canal
  E o usuário clica no botão "Salvar Alterações"
  Então o perfil do canal é exibido sem o texto "target="_blank" rel="noopener noreferrer""

Cenário: URL externa na descrição do perfil de grupo não exibe atributos
  Dado que um usuário está autenticado e na tela de edição do perfil do grupo "Grupo QA"
  Quando o usuário insere "Nosso fórum: https://group.forum.com/discuss" na descrição do grupo
  E o usuário clica no botão "Salvar Alterações"
  Então o perfil do grupo é exibido sem o texto "target="_blank" rel="noopener noreferrer""

Cenário: Edição de postagem com URL existente não introduz atributos
  Dado que existe uma postagem com ID "post-456" contendo a URL "https://old-link.com"
  E um usuário está autenticado e editando a postagem "post-456"
  Quando o usuário altera apenas o texto da postagem para "Texto atualizado: https://old-link.com"
  E o usuário clica no botão "Salvar Edição"
  Então a postagem editada é exibida sem o texto "target="_blank" rel="noopener noreferrer""

Cenário: Adição de URL externa em postagem existente não exibe atributos
  Dado que existe uma postagem com ID "post-789" sem URLs
  E um usuário está autenticado e editando a postagem "post-789"
  Quando o usuário adiciona "Leia mais em: https://new-article.net" ao corpo da postagem
  E o usuário clica no botão "Salvar Edição"
  Então a postagem editada é exibida sem o texto "target="_blank" rel="noopener noreferrer""

Cenário: URL interna do sistema não exibe atributos
  Dado que um usuário está autenticado e na tela de criação de postagem
  Quando o usuário insere "Veja meu perfil: https://app.example.com/profile/user123" no corpo da postagem
  E o usuário clica no botão "Publicar Postagem"
  Então a postagem é exibida sem o texto "target="_blank" rel="noopener noreferrer""