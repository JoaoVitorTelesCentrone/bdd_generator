# Story: Email: Automate bring your friends post for 7 days after registration
# Model: flash | Score: 6.2/10

Funcionalidade: Envio de E-mail de Indicação de Amigos 7 Dias Após o Registro

Cenário: Usuário Elegível Recebe E-mail de Indicação
  Dado que o usuário "usuario_elegivel@teste.com" registrou sua conta há "7 dias e 1 minuto"
  E que o usuário "usuario_elegivel@teste.com" verificou seu e-mail há "6 dias"
  E que o usuário "usuario_elegivel@teste.com" não realizou nenhuma indicação
  Quando o sistema processa o job de envio de e-mails
  Então o sistema envia um e-mail para "usuario_elegivel@teste.com"
  E o e-mail recebido deve ter o assunto "Friends help friends get off big tech"
  E o e-mail recebido deve conter um preheader
  E o e-mail recebido deve conter um call-to-action para indicar amigos

Cenário: Não Enviar E-mail Quando Usuário Não Verificou o E-mail
  Dado que o usuário "nao_verificado@teste.com" registrou sua conta há "7 dias e 1 minuto"
  E que o usuário "nao_verificado@teste.com" não verificou seu e-mail
  E que o usuário "nao_verificado@teste.com" não realizou nenhuma indicação
  Quando o sistema processa o job de envio de e-mails
  Então o sistema não envia nenhum e-mail para "nao_verificado@teste.com"

Cenário: Não Enviar E-mail Quando Usuário Já Indicou Amigo Antes do 7º Dia
  Dado que o usuário "ja_indicou@teste.com" registrou sua conta há "7 dias e 1 minuto"
  E que o usuário "ja_indicou@teste.com" verificou seu e-mail há "6 dias"
  E que o usuário "ja_indicou@teste.com" realizou uma indicação há "5 dias"
  Quando o sistema processa o job de envio de e-mails
  Então o sistema não envia nenhum e-mail para "ja_indicou@teste.com"

Cenário: Não Enviar E-mail Quando Menos de 7 Dias Passaram Desde o Registro
  Dado que o usuário "menos_7dias@teste.com" registrou sua conta há "6 dias e 23 horas"
  E que o usuário "menos_7dias@teste.com" verificou seu e-mail há "6 dias"
  E que o usuário "menos_7dias@teste.com" não realizou nenhuma indicação
  Quando o sistema processa o job de envio de e-mails
  Então o sistema não envia nenhum e-mail para "menos_7dias@teste.com"

Cenário: Não Enviar E-mail Quando Usuário Deletou a Conta Antes do 7º Dia
  Dado que o usuário "conta_deletada@teste.com" registrou sua conta há "7 dias e 1 minuto"
  E que o usuário "conta_deletada@teste.com" verificou seu e-mail há "6 dias"
  E que o usuário "conta_deletada@teste.com" deletou sua conta há "4 dias"
  Quando o sistema processa o job de envio de e-mails
  Então o sistema não