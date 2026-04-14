# Story: (bug) Verify your email address emails broken on Hotmail and Outlook
# Model: flash | Score: 4.5/10

Funcionalidade: Verificação de Endereço de Email

Cenário: Email de verificação é exibido corretamente no Outlook
  Dado que um usuário com email "usuario@outlook.com" se registrou e aguarda verificação
  Quando o sistema envia o email de verificação para "usuario@outlook.com"
  Então o usuário recebe o email de verificação em sua caixa de entrada do Outlook
  E o email possui o título "Verifique seu endereço de e-mail para [Nome da Aplicação]"
  E o corpo do email contém o texto "Olá [Nome do Usuário],"
  E o corpo do email contém o texto "Por favor, verifique seu endereço de e-mail clicando no link abaixo:"
  E o email exibe um link `a[data-testid="verify-email-link"]` com o texto "Verificar E-mail"
  E o email exibe o branding ou logotipo da aplicação no elemento `img[alt="Logo da Aplicação"]`
  E o layout do email é renderizado sem quebras visuais ou elementos sobrepostos

Cenário: Email de verificação é exibido corretamente no Hotmail
  Dado que um usuário com email "usuario@hotmail.com" se registrou e aguarda verificação
  Quando o sistema envia o email de verificação para "usuario@hotmail.com"
  Então o usuário recebe o email de verificação em sua caixa de entrada do Hotmail
  E o email possui o título "Verifique seu endereço de e-mail para [Nome da Aplicação]"
  E o corpo do email contém o texto "Olá [Nome do Usuário],"
  E o corpo do email contém o texto "Por favor, verifique seu endereço de e-mail clicando no link abaixo:"
  E o email exibe um link `a[data-testid="verify-email-link"]` com o texto "Verificar E-mail"
  E o email exibe o branding ou logotipo da aplicação no elemento `img[alt="Logo da Aplicação"]`
  E o layout do email é renderizado sem quebras visuais ou elementos sobrepostos

Cenário: Conteúdo do email é legível e formatado corretamente no Outlook
  Dado que um usuário com email "usuario@outlook.com" recebeu o email de verificação
  Quando o usuário abre o email de verificação no Outlook
  Então o texto do email é formatado com fonte legível e tamanho adequado
  E os parágrafos do email possuem espaçamento correto
  E não há caracteres especiais ou símbolos quebrados no corpo do email `div.email-body-content`
  E o link `a[data-testid="verify-email-link"]` é clicável e visualmente destacado

Cenário: Conteúdo do email é legível e formatado corretamente no Hotmail
  Dado que um usuário com email "usuario@hotmail.com" recebeu o email de verificação
  Quando o usuário abre o email de verificação no Hotmail
  Então o texto do email é formatado com fonte legível e tamanho adequado
  E os parágrafos do email possuem espaçamento correto
  E não há caracteres especiais ou símbolos quebrados no corpo do email `div.email-body-content`
  E o link `a[data-testid="verify-email-link"]` é clicável e visualmente destacado

Cenário: Email de verificação inclui informações de contato e privacidade no Outlook
  Dado que um usuário com email "usuario@outlook.com" recebeu o email de verificação
  Quando o usuário abre o email de verificação no Outlook
  Então o rodapé do email contém o endereço de contato da aplicação no elemento `div.email-footer-address`
  E o rodapé do email contém um link para a política de privacidade no elemento `a[href*="politica-privacidade"]`
  E o rodapé do email contém um link para os termos de serviço no elemento `a[href*="termos-servico"]`

Cenário: Email de verificação inclui informações de contato e privacidade no Hotmail
  Dado que um usuário com email "usuario@hotmail.com" recebeu o email de verificação
  Quando o usuário abre o email de verificação no Hotmail
  Então o rodapé do email contém o endereço de contato da aplicação no elemento `div.email-footer-address`
  E o rodapé do email contém um link para a política de privacidade no elemento `a[href*="politica-privacidade"]`
  E o rodapé do email contém um link para os termos de serviço no elemento `a[href*="termos-servico"]`