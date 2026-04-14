# Story: Update interest tag options presented during onboarding
# Model: flash | Score: 4.8/10

Funcionalidade: Atualização das Opções de Tags de Interesse no Onboarding

Cenário: Novo usuário visualiza opções de tags atualizadas no onboarding
  Dado que um novo usuário inicia o processo de cadastro
  Quando o usuário acessa a página `https://app.example.com/onboarding/interesses`
  Então a seção `#tag-options` exibe a tag "Inteligência Artificial"
  E a seção `#tag-options` exibe a tag "Realidade Virtual"
  E a seção `#tag-options` exibe a tag "Cibersegurança"
  E o botão `#btn-prosseguir` está desabilitado

Cenário: Usuário seleciona tags atualizadas e avança no onboarding
  Dado que um novo usuário está na página `https://app.example.com/onboarding/interesses`
  E a página exibe as tags "Inteligência Artificial", "Realidade Virtual"
  Quando o usuário clica no checkbox `input[value="Inteligência Artificial"]`
  E o usuário clica no checkbox `input[value="Realidade Virtual"]`
  E o usuário clica no botão `#btn-prosseguir`
  Então o usuário é redirecionado para `https://app.example.com/onboarding/perfil`

Cenário: Tags de interesse descontinuadas não são exibidas no onboarding
  Dado que um novo usuário inicia o processo de cadastro
  Quando o usuário acessa a página `https://app.example.com/onboarding/interesses`
  Então a seção `#tag-options` não contém a tag "Blockchain Legado"
  E a seção `#tag-options` não contém a tag "Realidade Aumentada Antiga"

Cenário: Usuário tenta exceder o limite de seleção de tags
  Dado que um novo usuário está na página `https://app.example.com/onboarding/interesses`
  E o limite máximo de tags selecionáveis é "2"
  E a página exibe as tags "Tecnologia", "Design", "Marketing"
  Quando o usuário clica no checkbox `input[value="Tecnologia"]`
  E o usuário clica no checkbox `input[value="Design"]`
  E o usuário tenta clicar no checkbox `input[value="Marketing"]`
  Então o checkbox `input[value="Marketing"]` deve estar desabilitado
  E a mensagem `.error-message` exibe "Máximo de 2 tags selecionadas"

Cenário: Tags de interesse são apresentadas em ordem alfabética
  Dado que um novo usuário inicia o processo de cadastro
  Quando o usuário acessa a página `https://app.example.com/onboarding/interesses`
  Então a lista `#tag-options .tag-item` exibe "Cibersegurança" como primeiro item
  E a lista `#tag-options .tag-item` exibe "Inteligência Artificial" como segundo item
  E a lista `#tag-options .tag-item` exibe "Realidade Virtual" como terceiro item