# Story: Email: Automate welcome post for 1 day after registration
# Model: flash | Score: 7.4/10

Funcionalidade: Automação de Email de Boas-Vindas

Cenário: Usuário recebe email de boas-vindas um dia após registro e verificação
  Dado que o usuário "novo.usuario@example.com" se registrou com o username "NovoUser"
  E que o email "novo.usuario@example.com" foi verificado com sucesso
  Quando 24 horas se passam desde a verificação do email
  Então o sistema envia um email para "novo.usuario@example.com"
  E o email recebido possui o assunto "Welcome to Minds, NovoUser"
  E o email recebido possui o preheader "You've taken the first step. Here's what's next."
  E o email recebido contém o texto "Thanks for joining Minds! H"

Cenário: Usuário não recebe email de boas-vindas se o email não foi verificado
  Dado que o usuário "nao.verificado@example.com" se registrou com o username "NaoVerificado"
  E que o email "nao.verificado@example.com" não foi verificado
  Quando 24 horas se passam desde o registro do usuário
  Então o sistema não envia um email de boas-vindas para "nao.verificado@example.com"

Cenário: Usuário não recebe email de boas-vindas antes de 24 horas após verificação
  Dado que o usuário "verificado.recente@example.com" se registrou com o username "RecenteUser"
  E que o email "verificado.recente@example.com" foi verificado com sucesso
  Quando 12 horas se passam desde a verificação do email
  Então o sistema não envia um email de boas-vindas para "verificado.recente@example.com"

Cenário: Email de boas-vindas é enviado apenas uma vez por usuário
  Dado que o usuário "unico.envio@example.com" se registrou com o username "UnicoEnvio"
  E que o email "unico.envio@example.com" foi verificado com sucesso
  E que 24 horas se passaram desde a verificação do email
  E que o sistema enviou o email de boas-vindas para "unico.envio@example.com"
  Quando 48 horas se passam desde a verificação do email
  Então o sistema não envia um segundo email de boas-vindas para "unico.envio@example.com"