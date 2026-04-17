Funcionalidade: Login de Usuário

  Cenário: Login bem-sucedido com credenciais válidas
    Dado que o usuário está na página de login
    Quando preencho o campo "Usuário" com "usuario@exemplo.com"
    E preencho o campo "Senha" com "SenhaSegura123"
    E clico no botão "Entrar"
    Então sou redirecionado para a página "Dashboard"
    E vejo a mensagem de boas-vindas "Olá, Usuário!"

  Cenário: Falha no login com usuário inválido
    Dado que o usuário está na página de login
    Quando preencho o campo "Usuário" com "usuario.invalido@exemplo.com"
    E preencho o campo "Senha" com "SenhaCorreta123"
    E clico no botão "Entrar"
    Então vejo a mensagem de erro "Usuário ou senha inválidos."
    E permaneço na página de login

  Cenário: Falha no login com senha inválida
    Dado que o usuário está na página de login
    Quando preencho o campo "Usuário" com "usuario@exemplo.com"
    E preencho o campo "Senha" com "SenhaErrada123"
    E clico no botão "Entrar"
    Então vejo a mensagem de erro "Usuário ou senha inválidos."
    E permaneço na página de login

  Cenário: Falha no login com usuário e senha vazios
    Dado que o usuário está na página de login
    Quando clico no botão "Entrar"
    Então vejo a mensagem de erro "O campo Usuário é obrigatório."
    E vejo a mensagem de erro "O campo Senha é obrigatório."
    E permaneço na página de login

  Cenário: Falha no login com usuário vazio
    Dado que o usuário está na página de login
    Quando preencho o campo "Senha" com "SenhaValida123"
    E clico no botão "Entrar"
    Então vejo a mensagem de erro "O campo Usuário é obrigatório."
    E permaneço na página de login

  Cenário: Falha no login com senha vazia
    Dado que o usuário está na página de login
    Quando preencho o campo "Usuário" com "usuario@exemplo.com"
    E clico no botão "Entrar"
    Então vejo a mensagem de erro "O campo Senha é obrigatório."
    E permaneço na página de login