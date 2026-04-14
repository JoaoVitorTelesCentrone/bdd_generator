# Story: Define email strategy
# Model: flash | Score: 7.5/10

Funcionalidade: Definição de Estratégias de E-mail

Cenário: Visualizar estratégias de e-mail existentes como administrador
  Dado que o usuário "admin@empresa.com" está logado como administrador
  E que a página "https://app.empresa.com/admin/email-strategies" exibe as estratégias
  E que existe uma estratégia "Boas-vindas" com descrição "Enviar e-mails para novos usuários" e status "Ativa"
  Quando o usuário acessa a página "https://app.empresa.com/admin/email-strategies"
  Então a tabela `table[data-testid="strategies-list"]` exibe a estratégia "Boas-vindas"
  E a linha da estratégia "Boas-vindas" `tr[data-strategy-name="Boas-vindas"]` contém a descrição "Enviar e-mails para novos usuários"
  E a linha da estratégia "Boas-vindas" `tr[data-strategy-name="Boas-vindas"]` exibe o status "Ativa"

Cenário: Criar uma nova estratégia de e-mail com sucesso
  Dado que o usuário "admin@empresa.com" está logado como administrador
  E que o usuário está na página de criação de estratégia "https://app.empresa.com/admin/email-strategies/new"
  Quando o usuário digita "Reengajamento de Inativos" no campo `input[name="strategyName"]`
  E o usuário digita "Campanha para reativar usuários que não interagem há 30 dias." no campo `textarea[name="description"]`
  E o usuário seleciona "Reengajamento" no dropdown `select[name="strategyType"]`
  E o usuário seleciona "Mensal" no dropdown `select[name="frequency"]`
  E o usuário clica no botão `button[data-testid="save-strategy"]`
  Então o usuário é redirecionado para "https://app.empresa.com/admin/email-strategies"
  E uma mensagem de sucesso `div[data-testid="success-message"]` com "Estratégia criada com sucesso" é exibida
  E a tabela `table[data-testid="strategies-list"]` exibe a estratégia "Reengajamento de Inativos"
  E a estratégia "Reengajamento de Inativos" `tr[data-strategy-name="Reengajamento de Inativos"]` exibe o status "Inativa"

Cenário: Editar uma estratégia de e-mail existente
  Dado que o usuário "admin@empresa.com" está logado como administrador
  E que a estratégia "Boas-vindas" existe com descrição "Enviar e-mails para novos usuários"
  Quando o usuário acessa a página de edição "https://app.empresa.com/admin/email-strategies/boas-vindas/edit"
  E o usuário digita "Sequência de e-mails para novos cadastros com dicas de uso." no campo `textarea[name="description"]`
  E o usuário seleciona "Semanal" no dropdown `select[name="frequency"]`
  E o usuário clica no botão `button[data-testid="update-strategy"]`
  Então o usuário é redirecionado para "https://app.empresa.com/admin/email-strategies"
  E uma mensagem de sucesso `div[data-testid="success-message"]` com "Estratégia atualizada com sucesso" é exibida
  E a tabela `table[data-testid="strategies-list"]` exibe a estratégia "Boas-vindas" com descrição "Sequência de e-mails para novos cadastros com dicas de uso."
  E a estratégia "Boas-vindas" `tr[data-strategy-name="Boas-vindas"]` tem a frequência "Semanal"

Cenário: Ativar uma estratégia de e-mail inativa
  Dado que o usuário "admin@empresa.com" está logado como administrador
  E que a estratégia "Promoções Semanais" existe com status "Inativa"
  Quando o usuário clica no botão "Ativar" `button[data-strategy-name="Promoções Semanais"][data-action="activate"]` na página "https://app.empresa.com/admin/email-strategies"
  Então uma mensagem de sucesso `div[data-testid="success-message"]` com "Estratégia ativada com sucesso" é exibida
  E a estratégia "Promoções Semanais" `tr[data-strategy-name="Promoções Semanais"]` exibe o status "Ativa"

Cenário: Desativar uma estratégia de e-mail ativa
  Dado que o usuário "admin@empresa.com" está logado como administrador
  E que a estratégia "Boas-vindas" existe com status "Ativa"
  Quando o usuário clica no botão "Desativar" `button[data-strategy-name="Boas-vindas"][data-action="deactivate"]` na página "https://app.empresa.com/admin/email-strategies"
  Então uma mensagem de sucesso `div[data-testid="success-message"]` com "Estratégia desativada com sucesso" é exibida
  E a estratégia "Boas-vindas" `tr[data-strategy-name="Boas-vindas"]` exibe o status "Inativa"

Cenário: Tentar criar estratégia de e-mail com nome duplicado
  Dado que o usuário "admin@empresa.com" está logado como administrador
  E que a estratégia "Boas-vindas" já existe
  E que o usuário está na página de criação de estratégia "https://app.empresa.com/admin/email-strategies/new"
  Quando o usuário digita "Boas-vindas" no campo `input[name="strategyName"]`
  E o usuário digita "Uma nova estratégia de boas-vindas." no campo `textarea[name="description"]`
  E o usuário seleciona "Boas-vindas" no dropdown `select[name="strategyType"]`
  E o usuário clica no botão `button[data-testid="save-strategy"]`
  Então uma mensagem de erro `span[data-testid="error-message-name"]` com "Nome da estratégia já existe" é exibida
  E a estratégia "Boas-vindas" não é criada novamente

Cenário: Tentar criar estratégia de e-mail sem nome (campo obrigatório)
  Dado que o usuário "admin@empresa.com" está logado como administrador
  E que o usuário está na página de criação de estratégia "https://app.empresa.com/admin/email-strategies/new"