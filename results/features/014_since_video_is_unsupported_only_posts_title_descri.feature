# Story: Since video is unsupported, only posts title, description and reference minds link
# Model: flash | Score: 5.8/10

Funcionalidade: Criação de Post (Sem Suporte a Vídeo)

Contexto:
  Dado que o usuário está logado
  E está na página de criação de post "https://app.exemplo.com/posts/novo"

Cenário: Criação bem-sucedida de post com todos os campos permitidos
  Quando preencho o campo de título "#post-title" com "Meu Primeiro Post Importante"
  E preencho o campo de descrição "#post-description" com "Esta é uma descrição detalhada do meu post."
  E preencho o campo de link de referência "#post-minds-link" com "https://www.minds.com/usuario/meu-post"
  E clico no botão "Publicar" "button[type='submit']"
  Então sou redirecionado para a página de detalhes do post "https://app.exemplo.com/posts/meu-primeiro-post-importante"
  E vejo o título "Meu Primeiro Post Importante" ".post-detail-title"
  E vejo a descrição "Esta é uma descrição detalhada do meu post." ".post-detail-description"
  E vejo o link "https://www.minds.com/usuario/meu-post" ".post-detail-minds-link"

Cenário: Ausência de opção para inclusão de vídeo
  Quando a página de criação de post é carregada
  Então não vejo o elemento "input[type='file'][accept*='video']"
  E não vejo o botão "Adicionar Vídeo" "button[data-testid='add-video']"

Cenário: Criação de post apenas com título e descrição
  Quando preencho o campo de título "#post-title" com "Apenas Título e Descrição"
  E preencho o campo de descrição "#post-description" com "Conteúdo mínimo para o post."
  E clico no botão "Publicar" "button[type='submit']"
  Então sou redirecionado para a página de detalhes do post "https://app.exemplo.com/posts/apenas-titulo-e-descricao"
  E vejo o título "Apenas Título e Descrição" ".post-detail-title"
  E vejo a descrição "Conteúdo mínimo para o post." ".post-detail-description"
  E não vejo o link de referência ".post-detail-minds-link"

Cenário: Falha ao criar post com título vazio
  Quando preencho o campo de descrição "#post-description" com "Descrição sem título."
  E preencho o campo de link de referência "#post-minds-link" com "https://www.minds.com/usuario/outro-post"
  E cl