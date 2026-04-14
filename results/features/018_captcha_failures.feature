# Story: Captcha failures
# Model: flash | Score: 2.5/10

Funcionalidade: Validação do CAPTCHA no Registro de Usuário

Cenário: Falha na validação do CAPTCHA com entrada correta
  Dado que o usuário está na página de registro "https://minds.com/register"
  E um CAPTCHA "ABC123" é exibido no campo input[name="captcha"]
  E o usuário preenche o campo input[name="username"] com "usuario_correto"
  E o usuário preenche o campo input[name="email"] com "correto@exemplo.com"
  E o usuário preenche o campo input[name="password"] com "SenhaSegura123!"
  E o usuário preenche o campo input[name="password_