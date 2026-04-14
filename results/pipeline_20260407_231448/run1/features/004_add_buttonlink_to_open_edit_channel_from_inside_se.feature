# Story: Add button/link to open edit channel from inside settings
# Model: flash | Score: 7.8/10

Cenario: Visibilidade do link "Profile Settings" na seção de configurações
  Dado que o usuário é "Proprietário do Canal" e está logado
  E o canal "Meu Canal de Testes" existe
  Quando o usuário navega para a seção "Settings"
  Então o link "Profile Settings" deve ser exibido

Cenario: Posicionamento do link "Profile Settings" abaixo de "Display Name"
  Dado que o usuário é "Proprietário do Canal" e está logado
  E o canal "Meu Canal de Testes" existe
  E o campo "Display Name" está visível na seção "Settings"
  Quando o usuário acessa a seção "Settings"
  Então o link "Profile Settings" deve estar posicionado diretamente abaixo do campo "Display Name"

Cenario: Abrir modal de edição do canal através do link "Profile Settings"
  Dado que o usuário é "Proprietário do Canal" e está logado
  E o canal "Meu Canal de Testes" existe
  E o link "Profile Settings" está visível na seção "Settings"
  Quando o usuário clica no link "Profile Settings"
  Então um modal de edição do canal deve ser exibido

Cenario: Conteúdo do modal de edição do canal aberto pelo link "Profile Settings"
  Dado que o usuário é "Proprietário do Canal" e está logado
  E o canal "Meu Canal de Testes" existe
  E o link "Profile Settings" está visível na seção "Settings"
  Quando o usuário clica no link "Profile Settings"
  Então o modal deve ser exibido com o título "Editar Canal"
  E o modal deve conter o campo de texto "Nome do Canal"
  E o modal deve conter o botão "Salvar"

Cenario: Conteúdo do modal de edição do canal aberto pelo botão "Edit Channel"
  Dado que o usuário é "Proprietário do Canal" e está logado
  E o canal "Meu Canal de Testes" existe
  E o botão "Edit Channel" está visível na página do canal
  Quando o usuário clica no botão "Edit Channel"
  Então o modal deve ser exibido com o título "Editar Canal"
  E o modal deve conter o campo de texto "Nome do Canal"
  E o modal deve conter o botão "Salvar"