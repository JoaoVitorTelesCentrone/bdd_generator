# Story: Move completed development tickets to QA Review in sprint and attach link to sandbox
# Model: flash | Score: 6.2/10

Funcionalidade: Movimentação de Tickets para Revisão QA

Cenário: Mover ticket de desenvolvimento concluído para revisão QA com link válido
  Dado que o usuário "dev@empresa.com" está logado como Desenvolvedor
  E que o ticket "DEV-123" com status "Desenvolvimento Concluído" existe no sprint ativo
  Quando o usuário arrasta o ticket "DEV-123" para a coluna "Revisão QA" no painel do sprint
  E preenche o campo `input[data-testid='sandbox-link-input']` com "https://sandbox.empresa.com/dev123"
  E clica no botão `button[data-testid='confirmar-movimentacao']`
  Então o ticket "DEV-123" é exibido na coluna "Revisão QA"
  E o campo `.ticket-details__sandbox-link` do ticket "DEV-123" exibe o link "https://sandbox.empresa.com/dev123"
  E o status do ticket "DEV-123" é "Revisão QA"

Cenário: Impedir movimentação sem link de sandbox obrigatório
  Dado que o usuário "dev@empresa.com" está logado como Desenvolvedor
  E que o ticket "DEV-124" com status "Desenvolvimento Concluído" existe no sprint ativo
  Quando o usuário arrasta o ticket "DEV-124" para a coluna "Revisão QA" no painel do sprint
  E clica no botão `button[data-testid='confirmar-movimentacao']` sem preencher o campo `input[data-testid='sandbox-link-input']`
  Então o sistema exibe a mensagem de erro `.error-message[for='sandbox-link']` com "O link do sandbox é obrigatório."
  E o ticket "DEV-124" permanece na coluna "Desenvolvimento Concluído"

Cenário: Impedir movimentação de ticket não concluído para revisão QA
  Dado que o usuário "dev@empresa.com" está logado como Desenvolvedor
  E que o ticket "DEV-125" com status "Em Desenvolvimento" existe no sprint ativo
  Quando o usuário tenta arrastar o ticket "DEV-125" para a coluna "Revisão QA" no painel do sprint
  Então o sistema exibe a mensagem de erro `.alert-danger` com "Apenas tickets em 'Desenvolvimento Concluído' podem ser movidos para Revisão QA."
  E o ticket "DEV-125" permanece na coluna "Em Desenvolvimento"

Cenário: Link do sandbox anexado é clicável e visível para revisores de QA
  Dado que o usuário "qa@empresa.com" está logado como QA
  E que o ticket "DEV-123" está na coluna "Revisão QA" no sprint ativo
  E que o ticket "DEV-123" possui o link "https://sandbox.empresa.com/dev123" anexado
  Quando o usuário acessa a página de detalhes do ticket "DEV-123" na URL "https://app.empresa.com/ticket/DEV-123"
  Então o elemento `a.ticket-details__sandbox-link` com o texto "https://sandbox.empresa.com/dev123" é visível
  E o atributo `href` do elemento `a.ticket-details__sandbox-link` é "https://sandbox.empresa.com/dev123"

Cenário: Impedir movimentação com formato de link de sandbox inválido
  Dado que o usuário "dev@empresa.com" está logado como Desenvolvedor
  E que o ticket "DEV-126" com status "Desenvolvimento Concluído" existe no sprint ativo
  Quando o usuário arrasta o ticket "DEV-126" para a coluna "Revisão QA" no painel do sprint
  E preenche o campo `input[data-testid='sandbox-link-input