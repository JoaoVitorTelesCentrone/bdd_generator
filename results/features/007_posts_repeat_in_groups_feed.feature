# Story: Posts repeat in Groups feed
# Model: flash | Score: 4.4/10

Cenário: Visualização inicial de um feed de grupo sem repetição
  Dado que sou um usuário logado
  E estou na página do feed do grupo "Grupo de Teste QA"
  Quando a página é carregada completamente
  Então todos os posts exibidos são únicos
  E não há posts duplicados visíveis

Cenário: Rolagem do feed de grupo sem repetição de posts
  Dado que sou um usuário logado
  E estou na página do feed do grupo "Grupo de Teste QA" com muitos posts
  Quando rolo a página para baixo para carregar mais conteúdo
  Então os novos posts carregados são únicos
  E nenhum post anterior ou novo é duplicado

Cenário: Feed de grupo com conteúdo variado sem repetição
  Dado que sou um usuário logado
  E estou na página do feed do grupo "Grupo de Conteúdo Misto"
  E o feed contém posts de texto, imagem e vídeo
  Quando a página é carregada completamente
  Então todos os posts de diferentes tipos são únicos
  E não há posts duplicados visíveis

Cenário: Navegação para o feed de um grupo específico problemático (pós-correção)
  Dado que sou um usuário logado
  E o grupo "Minds Brasil" (ID: 569272650258460672) era conhecido por repetições
  Quando acesso a página do feed do grupo "Minds Brasil"
  Então todos os posts exibidos são únicos
  E não há posts duplicados visíveis na tela

Cenário: Atualização da página do feed de grupo sem introduzir repetições
  Dado que sou um usuário logado
  E estou na página do feed do grupo "Grupo de Teste QA"
  Quando atualizo a página do navegador
  Então todos os posts exibidos após a atualização são únicos
  E não há posts duplicados visíveis