# Story: Show toast message before launching modal if email verification is required to complete modal actions
# Model: flash | Score: 4.5/10

Funcionalidade: Mensagem Toast para Ações Restritas por Verificação de E-mail

Cenário: Exibir toast e bloquear lançamento de modal quando e-mail não verificado
  Dado que o usuário "usuario@example.com" está logado
  E que o e-mail do usuário não está verificado
  Quando o usuário clica no botão `button[data-testid="trigger-restricted-modal"]`
  Então uma mensagem toast `div[data-testid="toast-message"]` é exibida
  E a mensagem toast `div[data-testid="toast-message"]` exibe o texto "Por favor, verifique seu e-mail para completar esta ação."
  E o modal `div[data-testid="restricted-modal"]` não é exibido

Cenário: Lançar modal diretamente quando e-mail verificado
  Dado que o usuário "usuario@example.com" está logado
  E que o e-mail do usuário está verificado
  Quando o usuário clica no botão `button[data-testid="trigger-restricted-modal"]`
  Então o modal `div[data-testid="restricted-modal"]` é exibido
  E nenhuma mensagem toast `div[data-testid="toast-message"]` é exibida

Cenário: Mensagem toast desaparece automaticamente após tempo limite
  Dado que o usuário "usuario@example.com" está logado
  E que o e-mail do usuário não está verificado
  E que o usuário clica no botão `button[data-testid="trigger-restricted-modal"]`
  E que uma mensagem toast `div[data-testid="toast-message"]` é exibida
  Quando "5" segundos se passam
  Então a mensagem toast `div[data-testid="toast-message"]` não é mais exibida

Cenário: Tentar ação restrita sem estar logado redireciona para login
  Dado que o usuário não está logado
  Quando o usuário clica no botão `button[data-testid="trigger-restricted-modal"]`
  Então o usuário é redirecionado para a página de login "https://www.minds.com/login"
  E nenhuma mensagem toast `div[data-testid="toast-message"]` é exibida
  E o modal `div[data-testid="restricted-modal"]` não é exibido

Cenário: Mensagem toast não bloqueia outras interações na página
  Dado que o usuário "usuario@example.com" está logado
  E que o e-mail do usuário não está verificado
  E que o usuário clica no botão `button[data-testid="trigger-restricted-modal"]`
  E que uma mensagem toast `div[data-testid="toast-message"]` é exibida
  Quando o usuário clica em um elemento diferente `button[data-testid="other-action-button"]`
  Então o toast message `div[data-testid="toast-message"]` ainda é exibido
  E a ação do botão `button[data-testid="other-action-button"]` é processada com sucesso