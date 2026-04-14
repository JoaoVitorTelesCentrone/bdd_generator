# Story: Register modal improvements
# Model: flash | Score: 5.7/10

Característica: Melhorias no Modal de Registro

Cenário: Registro bem-sucedido com dados válidos
  Dado que o usuário está na página "https://app.exemplo.com/cadastro"
  Quando preencho o campo input[name="email"] com "novo.usuario@email.com"
  E preencho o campo input[name="password"] com "SenhaForte@123"
  E preencho o campo input[name="confirm-password"] com "SenhaForte@123"
  E clico no checkbox #terms-checkbox
  E clico no botão button[type="submit"]
  Então vejo a mensagem .success-message "Registro realizado com sucesso!"
  E sou redirecionado para a URL "https://app.exemplo.com/dashboard"

Cenário: Exibição de requisitos de senha ao digitar
  Dado que o usuário está na página "https://app.exemplo.com/cadastro"
  Quando digito "senha" no campo input[name="password"]
  Então vejo o texto .password-requirement:nth-child(1) "Mínimo 8 caracteres"
  E vejo o texto .password-requirement:nth-child(2) "Pelo menos um número"
  E vejo o texto .password-requirement:nth-child(3) "Pelo menos um caractere especial"

Cenário: Validação de e-mail inválido em tempo real
  Dado que o usuário está na página "https://app.exemplo.com/cadastro"
  Quando preencho o campo input[name="email"] com "email_invalido"
  E clico no campo input[name="password"]
  Então vejo a mensagem .error-message[for="email"] "Formato de e-mail inválido"

Cenário: Senhas não coincidem
  Dado que o usuário está na página "https://app.exemplo.com/cadastro"
  Quando preencho o campo input[name="password"] com "SenhaForte@123"
  E preencho o campo input[name="confirm-password"] com "SenhaDiferente@123"
  E clico no botão button[type="submit"]
  Então vejo a mensagem .error-message[for="confirm-password"] "As senhas não coincidem"

Cenário: E-mail já registrado
  Dado que o usuário está na página "https://app.exemplo.com/cadastro"
  E o e-mail "existente@email.com" já está registrado no sistema
  Quando preencho o campo input[name="email"] com "existente@email.com"
  E preencho o campo input[name="password"] com "NovaSenha@456"
  E preencho o campo input[name="confirm-password"] com "NovaSenha@456"
  E clico no checkbox #terms-checkbox
  E clico no botão button[type="submit"]
  Então vejo a mensagem .error-message[for="email"] "Este e-mail já está em uso"

Cenário: Links de Termos de Serviço e Política de Privacidade presentes e clicáveis
  Dado que o usuário está na página "https://app.exemplo.com/cadastro"
  Quando vejo o modal de registro
  Então vejo o link a[href="https://app.exemplo.com/termos"] com o texto "Termos de Serviço"
  E vejo o link a[href="https://app.exemplo.com/politica-privacidade"] com o texto "Política de Privacidade"
  E o link a[href="https://app.exemplo.com/termos"] é clicável
  E o link a[href="https://app.exemplo.com/politica-privacidade"] é clicável