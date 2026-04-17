Funcionalidade: Login de Usuário

  Cenário: Login bem-sucedido com credenciais válidas
    Dado que o usuário está na página de "Login"
    Quando o usuário preenche o campo "Usuário" com "usuario@exemplo.com"
    E o usuário preenche o campo "Senha" com "Senha123!"
    E o usuário clica no botão "Entrar"
    Então o usuário é redirecionado para a página "Dashboard"
    E o sistema exibe a mensagem "Login realizado com sucesso"

  Cenário: Tentativa de login com usuário inválido
    Dado que o usuário está na página de "Login"
    Quando o usuário preenche o campo "Usuário" com "naoexiste@exemplo.com"
    E o usuário preenche o campo "Senha" com "Senha123!"
    E o usuário clica no botão "Entrar"
    Então o sistema exibe a mensagem de erro "Usuário ou senha inválidos"
    E o usuário permanece na página de "Login"

  Cenário: Tentativa de login com senha inválida
    Dado que o usuário está na página de "Login"
    Quando o usuário preenche o campo "Usuário" com "usuario@exemplo.com"
    E o usuário preenche o campo "Senha" com "SenhaIncorreta!"
    E o usuário clica no botão "Entrar"
    Então o sistema exibe a mensagem de erro "Usuário ou senha inválidos"
    E o usuário permanece na página de "Login"

  Cenário: Tentativa de login com campo de usuário vazio
    Dado que o usuário está na página de "Login"
    Quando o usuário preenche o campo "Usuário" com ""
    E o usuário preenche o campo "Senha" com "Senha123!"
    E o usuário clica no botão "Entrar"
    Então o sistema exibe a mensagem de erro "O campo Usuário é obrigatório"
    E o usuário permanece na página de "Login"

  Cenário: Tentativa de login com campo de senha vazio
    Dado que o usuário está na página de "Login"
    Quando o usuário preenche o campo "Usuário" com "usuario@exemplo.com"
    E o usuário preenche o campo "Senha" com ""
    E o usuário clica no botão "Entrar"
    Então o sistema exibe a mensagem de erro "O campo Senha é obrigatório"
    E o usuário permanece na página de "Login"