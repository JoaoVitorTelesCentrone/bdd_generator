# Story: Email: Automate bring your friends post for 7 days after registration
# Model: flash | Score: 6.0/10

Funcionalidade: Automação de E-mail de Indicação de Amigos

Cenário: Envio bem-sucedido de e-mail de indicação para usuário elegível
  Dado que o usuário "usuario_elegivel@exemplo.com" está registrado há "7" dias
  E que o e-mail do usuário "usuario_elegivel@exemplo.com" está verificado
  E que o usuário "usuario_elegivel@exemplo.com" nunca realizou uma indicação
  Quando o sistema executa o job de envio de e-mails de indicação
  Então o usuário "usuario_elegivel@exemplo.com" recebe um e-mail
  E o e-mail exibe o assunto "Friends help friends get off big tech"

Cenário: Não envio de e-mail para usuário com menos de 7 dias de registro
  Dado que o usuário "usuario_novo@exemplo.com" está registrado há "3" dias
  E que o e-mail do usuário "usuario_novo@exemplo.com" está verificado
  E que o usuário "usuario_novo@exemplo.com" nunca realizou uma indicação
  Quando o sistema executa o job de envio de e-mails de indicação
  Então o usuário "usuario_novo@exemplo.com" não recebe um e-mail

Cenário: Não envio de e-mail para usuário com e-mail não verificado
  Dado que o usuário "usuario_nao_verificado@exemplo.com" está registrado há "7" dias
  E que o e-mail do usuário "usuario_nao_verificado@exemplo.com" não está verificado
  E que o usuário "usuario_nao_verificado@exemplo.com" nunca realizou uma indicação
  Quando o sistema executa o job de envio de e-mails de indicação
  Então o usuário "usuario_nao_verificado@exemplo.com" não recebe um e-mail

Cenário: Não envio de e-mail para usuário que já realizou uma indicação
  Dado que o usuário "usuario_ja_indicou@exemplo.com" está registrado há "7" dias
  E que o e-mail do usuário "usuario_ja_indicou@exemplo.com" está verificado
  E que o usuário "usuario_ja_indicou@exemplo.com" já realizou uma indicação
  Quando o sistema executa o job de envio de e-mails de indicação
  Então o usuário "usuario_ja_indicou@exemplo.com" não recebe um e-mail