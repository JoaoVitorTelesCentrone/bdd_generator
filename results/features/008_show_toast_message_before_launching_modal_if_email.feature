# Story: Show toast message before launching modal if email verification is required to complete modal actions
# Model: flash | Score: 5.3/10

Funcionalidade: Exibir mensagem toast antes de abrir modal se a verificação de email for necessária

  Cenário: Usuário não verificado tenta abrir modal com ação restrita
    Dado que o usuário "nao_verificado@exemplo.com" está logado
    E que o email "nao_verificado@exemplo.com" não está verificado
    E que a ação do botão "#btn-abrir-modal-acao" requer verificação de email
    Quando eu clico no botão "#btn-abrir-modal-acao"
    Então eu vejo o toast ".toast-message-warning"
    E que o modal "#modal-confirmacao" não é exibido

  Cenário: Usuário verificado abre modal com ação restrita
    Dado que o usuário "verificado@exemplo.com" está logado
    E que o email "verificado@exemplo.com" está verificado
    E que a ação do botão "#btn-abrir-modal-acao" requer verificação de email
    Quando eu clico no botão "#btn-abrir-modal-acao"
    Então eu não vejo o toast ".toast-message-warning"
    E que o modal "#modal-confirmacao" é exibido

  Cenário: Conteúdo específico da mensagem toast para email não verificado
    Dado que o usuário "email_pendente@exemplo.com" está logado
    E que o email "email_pendente@exemplo.com" não está verificado
    E que a ação do link "[data-testid='link-config-avancada']" requer verificação de email
    Quando eu clico no link "[data-testid='link-config-avancada']"
    Então o toast ".toast-message-warning" exibe "Verifique seu email para esta ação"
    E que o modal "#modal-config-avancada" não aparece

  Cenário: Toast de verificação aparece e desaparece automaticamente
    Dado que o usuário "teste_toast@exemplo.com" está logado
    E que o email "teste_toast@exemplo.com" não está verificado
    E que a ação do botão "[data-testid='btn-publicar']" requer verificação de email
    Quando eu clico no botão "[data-testid='btn-publicar']"
    Então eu vejo o toast ".toast-message-warning"
    E que o toast ".toast-message-warning" desaparece após 5 segundos
    E que o modal "#modal-publicacao" não é exibido