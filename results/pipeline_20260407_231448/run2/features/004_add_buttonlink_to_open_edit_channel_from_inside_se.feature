# Story: Add button/link to open edit channel from inside settings
# Model: flash | Score: 5.7/10

Funcionalidade: Gerenciamento de Configurações de Canal

Cenário: Exibição e posicionamento do item "Configurações de Perfil" nas configurações do canal
  Dado que um usuário "admin@exemplo.com" está logado
  E que o canal "canal-de-teste-123" possui o nome de exibição "Meu Canal Legal"
  Quando o usuário navega para a tela de "Configurações" do canal "canal-de-teste-123"
  Então o item "Configurações de Perfil" é exibido
  E o item "Configurações de Perfil" possui o texto "Configurações de Perfil"
  E o item "Configurações de Perfil" está posicionado abaixo do item "Nome de Exibição"

Cenário: Abertura e validação do modal de edição de canal a partir do item "Configurações de Perfil"
  Dado que um usuário "admin@exemplo.com" está logado
  E que o canal "canal-de-teste-123" existe
  Quando o usuário navega para a tela de "Configurações" do canal "canal-de-teste-123"
  E clica no item "Configurações de Perfil"
  Então o modal de edição de canal é exibido
  E o modal exibido possui o título "Editar Canal"
  E o modal exibido contém o campo "Nome de Exibição"
  E o modal exibido contém o campo "Descrição"
  E o botão "Salvar" é exibido no modal
  E o botão "Cancelar" é exibido no modal