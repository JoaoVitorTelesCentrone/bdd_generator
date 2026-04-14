# Story: Email: Automate bring your friends post for 7 days after registration
# Model: flash | Score: 3.1/10

Funcionalidade: Envio de Email de Indicação de Amigos

  Cenário: Usuário elegível recebe o email de indicação após 7 dias
    Dado que o usuário "novo.usuario@exemplo.com" está registrado
    E que o email "novo.usuario@exemplo.com" foi verificado
    E que o usuário "novo.usuario@exemplo.com" não fez nenhuma indicação
    E que 7 dias se passaram desde o registro
    Quando o sistema processa o agendamento de emails
    Então o usuário "novo.usuario@exemplo.com" recebe um email
    E o assunto do email é "Friends help friends get off big tech"

  Cenário: Usuário com email não verificado não recebe o email de indicação
    Dado que o usuário "nao.verificado@exemplo.com" está registrado
    E que o email "nao.verificado@exemplo.com" NÃO foi verificado
    E que o usuário "nao.verificado@exemplo.com" não fez nenhuma indicação
    E que