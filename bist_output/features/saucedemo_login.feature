Funcionalidade: Login no SauceDemo

  Cenário: Login bem-sucedido com credenciais válidas
    Dado que estou na página de "https://www.saucedemo.com"
    Quando preenche o campo "#user-name" com "standard_user"
    E preenche o campo "#password" com "secret_sauce"
    E clica no botão "#login-button"
    Então o sistema exibe "Products"

  Cenário: Tentativa de login com senha inválida
    Dado que estou na página de "https://www.saucedemo.com"
    Quando preenche o campo "#user-name" com "standard_user"
    E preenche o campo "#password" com "senha_errada"
    E clica no botão "#login-button"
    Então o sistema exibe "Epic sadface"

  Cenário: Tentativa de login com usuário bloqueado
    Dado que estou na página de "https://www.saucedemo.com"
    Quando preenche o campo "#user-name" com "locked_out_user"
    E preenche o campo "#password" com "secret_sauce"
    E clica no botão "#login-button"
    Então o sistema exibe "Sorry, this user has been locked out"
