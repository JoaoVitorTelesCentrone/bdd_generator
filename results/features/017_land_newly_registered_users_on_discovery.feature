# Story: Land newly-registered users on Discovery
# Model: flash | Score: 6.0/10

Funcionalidade: Redirecionamento de Novos Usuários para a Página Descobrir

Cenário: Usuário recém-registrado com verificação de email é redirecionado para a página Descobrir
  Dado que um usuário não registrado está na página "/cadastro"
  E o usuário "novo.usuario@example.com" se registra com a senha "SenhaSegura123" e username "NovoUser"
  E o email "novo.usuario@example.com" é verificado com sucesso
  Quando o usuário "novo.usuario@example.com" realiza o primeiro login na página "/login"
  Então o usuário é redirecionado para a página "/discovery"
  E o título `h1[data-testid="page-title"]` exibe "Descobrir"
  E a seção de feeds `section[data-testid="discovery-feed"]` é exibida

Cenário: Usuário existente não é redirecionado para a página Descobrir após login
  Dado que o usuário "existente@example.com" está registrado e com conta ativa
  E o usuário já acessou a plataforma anteriormente
  Quando o usuário "existente@example.com" realiza o login na página "/login"
  Então o usuário é redirecionado para a página "/feed"
  E o título `h1[data-testid="page-title"]` exibe "Meu Feed"
  E a página "/discovery" não é exibida

Cenário: Usuário recém-registrado que faz login novamente não é redirecionado para a página Descobrir
  Dado que o usuário "recente@example.com" se registrou, verificou o email e realizou o primeiro login
  E o usuário "recente@example.com" acessou a página "/discovery"
  E o usuário realiza o logout da plataforma
  Quando o usuário "recente@example.com" realiza um novo login na página "/login"
  Então o usuário é redirecionado para a página "/feed"
  E o título `h1[data-testid="page-title"]` exibe "Meu Feed"
  E a página "/discovery" não é exibida