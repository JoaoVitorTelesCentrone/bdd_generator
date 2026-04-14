# Story: Bug Triage and Customer Support
# Model: flash | Score: 5.6/10

Funcionalidade: Relatório de Bug e Suporte ao Cliente

  Cenário: Submeter um relatório de bug detalhado com sucesso
    Dado que estou na página de "Relatar Bug" em "https://app.suporte.com/bugs/novo"
    Quando preencho o campo input[name="titulo-bug"] com "Erro ao salvar configurações do perfil"
    E preencho o campo textarea[name="descricao-bug"] com "Ao clicar em 'Salvar', um erro 500 é exibido."
    E preencho o campo textarea[name="passos-reproducao"] com "1. Acessar /perfil. 2. Alterar nome. 3. Clicar em 'Salvar'."
    E preencho o campo input[name="resultado-esperado"] com "Configurações salvas e mensagem de sucesso."
    E preencho o campo input[name="resultado-real"] com "Erro 500 e dados não são salvos."
    E seleciono a opção "Alta" no dropdown select[name="severidade"]
    E seleciono a opção "Média" no dropdown select[name="prioridade"]
    E clico no botão button[data-testid="submit-bug-report"]
    Então vejo a mensagem ".alert-success" com "Bug reportado com sucesso!"
    E sou redirecionado para a URL "https://app.suporte.com/bugs/12345"

  Cenário: Tentar submeter um relatório de bug com campos obrigatórios ausentes
    Dado que estou na página de "Relatar Bug" em "https://app.suporte.com/bugs/novo"
    Quando preencho o campo input[name="titulo-bug"] com "Bug sem descrição"
    E clico no botão button[data-testid="submit-bug-report"]
    Então vejo a mensagem ".error-msg[for='descricao-bug']" com "Descrição é obrigatória."
    E vejo a mensagem ".error-msg[for='passos-reproducao']" com "Passos para Reprodução são obrigatórios."
    E não sou redirecionado da URL "https://app.suporte.com/bugs/novo"

  Cenário: Submeter um relatório de bug com anexo
    Dado que estou na página de "Relatar Bug" em "https://app.suporte.com/bugs/novo"
    Quando preencho o campo input[name="titulo-bug"] com "Bug de layout em dispositivos móveis"
    E preencho o campo textarea[name="descricao-bug"] com "O rodapé se sobrepõe ao conteúdo em telas pequenas."
    E preencho o campo textarea[name="passos-reproducao"] com "1. Acessar a página inicial. 2. Redimensionar janela para mobile."
    E preencho o campo input[name="resultado-esperado"] com "Layout responsivo correto."
    E preencho o campo input[name="resultado-real"] com "Rodapé sobreposto."
    E anexo o arquivo "screenshot_mobile.png" ao input[type="file"]
    E clico no botão button[data-testid="submit-bug-report"]
    Então vejo a mensagem ".alert-success"