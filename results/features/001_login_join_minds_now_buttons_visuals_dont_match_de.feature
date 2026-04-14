# Story: Login / Join Minds Now buttons visuals don't match designs
# Model: flash | Score: 5.5/10

Cenário: Exibição Correta dos Botões "Login" e "Register" em Desktop
  Dado que um usuário não autenticado está na página inicial "https://example.com/"
  Quando a página é carregada em um navegador desktop com largura mínima de 1024px
  Então o botão com seletor "[data-test-id='login-button']" é exibido no canto superior direito
  E o botão com seletor "[data-test-id='login-button']" tem a cor de fundo "#HEX_PRIMARIA_MARCA"
  E o texto do botão com seletor "[data-test-id='login-button']" é "Login"
  E o texto do botão com seletor "[data-test-id='login-button']" tem a cor "#FFFFFF"
  E o botão com seletor "[data-test-id='register-button']" é exibido à direita do botão com seletor "[data-test-id='login-button']"
  E o texto do botão com seletor "[data-test-id='register-button']" é "Register"
  E o botão com seletor "[data-test-id='register-button']" tem borda de "1px" sólida com a cor "#HEX_PRIMARIA_MARCA"
  E o botão com seletor "[data-test-id='register-button']" tem a cor de fundo "#FFFFFF"
  E o texto do botão com seletor "[data-test-id='register-button']" tem a cor "#HEX_PRIMARIA_MARCA"
  E ambos os botões têm a fonte "Nome da Fonte" com tamanho "16px"
  E ambos os botões têm o peso da fonte "500"
  E o botão com seletor "[data-test-id='login-button']" tem padding horizontal de "24px" e vertical de "12px"
  E o botão com seletor "[data-test-id='register-button']" tem padding horizontal de "24px" e vertical de "12px"
  E ambos os botões têm border-radius de "8px"

Cenário: Interatividade do Botão "Login"
  Dado que um usuário não autenticado está na página inicial "https://example.com/"
  Quando eu clico no botão com seletor "[data-test-id='login-button']"
  Então sou redirecionado para a URL "https://example.com/login"

Cenário: Interatividade do Botão "Register"
  Dado que um usuário não autenticado está na página inicial "https://example.com/"
  Quando eu clico no botão com seletor "[data-test-id='register-button']"
  Então sou redirecionado para a URL "https://example.com/register"

Cenário: Responsividade dos Botões em Dispositivos Móveis
  Dado que um usuário não autenticado está na página inicial "https://example.com/"
  Quando a página é visualizada em um viewport de 375px de largura
  Então o botão com seletor