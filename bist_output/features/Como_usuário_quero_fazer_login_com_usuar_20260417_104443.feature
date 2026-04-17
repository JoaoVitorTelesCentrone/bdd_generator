Funcionalidade: Login de Usuário

  Cenário: Login bem-sucedido com credenciais válidas
    Dado que estou na página de login
    Quando preencho o campo "Usuário" com "usuario@exemplo.com"
    E preencho o campo "Senha" com "SenhaSegura123"
    E clico no botão "Login"
    Então sou redirecionado para a página "/dashboard"
    E vejo a mensagem de boas-vindas "Bem-vindo, usuario@exemplo.com!"

  Cenário: Tentativa de login com usuário inexistente
    Dado que estou na página de login
    Quando preencho o campo "Usuário" com "usuario.inexistente@exemplo.com"
    E preencho o campo "Senha" com "SenhaSegura123"
    E clico no botão "Login"
    Então vejo a mensagem de erro "Usuário ou senha inválidos."
    E permaneço na página de login "/login"

  Cenário: Tentativa de login com senha incorreta
    Dado que estou na página de login
    Quando preencho o campo "Usuário" com "usuario@exemplo.com"
    E preencho o campo "Senha" com "SenhaInvalida456"
    E clico no botão "Login"
    Então vejo a mensagem de erro "Usuário ou senha inválidos."
    E permaneço na página de login "/login"

  Cenário: Tentativa de login com campo de usuário vazio
    Dado que estou na página de login
    Quando preencho o campo "Usuário" com ""
    E preencho o campo "Senha" com "SenhaSegura123"
    E clico no botão "Login"
    Então vejo a mensagem de validação "O campo Usuário é obrigatório."
    E permaneço na página de login "/login"

  Cenário: Tentativa de login com campo de senha vazio
    Dado que estou na página de login
    Quando preencho o campo "Usuário" com "usuario@exemplo.com"
    E preencho o campo "Senha" com ""
    E clico no botão "Login"
    Então vejo a mensagem de validação "O campo Senha é obrigatório."
    E permaneço na página de login "/login"

  Cenário: Tentativa de login com ambos os campos vazios
    Dado que estou na página de login
    Quando preencho o campo "Usuário" com ""
    E preencho o campo "Senha" com ""
    E clico no botão "Login"
    Então vejo a mensagem de validação "O campo Usuário é obrigatório."
    E vejo a mensagem de validação "O campo Senha é obrigatório."
    E permaneço na página de login "/login"