# Story: (bug) Emails not arriving
# Model: flash | Score: 4.7/10

Funcionalidade: Envio de E-mails do Sistema

Cenário: E-mail de redefinição de senha não chega ao usuário
  Dado que o usuário "joao.silva@exemplo.com" está registrado no sistema
  E que o usuário "joao.silva@exemplo.com" navega para a página "https://app.exemplo.com/esqueci-senha"
  Quando o usuário preenche o campo `input[name="email"]` com "joao.silva@exemplo.com"
  E o usuário clica no botão `button[data-testid="solicitar-reset"]`
  Então o sistema exibe a mensagem ".alert-success" com "Instruções de redefinição enviadas."
  E a caixa de entrada de "joao.silva@exemplo.com" não contém nenhum e-mail com o assunto "Redefinição de Senha"
  E a pasta de spam de "joao.silva@exemplo.com" não contém nenhum e-mail com o assunto "Redefinição de Senha"

Cenário: E-mail de verificação de conta não chega após registro
  Dado que um novo usuário "maria.santos@exemplo.com" tenta se registrar no sistema
  E que o usuário "maria.santos@exemplo.com" navega para a página "https://app.exemplo.com/registrar"
  Quando o usuário preenche o campo `input[name="email"]` com "maria.santos@exemplo.com"
  E o usuário preenche o campo `input[name="senha"]` com "Senha@123"
  E o usuário preenche o campo `input[name="confirmar-senha"]` com "Senha@123"
  E o usuário clica no botão `button[data-testid="criar-conta"]`
  Então o sistema exibe a mensagem ".alert-success" com "Conta criada! Verifique seu e-mail."
  E a caixa de entrada de "maria.santos@exemplo.com" não contém nenhum e-mail com o assunto "Verifique sua Conta"
  E a pasta de spam de "maria.santos@exemplo.com" não contém nenhum e-mail com o assunto "Verifique sua Conta"

Cenário: E-mail de verificação de e-mail alterado não chega
  Dado que o usuário "joao.silva@exemplo.com" está logado no sistema
  E que o usuário "joao.silva@exemplo.com" navega para a página "https://app.exemplo.com/perfil/configuracoes"
  Quando o usuário preenche o campo `input[name="novo-email"]` com "joao.novo@exemplo.com"
  E o usuário clica no botão `button[data-testid="salvar-email"]`
  Então o sistema exibe a mensagem ".alert-success" com "Seu novo e-mail precisa ser verificado."
  E a caixa de entrada de "joao.novo@exemplo.com" não contém nenhum e-mail com o assunto "Confirme seu Novo E-mail"
  E a pasta de spam de "joao.novo@exemplo.com" não contém nenhum e-mail com o assunto "Confirme seu Novo E-mail"