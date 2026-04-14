# Story: Discovery: Implement channel recommendations component - web
# Model: flash | Score: 7.1/10

Funcionalidade: Componente de Recomendações de Canais na Página Discovery

Cenário: Exibição inicial do componente de recomendações na página Discovery
  Dado que o usuário está na página inicial do Minds
  Quando o usuário acessa a URL "https://www.minds.com/discovery/top"
  Então o componente "Suggested Channels" deve ser exibido
  E o título "Suggested Channels" deve ser visível
  E pelo menos "1" cartão de canal deve aparecer

Cenário: Estrutura visual de um cartão de canal recomendado
  Dado que o usuário está na página "https://www.minds.com/discovery/top"
  E o componente "Suggested Channels" está visível
  Quando o usuário visualiza o primeiro cartão de canal recomendado
  Então o cartão deve exibir uma imagem de avatar
  E o cartão deve exibir um "nome de canal"
  E o cartão deve exibir um botão "Follow"

Cenário: Seguir um canal a partir do componente de recomendações
  Dado que o usuário está logado na página "https://www.minds.com/discovery/top"
  E o componente "Suggested Channels" está visível
  E o primeiro canal recomendado não está sendo seguido
  Quando o usuário clica no botão "Follow" do primeiro canal
  Então o botão "Follow" deve mudar para "Following"
  E o status do canal deve indicar que está sendo seguido

Cenário: Interação de rolagem horizontal com múltiplos canais
  Dado que o usuário está na página "https://www.minds.com/discovery/top"
  E o componente "Suggested Channels" está visível
  E existem mais de "5" canais recomendados
  Quando o usuário tenta rolar horizontalmente o componente
  Então novos cartões de canal devem aparecer
  E os cartões previamente visíveis devem desaparecer ou se mover para fora da tela