# Story: Display a modal of mutual subscribers to be displayed when clicking 'other' on `m-channel__mutualSubscriptions`
# Model: flash | Score: 5.2/10

Funcionalidade: Exibição do Modal de Inscritos Mútuos

Cenário: Abrir o modal de inscritos mútuos ao clicar em "Outros"
  Dado que o usuário "alice@exemplo.com" está logado
  E que o usuário está na página do canal "CanalDoBob"
  E que o elemento ".m-channel__mutualSubscriptions" está visível
  Quando clico no botão "Outros" no elemento ".m-channel__mutualSubscriptions"
  Então o modal "div[data-testid='mutual-subscribers-modal']" é exibido
  E o modal "div[data-testid='mutual-subscribers-modal']" exibe o título "Inscritos