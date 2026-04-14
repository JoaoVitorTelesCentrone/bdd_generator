# Story: Add definition for each report reason
# Model: flash | Score: 7.4/10

Funcionalidade: Gerenciamento de Definições para Motivos de Denúncia

Cenário: Visualizar definições existentes para motivos de denúncia como administrador
  Dado que o usuário "admin@minds.com" está logado como administrador
  E que a página "https://app.minds.com/admin/report-reasons" exibe os motivos de denúncia
  E que o motivo "Spam" possui a definição "Conteúdo indesejado e repetitivo."
  Quando o usuário acessa a página "https://app.minds.com/admin/report-reasons"
  Então o campo `div[data-reason="Spam"] p[data-testid="reason-definition"]` exibe o texto "Conteúdo indesejado e repetitivo."

Cenário: Adicionar uma nova definição a um motivo de denúncia sem definição
  Dado que o usuário "admin@minds.com" está logado como administrador
  E que a página "https://app.minds.com/admin/report-reasons" exibe os motivos de denúncia
  E que o motivo "Assédio" não possui uma definição
  Quando o usuário clica no botão `button[data-reason="Assédio"][data-action="add-definition"]`
  E o usuário digita "Comportamento ofensivo e repetitivo contra indivíduos." no campo `textarea[data-testid="definition-input"]`
  E o usuário clica no botão `button[data-testid="save-definition"]`
  Então o campo `div[data-reason="Assédio"] p[data-testid="reason-definition"]` exibe o texto "Comportamento ofensivo e repetitivo contra indivíduos."
  E uma mensagem de sucesso `div[data-testid="success-message"]` com "Definição salva com sucesso" é exibida

Cenário: Editar uma definição existente para um motivo de denúncia
  Dado que o usuário "admin@minds.com" está logado como administrador
  E que a página "https://app.minds.com/admin/report-reasons" exibe os motivos de denúncia
  E que o motivo "Nudez" possui a definição "Conteúdo sexualmente explícito ou gráfico."
  Quando o usuário clica no botão `button[data-reason="Nudez"][data-action="edit-definition"]`
  E o usuário digita "Imagens ou vídeos de nudez, total ou parcial." no campo `textarea[data-testid="definition-input"]`
  E o usuário clica no botão `button[data-testid="save-definition"]`
  Então o campo `div[data-reason="Nudez"] p[data-testid="reason-definition"]` exibe o texto "Imagens ou vídeos de nudez, total ou parcial."
  E uma mensagem de sucesso `div[data-testid="success-message"]` com "Definição atualizada com sucesso" é exibida

Cenário: Tentar adicionar uma definição vazia
  Dado que o usuário "admin@minds.com" está logado como administrador
  E que a página "https://app.minds.com/admin/report-reasons" exibe os motivos de denúncia
  E que o motivo "Discurso de Ódio" não possui uma definição
  Quando o usuário clica no botão `button[data-reason="Discurso de Ódio"][data-action="add-definition"]`
  E o usuário limpa o campo `textarea[data-testid="definition-input"]`
  E o usuário clica no botão `button[data-testid="save-definition"]`
  Então uma mensagem de erro `span[data-testid="error-message-definition"]` com "A definição não pode ser vazia" é exibida
  E o motivo "Discurso de Ódio" ainda não possui uma definição

Cenário: Tentar adicionar uma definição que excede o limite de caracteres
  Dado que o usuário "admin@minds.com" está logado como administrador
  E que a página "https://app.minds.com/admin/report-reasons" exibe os motivos de denúncia
  E que o motivo "Informação Falsa" não possui uma definição
  Quando o usuário clica no botão `button[data-reason="Informação Falsa"][data-action="add-definition"]`
  E o usuário digita "Este é um texto muito longo para testar o limite de caracteres. Ele deve exceder o limite máximo permitido para uma definição de motivo de denúncia, que é de 255 caracteres, para garantir que a validação de comprimento funcione corretamente e impeça o envio de dados excessivos." no campo `textarea[data-testid="definition-input"]`
  E o usuário clica no botão `button[data-testid="save-definition"]`
  Então uma mensagem de erro `span[data-testid="error-message-definition"]` com "A definição excede o limite de 255 caracteres" é exibida
  E o motivo "Informação Falsa" ainda não possui uma definição

Cenário: Cancelar a edição de uma definição
  Dado que o usuário "admin@minds.com" está logado como administrador
  E que a página "