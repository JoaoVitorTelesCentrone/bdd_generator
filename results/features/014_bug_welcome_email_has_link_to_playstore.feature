# Story: (bug): welcome email has link to PlayStore
# Model: flash | Score: 5.6/10

Funcionalidade: Correção do Link da Play Store no E-mail de Boas-Vindas

  Cenário: E-mail de boas-vindas não contém o link inválido específico da Play Store
    Dado que estou na página de registro "https://app.exemplo.com/registrar"
    E que o e-mail "usuario.bug@exemplo.com" não está cadastrado no sistema
    Quando preencho o campo `input[name="email"]` com "usuario.bug@exemplo.com"
    E preencho o campo `input[name="senha"]` com "SenhaBug@123"
    E clico no botão `button[type="submit"]`
    Então