# Story: Include react native image picker library and enable cropping for Channel Avatar
# Model: flash | Score: 7.4/10

Funcionalidade: Gerenciamento do Avatar do Canal com Recorte Circular

  Cenário: Atualizar avatar do canal com uma imagem da galeria e recorte circular
    Dado que o usuário está logado e na tela de edição do perfil do canal "Meu Canal"
    Quando o usuário clica no botão `button[data-testid="edit-avatar"]`
    E o usuário seleciona a opção "Escolher da Galeria" no menu de seleção
    E o usuário seleciona a imagem "avatar_galeria.jpg" na galeria do dispositivo
    E a interface de recorte é exibida com uma máscara circular `view[data-testid="crop-mask-circle"]`
    E o usuário ajusta a imagem dentro da área de recorte
    E o usuário clica no botão `button[data-testid="confirm-crop"]`
    Então o avatar do canal `image[data-testid="channel-avatar"]` é atualizado com a imagem recortada
    E a imagem do avatar `image[data-testid="channel-avatar"]` tem formato circular

  Cenário: Atualizar avatar do canal com uma imagem da câmera e recorte circular
    Dado que o usuário está logado e na tela de edição do perfil do canal "Meu Canal"
    Quando o usuário clica no botão `button[data-testid="edit-avatar"]`
    E o usuário seleciona a opção "Tirar Foto" no menu de seleção
    E o usuário tira uma foto com a câmera do dispositivo
    E a interface de recorte é exibida com uma máscara circular `view[data-testid="crop-mask-circle"]`
    E o usuário ajusta a imagem dentro da área de recorte
    E o usuário clica no botão `button[data-testid="confirm-crop"]`
    Então o avatar do canal `image[data-testid="channel-avatar"]` é atualizado com a imagem recortada
    E a imagem do avatar `image[data-testid="channel-avatar"]` tem formato circular

  Cenário: Cancelar a seleção da imagem e manter o avatar existente
    Dado que o usuário está logado e na tela de edição do perfil do canal "Meu Canal"
    E que o avatar do canal `image[data-testid="channel-avatar"]` exibe a imagem "avatar_original.png"
    Quando o usuário clica no botão `button[data-testid="edit-avatar"]`
    E o usuário seleciona a opção "Escolher da Galeria" no menu de seleção
    E o usuário clica no botão `button[data-testid="cancel-selection"]` na tela de seleção de imagem
    Então o avatar do canal `image[data-testid="channel-avatar"]` ainda exibe a imagem "avatar_original.png"
    E a interface de seleção de imagem não é mais exibida

  Cenário: Cancelar o recorte da imagem e manter o avatar existente
    Dado que o usuário está logado e na tela de edição do perfil do canal "Meu Canal"
    E que o avatar do canal `image[data-testid="channel-avatar"]` exibe a imagem "avatar_original.png"
    Quando o usuário clica no botão `button[data-testid="edit-avatar"]`
    E o usuário seleciona a opção "Escolher da Galeria" no menu de seleção
    E o usuário seleciona a imagem "nova_imagem_para_recorte.jpg" na galeria do dispositivo
    E a interface de recorte é exibida com uma máscara circular `view[data-testid="crop-mask-circle"]`
    E o usuário clica no botão `button[data-testid="cancel-crop"]`
    Então o avatar do canal `image[data-testid="channel-avatar"]` ainda exibe a imagem "avatar_original.png"
    E a interface de recorte de imagem não é mais exibida

  Cenário: Visualizar máscara de recorte circular e controles ao selecionar imagem
    Dado que o usuário está logado e na tela de edição do perfil do canal "Meu Canal"
    Quando o usuário clica no botão `button[data-testid="edit-avatar"]`
    E o usuário seleciona a opção "Escolher da Galeria" no menu de seleção
    E o usuário seleciona a imagem "imagem_teste.jpg" na galeria do dispositivo
    Então a interface de recorte é exibida
    E uma máscara de recorte com formato circular `view[data-testid="crop-mask-circle"]` é visível
    E os controles de ajuste `view[data-testid="crop-controls"]` são exibidos

  Cenário: Mensagem de erro ao tentar selecionar um arquivo inválido
    Dado que o usuário está logado e na tela de edição do perfil do canal "Meu Canal"
    Quando o usuário clica no botão `button[data-testid="edit-avatar"]`
    E o usuário seleciona a opção "Escolher da Galeria" no menu de seleção
    E o usuário tenta selecionar o arquivo "documento.pdf" na galeria do dispositivo
    Então uma mensagem de erro `text[data-testid="error-message"]` com "Formato de arquivo inválido" é exibida
    E o avatar do canal `image[data-testid="channel-avatar"]` permanece inalterado

  C