# Story: Code-based email verifications in mobile app
# Model: flash | Score: 7.4/10

Cenário: Verificação de e-mail bem-sucedida com código válido
  Dado que eu estou na tela de "Verificação de E-mail" (ID: 'emailVerificationScreen')
  E o e-mail "usuario@exemplo.com" foi registrado no sistema
  E um código de verificação "123456" foi enviado para "usuario@exemplo.com" e está ativo
  Quando eu preencho o campo "Código de Verificação" (ID: 'verificationCodeInput') com "123456"
  E eu toco no botão "Verificar" (ID: 'verifyButton')
  Então o e-mail "usuario@exemplo.com" é marcado como verificado no