Funcionalidade: Fazer login
  Como um usuário
  Quero fazer login para acessar minha conta

  Cenário: Caminho feliz - Login bem-sucedido
    Dado que estou na página de login "https://app.exemplo.com/login"
    Quando preencho o campo de email com "admin@empresa.com"
    E preencho o campo de senha com "Senha@123"
    E clico no botão "Entrar"
    Então vejo a página de dashboard do usuário

  Cenário: Login com email inválido
    Dado que estou na página de login "https://app.exemplo.com/login"
    Quando preencho o campo de email com "usuario_invalido@empresa.com"
    E preencho o campo de senha com "Senha@123"
    E clico no botão "Entrar"
    Então vejo a mensagem de erro "Email ou senha inválidos"

  Cenário: Login com senha inválida
    Dado que estou na página de login "https://app.exemplo.com/login"
    Quando preencho o campo de email com "admin@empresa.com"
    E preencho o campo de senha com "senha_invalida"
    E clico no botão "Entrar"
    Então vejo a mensagem de erro "Email ou senha inválidos"

  Cenário: Login com campos vazios
    Dado que estou na página de login "https://app.exemplo.com/login"
    Quando clico no botão "Entrar"
    Então vejo a mensagem de erro "Preencha os campos de email e senha"

  Cenário: Login com email em branco
    Dado que estou na página de login "https://app.exemplo.com/login"
    Quando preencho o campo de senha com "Senha@123"
    E clico no botão "Entrar"
    Então vejo a mensagem de erro "Preencha o campo de email"

  Cenário: Login com senha em branco
    Dado que estou na página de login "https://app.exemplo.com/login"
    Quando preencho o campo de email com "admin@empresa.com"
    E clico no botão "Entrar"
    Então vejo a mensagem de erro "Preencha o campo de senha"

  Cenário: Login com múltiplos espaços no email
    Dado que estou na página de login "https://app.exemplo.com/login"
    Quando preencho o campo de email com "   admin@empresa.com   "
    E preencho o campo de senha com "Senha@123"
    E clico no botão "Entrar"
    Então vejo a página de dashboard do usuário

  Cenário: Login com caracteres especiais no email
    Dado que estou na página de login "https://app.exemplo.com/login"
    Quando preencho o campo de email com "admin!@empresa.com"
    E preencho o campo de senha com "Senha@123"
    E clio no botão "Entrar"
    Então vejo a mensagem de erro "Email inválido"