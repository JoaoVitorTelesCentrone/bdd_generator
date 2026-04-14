# Story: Change contact info for p/contact page
# Model: flash | Score: 7.0/10

Funcionalidade: Atualização das Informações de Contato na Página "p/contact"

Cenário: Verificação da exibição do novo título e email de contato
  Dado que o usuário está em qualquer página do site
  Quando o usuário navega para a página "https://www.minds.com/p/contact"
  Então o elemento `h2.contact-title` exibe o texto "Support Center"
  E o elemento `a.contact-email` exibe o email "support@minds.zendesk.com"

Cenário: Confirmação da remoção do título de contato antigo
  Dado que o usuário está em qualquer página do site
  Quando o usuário navega para a página "https://www.minds.com/p/contact"
  Então o texto "Help Desk" não é exibido na página
  E o elemento `h2.contact-title` não contém o texto "Help Desk"

Cenário: Confirmação da remoção do email de contato antigo
  Dado que o usuário está em qualquer página do site
  Quando o usuário navega para a página "https://www.minds.com/p/contact"
  Então o email "info@minds.com" não é exibido na página
  E o elemento `a.contact-email` não contém o email "info@minds.com"