# Story: Improve messaging for rejected boosts
# Model: flash | Score: 5.1/10

Funcionalidade: Melhorar Mensagens para Boosts Rejeitados

  Cenário: Boost rejeitado por Conteúdo Inapropriado
    Dado que estou logado como "usuario@exemplo.com"
    E que possuo um rascunho de boost com "conteúdo sexualmente explícito"
    E que estou na página de criação de boost "https://app.minds.com/boost/create"
    Quando clico no botão "Publicar Boost" `#publish-boost-button`
    Então vejo a mensagem "Seu boost foi rejeitado: Conteúdo considerado inapropriado. Edite seu post para conformidade." no elemento `.alert-danger`
    E então vejo o botão "Editar Post" `button[data-action="edit-post"]`

  Cenário: Boost rejeitado por Fundos Insuficientes
    Dado que estou logado como "usuario@exemplo.com"
    E que meu saldo disponível é "R$ 0,00"
    E que estou na página de criação de boost "https://app.minds.com/boost/create"
    E que o valor do boost é "R$ 10,00"
    Quando clico no botão "Publicar Boost" `#publish-boost-button`
    Então vejo a mensagem "Seu boost foi rejeitado: Saldo insuficiente. Adicione fundos para prosseguir." no elemento `.alert-warning`
    E então vejo o link "Adicionar Fundos" `a[href="/wallet/add-funds"]`

  Cenário: Boost rejeitado por Violação de Política da Plataforma
    Dado que estou logado como "usuario@exemplo.com"
    E que possuo um rascunho de boost que viola "política de direitos autorais"
    E que estou na página de criação de boost "https://app.minds.com/boost/create"
    Quando clico no botão "Publicar Boost" `#publish-boost-button`
    Então vejo a mensagem "Seu boost foi rejeitado: Violação de política de uso. Consulte nossas diretrizes." no elemento `.rejection-message`
    E então vejo o link "Diretrizes da Plataforma" `a[href="https://app.minds.com/policies"]`

  Cenário: Visualização de Boost Rejeitado na Página de Gerenciamento
    Dado que estou logado como "usuario@exemplo.com"
    E que possuo um boost com ID "123" previamente "rejeitado por conteúdo inapropriado"
    E que estou na página de gerenciamento de boosts "https://app.minds.com/boosts/manage"
    Quando acesso a URL "https://app.minds.com/boosts/manage"
    Então vejo o status "Rejeitado" no elemento `#boost-item-123 .status-badge`
    E então vejo a mensagem "Conteúdo considerado inapropriado. Por favor, edite seu post para conformidade." no elemento `#boost-item-123 .rejection-reason`
    E então vejo o botão "Detalhes da Rejeição" `button[data-boost-id="123"]`

  Cenário: Boost rejeitado por Erro Técnico Inesperado
    Dado que estou logado como "usuario@exemplo.com"
    E que o sistema de processamento de boosts está "indisponível"
    E que estou na página de criação de boost "https://app.minds.com/boost/create"
    Quando clico no botão "Publicar Boost" `#publish-boost-button`
    Então vejo a mensagem "Ocorreu um erro inesperado. Tente novamente ou contate o suporte." no elemento `.error-technical`
    E então vejo o link "Contatar Suporte" `a[href="/support"]`