# Story: Email address registration failure
# Model: flash | Score: 5.6/10

Funcionalidade: Falha no Registro de Endereço de Email

Cenário: Falha ao registrar com email "hzmd@me.com" no website
  Dado que o usuário acessa a página de registro "https://www.example.com/register"
  Quando o usuário digita "hzmd@me.com" no campo de email `input[type="email"]`
  E o usuário clica no botão "Registrar" `button[type="submit"]`
  Então uma mensagem de erro `div[data-testid="error-message"]` é exibida com "Endereço de email inválido ou não aceito"
  E o usuário permanece na página de registro "https://www.example.com/register"

Cenário: Falha ao registrar com email "hzmd@me.com" no aplicativo iOS
  Dado que o usuário está na tela de registro do aplicativo iOS
  Quando o usuário digita "hzmd@me.com" no campo de email `XCUIElementTypeTextField[@name="Email address input"]`
  E o usuário toca no botão "Registrar" `XCUIElementTypeButton[@name="Register button"]`
  Então uma mensagem de erro `XCUIElementTypeStaticText[@name="Error message"]` é exibida com "Endereço de email inválido ou não aceito"
  E o usuário permanece na tela de registro

Cenário: Falha ao registrar com email "hzmd@icloud.com" no aplicativo iOS
  Dado que o usuário está na tela de registro do aplicativo iOS
  Quando o usuário digita "hzmd@icloud.com" no campo de email `XCUIElementTypeTextField[@name="Email address input"]`
  E o usuário toca no botão "Registrar" `XCUIElementTypeButton[@name="Register button"]`
  Então uma mensagem de erro `XCUIElementTypeStaticText[@name="Error message"]` é exibida com "Endereço de email inválido ou não aceito"
  E o usuário permanece na tela de registro

Cenário: Múltiplas tentativas de registro com o mesmo email inválido no website
  Dado que o usuário acessa a página de registro "https://www.example.com/register"
  E que o campo de email `input[type="email"]` está preenchido com "hzmd@me.com"
  Quando o usuário clica no botão "Registrar" `button[type="submit"]` por "2" vezes
  Então uma mensagem de erro `div[data-testid="error-message"]` é exibida com "Endereço de email inválido ou não aceito"
  E o usuário permanece na página de registro "https://www.example.com/register"

Cenário: Múltiplas tentativas de registro com o mesmo email inválido no aplicativo iOS
  Dado que o usuário está na tela de registro do aplicativo iOS
  E que o campo de email `XCUIElementTypeTextField[@name="Email address input"]` está preenchido com "hzmd@me.com"
  Quando o usuário toca no botão "Registrar" `XCUIElementTypeButton[@name="Register button"]` por "2" vezes
  Então uma mensagem de erro `XCUIElementTypeStaticText[@name="Error message"]` é exibida com "Endereço de email inválido ou não aceito"
  E o usuário permanece na tela de registro