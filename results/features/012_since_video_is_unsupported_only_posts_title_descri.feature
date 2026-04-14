# Story: Since video is unsupported, only posts title, description and reference minds link
# Model: flash | Score: 7.3/10

Funcionalidade: Criação de Posts com Conteúdo Restrito

Cenário: Publicar post com título, descrição e link Minds válido
  Dado que o usuário está logado e na página de criação de posts "https://app.minds.com/create"
  Quando o usuário digita "Título do Meu Post" no campo `input[name="title"]`
  E o usuário digita "Descrição detalhada do meu post." no campo `textarea[name="description"]`
  E o usuário digita "https://www.minds.com/meu-perfil/minha-postagem" no campo `input[name="link"]`
  E o usuário clica no botão `button[data-testid="publish-post"]`
  Então o post é publicado com sucesso
  E o post publicado contém o título "Título do Meu Post"
  E o post publicado contém a descrição "Descrição detalhada do meu post."
  E o post publicado exibe o link "https://www.minds.com/meu-perfil/minha-postagem"

Cenário: Publicar post apenas com título e descrição
  Dado que o usuário está logado e na página de criação de posts "https://app.minds.com/create"
  Quando o usuário digita "Post Simples" no campo `input[name="title"]`
  E o usuário digita "Apenas um post com texto." no campo `textarea[name="description"]`
  E o usuário clica no botão `button[data-testid="publish-post"]`
  Então o post é publicado com sucesso
  E o post publicado contém o título "Post Simples"
  E o post publicado contém a descrição "Apenas um post com texto."
  E o post publicado não exibe um link

Cenário: Publicar post apenas com título e link Minds válido
  Dado que o usuário está logado e na página de criação de posts "https://app.minds.com/create"
  Quando o usuário digita "Post com Link Importante" no campo `input[name="title"]`
  E o usuário digita "https://www.minds.com/outro-perfil/outra-postagem" no campo `input[name="link"]`
  E o usuário clica no botão `button[data-testid="publish-post"]`
  Então o post é publicado com sucesso
  E o post publicado contém o título "Post com Link Importante"
  E o post publicado exibe o link "https://www.minds.com/outro-perfil/outra-postagem"
  E o post publicado não contém uma descrição

Cenário: Publicar post apenas com título
  Dado que o usuário está logado e na página de criação de posts "https://app.minds.com/create"
  Quando o usuário digita "Apenas Título" no campo `input[name="title"]`
  E o usuário clica no botão `button[data-testid="publish-post"]`
  Então o post é publicado com sucesso
  E o post publicado contém o título "Apenas Título"
  E o post publicado não contém uma descrição
  E o post publicado não exibe um link

Cenário: Tentar publicar post com conteúdo de vídeo
  Dado que o usuário está logado e na página de criação de posts "https://app.minds.com/create"
  Quando o usuário tenta carregar o arquivo "meu_video.mp4" usando `input[type="file"][accept="video/*"]`
  Então uma mensagem de erro `div[data-testid="error-message"]` é exibida com "Vídeos não são suportados"
  E o botão `button[data-testid="publish-post"]` permanece desabilitado

Cenário: Tentar publicar post com link que não é do Minds
  Dado que o usuário está logado e na página de criação de posts "https://app.minds.com/create"
  Quando o usuário digita "Título com Link Externo" no campo `input[name="title"]`
  E o usuário digita "https://www.youtube.com/watch?v=123" no campo `input[name="link"]`
  E o usuário clica no botão `button[data-testid="publish-post"]`
  Então uma mensagem de erro `span[data-testid="link-error"]` é exibida com "Apenas links do Minds são permitidos"
  E o post não é publicado

Cenário: Tentar publicar post com link Minds em formato inválido
  Dado que o usuário está logado e na página de criação de posts "https://app.minds.com/create"
  Quando o usuário digita "Título com Link Malformatado" no campo `input[name="title"]`
  E o usuário digita "minds.com/usuario/post" no campo `input[name="link"]`
  E o usuário clica no botão `button[data-testid="publish-post"]`
  Então uma mensagem de erro `span[data-testid="link-error"]` é exibida com "Formato de link inválido. Use https://www.minds.com/..."
  E o post não é publicado

Cenário: Tentar publicar post sem título (título obrigatório)
  Dado que o usuário está logado e na página de criação de posts "https://app.minds.com/create"
  Quando o usuário digita "Minha descrição" no campo `textarea[name="description"]`
  E o usuário clica no botão `button[data-testid="publish-post"]`
  Então uma mensagem de erro `span[data-testid="title-error"]` é exibida com "Título é obrigatório"
  E o post não é publicado