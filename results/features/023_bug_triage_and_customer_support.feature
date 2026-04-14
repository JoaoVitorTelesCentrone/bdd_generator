# Story: Bug Triage and Customer Support
# Model: flash | Score: 5.8/10

Funcionalidade: Relatório de Bugs e Suporte ao Cliente

  Cenário: Acesso ao Formulário de Relatório de Bug
    Dado que o usuário "suporte@empresa.com" está logado
    E o usuário está na URL "https://app.empresa.com/suporte"
    Quando clico no botão "Reportar um Bug" #btn-reportar-bug
    Então o formulário de bug é exibido na URL "https://app.empresa.com/suporte/bug-report"
    E vejo o título "Relatório de Bug Detalhado" #bug-report-title

  Cenário: Relatório de Bug Completo Submetido com Sucesso
    Dado que o usuário "suporte@empresa.com" está na URL "https://app.empresa.com/suporte/bug-report"
    E vejo o campo de texto "Título do Bug" #bug-title
    Quando preencho o campo "Título do Bug" com "Falha ao carregar imagens de perfil" #bug-title
    E preencho o campo "Descrição" com "Imagens não aparecem após upload em 'Minha Conta'" #bug-description
    E seleciono a opção "Alta" no dropdown "Prioridade" #bug-priority
    E digito "https://app.empresa.com/perfil" no campo "URL Atingida" #bug-url-affected
    E submeto o formulário de bug #submit-bug-report-btn
    Então sou redirecionado para a URL "https://app.empresa.com/suporte/confirmacao"
    E vejo a mensagem "Seu relatório de bug foi enviado com sucesso." .success-message

  Cenário: Tentativa de Submissão com Campos Obrigatórios Vazios
    Dado que o usuário "suporte@empresa.com" está na URL "https://app.empresa.com/suporte/bug-report"
    E vejo o campo de texto "Título do Bug" #bug-title
    Quando deixo o campo "Título do Bug" vazio #bug-title
    E preencho o campo "Descrição" com "Teste de descrição" #bug-description
    E submeto o formulário de bug #submit-bug-report-btn
    Então vejo a mensagem de erro "Este campo é obrigatório." .error-message[for="bug-title"]
    E a URL permanece "https://app.empresa.com/suporte/bug-report"

  Cenário: Relatório de Bug com Anexo de Evidência
    Dado que o usuário "suporte@empresa.com" está na URL "https://app.empresa.com/suporte/bug-report"
    E vejo o campo de upload "Anexar Evidência" #bug-attachment
    Quando preencho o campo "Título do Bug" com "Erro de digitação em cabeçalho" #bug-title
    E preencho o campo "Descrição" com "O cabeçalho 'Bem Vindo' está incorreto." #bug-description
    E anexo o arquivo "screenshot_erro.png" no campo "Anexar Evidência" #bug-attachment
    E submeto o formulário de bug #submit-bug-report-btn
    Então sou redirecionado para a URL "https://app.empresa.com/suporte/confirmacao"
    E vejo o texto "screenshot_erro.png" listado na confirmação .attachment-list-item

  Cenário: Cancelamento do Relatório de Bug
    Dado que o usuário "suporte@empresa.com" está na URL "https://app.empresa.com/suporte/bug-report"
    E vejo o botão "Cancelar" #btn-cancelar-bug
    Quando preencho o campo "Título do Bug" com "Bug de teste" #bug-title
    E clico no botão "Cancelar" #btn-cancelar-bug
    Então sou redirecionado para a URL "https://app.empresa.com/suporte"
    E não vejo o título "Relatório de Bug Detalhado" #bug-report-title