# Story: (bug): Images Library Has Disappeared
# Model: flash | Score: 5.9/10

Funcionalidade: Biblioteca de Imagens do Canal

Cenário: A biblioteca de imagens reaparece na barra lateral do canal
  Dado que estou logado como "usuario_autenticado"
  E que existe um canal com "3" imagens carregadas
  Quando acesso a URL "https://app.exemplo.com/canal/meu-canal-com-imagens"
  Então vejo a seção ".image-library-section" na barra lateral esquerda
  E vejo o título "Biblioteca de Imagens" no ".image-library-section h2"
  E vejo "3" miniaturas de imagens em ".image-library-section .thumbnail"

Cenário: A biblioteca de imagens é exibida abaixo da biografia do canal
  Dado que estou logado como "usuario_autenticado"
  E que existe um canal com uma biografia e "1" imagem
  Quando acesso a URL "https://app.exemplo.com/canal/meu-canal-com-bio"
  Então a seção ".image-library-section" aparece abaixo de "#channel-bio"

Cenário: A biblioteca de imagens é exibida acima da biblioteca de vídeos
  Dado que estou logado como "usuario_autenticado"
  E que existe um canal com "1" imagem e "1" vídeo
  Quando acesso a URL "https://app.exemplo.com/canal/meu-canal-com-videos"
  Então a seção ".image-library-section" aparece acima de ".video-library-section"

Cenário: A biblioteca de imagens exibe mensagem de vazio quando não há imagens
  Dado que estou logado como "usuario_autenticado"
  E que existe um canal sem imagens carregadas
  Quando acesso a URL "https://app.exemplo.com/canal/meu-canal-vazio"
  Então vejo a seção ".image-library-section" na barra lateral
  E vejo a mensagem "Nenhuma imagem carregada" em ".image-library-section .empty-message"

Cenário: Usuário pode navegar pelas imagens na biblioteca
  Dado que estou logado como "usuario_autenticado"
  E que existe um canal com "5" imagens carregadas
  Quando acesso a URL "https://app.exemplo.com/canal/meu-canal-com-5-imagens"
  E clico na miniatura da imagem ".image-library-section .thumbnail:nth-child(1)"
  Então vejo a imagem em tamanho "grande" no modal ".image-viewer-modal"
  E vejo o botão "Próxima imagem" em ".image-viewer-modal .next-button"