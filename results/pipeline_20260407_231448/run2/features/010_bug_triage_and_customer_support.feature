# Story: Bug Triage and Customer Support
# Model: flash | Score: 8.6/10

Funcionalidade: Registro de Relatos de Problema

Cenário: Acesso e exibição do template de registro de bug
  Dado que um usuário autenticado possui permissão para relatar problemas
  Quando o usuário navega para a página de "Relatar Problema"
  Então a interface de registro de problema é exibida
  E o template de bug é exibido claramente
  E o campo "Título" deve ser exibido
  E o campo "Descrição" deve ser exibido
  E o campo "Passos para Reproduzir" deve ser exibido
  E o campo "Comportamento Esperado" deve ser exibido
  E o campo "Comportamento Atual" deve ser exibido
  E o campo "Ambiente/Versão" deve ser exibido

Cenário: Submissão bem-sucedida de um relatório de bug completo e detalhado
  Dado que um usuário autenticado está na página de "Relatar Problema"
  E que o template de bug está visível
  Quando eu preencho o campo "Título" com "Bug: Botão de login não funciona"
  E eu preencho o campo "Descrição" com "O botão de login não reage ao clique"
  E eu preencho o campo "Passos para Reproduzir" com "1. Acessar tela de login. 2. Clicar no botão 'Entrar'."
  E eu preencho o campo "Comportamento Esperado" com "O sistema deve autenticar o usuário"
  E eu preencho o campo "Comportamento Atual" com "Nada acontece ao clicar no botão"
  E eu preencho o campo "Ambiente/Versão" com "Navegador Chrome v120, App v2.5"
  E eu anexo o arquivo "screenshot_erro_login.png"
  E eu seleciono a categoria "Bug"
  E eu clico no botão "Submeter Relatório"
  Então eu vejo a mensagem de sucesso "Relatório submetido com sucesso. ID: #BUG-12345"
  E o relatório é registrado no sistema com um identificador único

Cenário: Tentativa de submissão de relatório de bug com campos obrigatórios vazios
  Dado que um usuário autenticado está na página de "Relatar Problema"
  E que o template de bug está visível
  Quando eu preencho o campo "Título" com "Bug: Campo Descrição vazio"
  E eu deixo o campo "Descrição" vazio
  E eu preencho o campo "Passos para Reproduzir" com "1. Tentar submeter sem descrição."
  E eu seleciono a categoria "Bug"
  E eu clico no botão "Submeter Relatório"
  Então eu vejo a mensagem de erro "O campo Descrição é obrigatório"
  E o relatório não é submetido ao sistema

Cenário: Tentativa de acesso à página de relato de problema por usuário sem permissão
  Dado que um usuário autenticado não possui a permissão "RELATAR_PROBLEMAS"
  Quando o usuário tenta navegar para a página "relatar-problema"
  Então eu vejo a mensagem de erro "Você não tem permissão para acessar esta funcionalidade"
  E o usuário é redirecionado para a página "Minha Conta"

Cenário: Submissão bem-sucedida de um relato classificado como "Melhoria"
  Dado que um usuário autenticado está na página de "Relatar Problema"
  Quando eu preencho o campo "Título" com "Melhoria: Adicionar filtro de data"
  E eu preencho o campo "Descrição" com "Seria útil ter um filtro de data na tela de relatórios"
  E eu seleciono a categoria "Melhoria"
  E eu clico no botão "Submeter Relatório"
  Então eu vejo a mensagem de sucesso "Relato submetido com sucesso. ID: #MEL-67890"
  E o relato é registrado no sistema como uma "Melhoria"