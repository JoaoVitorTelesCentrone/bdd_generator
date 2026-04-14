# Story: (bug): Link previews disappear when editing a status post
# Model: flash | Score: 5.6/10

Funcionalidade: Edição de Posts de Status com Preview de Link

Cenário: Preview de link desaparece após edição de texto em post de status
  Dado que o usuário "usuario@exemplo.com" está logado
  E que um post de status com ID "101" foi criado com o texto "Meu post original com link: https://exemplo.com"
  E que o post com ID "101" exibe o preview do link "https://exemplo.com" no elemento `.link-preview[data-post-id='101'][data-link='https://exemplo.com']`
  Quando o usuário clica no menu de opções do post com ID "101" no elemento `.post-