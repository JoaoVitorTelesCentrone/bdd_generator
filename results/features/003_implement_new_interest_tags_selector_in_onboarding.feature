# Story: Implement new interest tags selector in onboarding
# Model: flash | Score: 4.3/10

Funcionalidade: Seleção de Tags de Interesse no Onboarding

Cenário: Exibição inicial do seletor de tags no onboarding
  Dado que o usuário está iniciando o fluxo de onboarding
  Quando o usuário acessa a página de "Interesses" em "https://app.exemplo.com/onboarding/interesses"
  Então o título "Selecione seus interesses" é exibido no elemento `h2.onboarding-title`
  E a descrição "Escolha pelo menos 2 para personalizar seu feed" é exibida no elemento `p.onboarding-description`
  E as tags "Tecnologia", "Esportes", "Culinária" são exibidas no elemento `div.tags-container`
  E o botão "Continuar" (`button[data-testid="onboarding-continue"]`) está desabilitado

Cenário: Seleção de tags e ativação do botão de continuar
  Dado que o usuário está na página de "Interesses" em "https://app.exemplo.com/onboarding/interesses"
  E que o botão "Continuar" (`button[data-testid="onboarding-continue"]`) está desabilitado
  Quando o usuário clica na tag "Tecnologia" (`button[data-tag-id="tecnologia"]`)
  E o usuário clica na tag "Esportes" (`button[data-tag-id="esportes"]`)
  Então a tag "Tecnologia" possui a classe CSS "selected"
  E a tag "Esportes" possui a classe CSS "selected"
  E o botão "Continuar" (`button[data-testid="onboarding-continue"]`) está habilitado

Cenário: Desseleção de tags previamente selecionadas
  Dado que o usuário está na página de "Interesses" em "https://app.exemplo.com/onboarding/interesses"
  E que as tags "Tecnologia" e "Esportes" estão selecionadas
  E que o botão "Continuar" (`button[data-testid="onboarding-continue"]`) está habilitado
  Quando o usuário clica na tag "Esportes" (`button[data-tag-id="esportes"]`)
  Então a tag "Esportes" não possui a classe CSS "selected"
  E a tag "Tecnologia" ainda possui a classe CSS "selected"
  E o botão "Continuar" (`button[data-testid="onboarding-continue"]`) permanece habilitado

Cenário: Tentativa de avançar com menos tags que o mínimo requerido
  Dado que o usuário está na página de "Interesses" em "https://app.exemplo.com/onboarding/interesses"
  E que o mínimo de tags para continuar é "2"
  E que apenas a tag "Música" (`button[data-tag-id="musica"]`) está selecionada
  Quando o usuário tenta clicar no botão "Continuar" (`button[data-testid="onboarding-continue"]`)
  Então o botão "Continuar" (`button[data-testid="onboarding-continue"]`) está desabilitado
  E uma mensagem de erro "Selecione no mínimo 2 interesses" é exibida no elemento `.error-message`

Cenário: Sucesso ao selecionar o número mínimo de tags e avançar
  Dado que o usuário está na página de "Interesses" em "https://app.exemplo.com/onboarding/interesses"
  E que o mínimo de tags para continuar é "2"
  Quando o usuário clica na tag "Arte" (`button[data-tag-id="arte"]`)
  E o usuário clica na tag "Fotografia" (`button[data-tag-id="fotografia"]`)
  E o usuário clica no botão "Continuar" (`button[data-testid="onboarding-continue"]`)
  Então o usuário é redirecionado para a URL "https://app.exemplo.com/onboarding/perfil"
  E o sistema registra as tags "Arte" e "Fotografia" para o usuário

Cenário: Impedir seleção de tags além do limite máximo
  Dado que o usuário está na página de "Interesses" em "https://app.exemplo.com/onboarding/interesses"
  E que o número máximo de tags permitidas é "5