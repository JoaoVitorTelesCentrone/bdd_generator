# Story: (feat): change 'from' email address to 'no-reply@minds.com'
# Model: flash | Score: 7.6/10

Funcionalidade: Padronização do Endereço de Email do Remetente

Cenário: Email de Redefinição de Senha enviado por "no-reply@minds.com"
  Dado que o usuário "alice@exemplo.com" está registrado e com conta ativa
  Quando o usuário solicita a redefinição de senha na página "https://app.minds.com/esqueci-senha"
  Então o usuário "alice@exemplo.com" recebe um email na sua caixa de entrada
  E o email recebido tem o remetente "no-reply@minds.com"
  E o email recebido não tem o remetente "info@minds.com"

Cenário: Email de Confirmação de Cadastro enviado por "no-reply@minds.com"
  Dado que o usuário "bob@exemplo.com" realiza um novo cadastro com email válido
  Quando o usuário clica no botão `button[data-testid="confirmar-cadastro"]` na página "https://app.minds.com/cadastro"
  Então o usuário "bob@exemplo.com" recebe um email na sua caixa de entrada
  E o email recebido tem o remetente "no-reply@minds.com"
  E o email recebido não tem o remetente "info@minds.com"

Cenário: Email de Notificação de Interação enviado por "no-reply@minds.com"
  Dado que o usuário "carol@exemplo.com" possui uma postagem publicada
  E que o usuário "dave@exemplo.com" comenta na postagem de "carol@exemplo.com"
  Quando o sistema envia a notificação de novo comentário para o autor
  Então o usuário "carol@exemplo.com" recebe um email na sua caixa de entrada
  E o email recebido tem o remetente "no-reply@minds.com"
  E o email recebido não tem o remetente "info@minds.com"

Cenário: Email de Confirmação de Contato enviado por "no-reply@minds.com"
  Dado que um usuário "eva@exemplo.com" preenche o formulário de contato
  Quando o usuário envia o formulário na página "https://app.minds.com/contato"
  Então o usuário "eva@exemplo.com" recebe um email de confirmação na sua caixa de entrada
  E o email recebido tem o remetente "no-reply@minds.com"
  E o email recebido não tem o remetente "info@minds.com"