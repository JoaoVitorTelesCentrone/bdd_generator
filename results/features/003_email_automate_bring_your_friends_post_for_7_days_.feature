# Story: Email: Automate bring your friends post for 7 days after registration
# Model: flash | Score: 6.0/10

Funcionalidade: Automação de Email de Referência de Amigos

Cenário: Usuário recebe email de referência após 7 dias de registro e verificação
  Dado que o usuário "amigo.novo@example.com" se registrou com o username "AmigoNovo"
  E que o email "amigo.novo@example.com" foi verificado com sucesso
  E que o usuário "amigo.novo@example.com" não referiu nenhum amigo
  Quando 7 dias se passam desde a verificação do email
  Então o sistema envia um email para "amigo.novo@example.com"
  E o email recebido possui o assunto "Friends help friends get off big tech"
  E o email recebido tem o remetente "no-reply@minds.com"

Cenário: Usuário não recebe email de referência se o email não foi verificado
  Dado que o usuário "nao.verificado@example.com" se registrou com o username "NaoVerificado"
  E que o email "nao.verificado@example.com" não foi verificado
  Quando 7 dias se passam desde o registro do usuário
  Então o sistema não envia um email de referência para "nao.verificado@example.com"

Cenário: Usuário não recebe email de referência antes de 7 dias após verificação
  Dado que o usuário "verificado.recente@example.com" se registrou com o username "RecenteUser"
  E que o email "verificado.recente@example.com" foi verificado com sucesso
  E que o usuário "verificado.recente@example.com" não referiu nenhum amigo
  Quando 6 dias se passam desde a verificação do email
  Então o sistema não envia um email de referência para "verificado.recente@example.com"

Cenário: Usuário não recebe email de referência se já referiu alguém
  Dado que o usuário "ja.referiu@example.com" se registrou com o username "JaReferiu"
  E que o email "ja.referiu@example.com" foi verificado com sucesso
  E que o usuário "ja.referiu@example.com" já referiu um amigo
  Quando 7 dias se passam desde a verificação do email
  Então o sistema não envia um email de referência para "ja.referiu@example.com"

Cenário: Email de referência é enviado apenas uma vez por usuário
  Dado que o usuário "unico.envio@example.com" se registrou com o username "UnicoEnvio"
  E que o email "unico.envio@example.com" foi verificado com sucesso
  E que o usuário "unico.envio@example.com" não referiu nenhum amigo
  E que 7 dias se passaram desde a verificação do email
  E que o sistema enviou o email de referência para "unico.envio@example.com"
  Quando 14 dias se passam desde a verificação do email
  Então o sistema não envia um segundo email de referência para "unico.envio@example.com"