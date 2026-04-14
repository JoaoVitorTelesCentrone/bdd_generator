# Story: Add Popular Channels module
# Model: flash | Score: 6.5/10

Funcionalidade: Módulo Canais Populares

  Cenário: Exibição do Módulo "Canais Populares" para Usuário Convidado em Desktop
    Dado que um usuário "convidado" está na página inicial da plataforma
    E a visualização da tela é em "desktop"
    E a lista de canais populares estática contém "Minds Official", "Crypto Insights" e "Creative Hub"
    Quando a página é "completamente carregada"
    Então o módulo "Popular Channels" deve ser exibido no "right rail"
    E o módulo deve ter o título "Popular Channels"
    E a lista de canais deve exibir "Minds Official"
    E a lista de canais deve exibir "Crypto Insights"
    E a lista de canais deve exibir "Creative Hub"
    E cada canal na lista deve exibir um "nome" e um "avatar"
    E a ordem dos canais deve ser "fixa e pré-definida"

  Cenário: Redirecionamento ao Clicar em um Canal Popular
    Dado que um usuário "convidado" está visualizando o módulo "Popular Channels" em um "desktop"
    E a lista de canais populares estática contém "Minds Official"
    Quando o usuário clica no canal "Minds Official"
    Então o usuário deve ser redirecionado para a página do canal "/MindsOfficial"

  Cenário: Ausência de Funcionalidades de Recomendação Dinâmica para Convidados
    Dado que um usuário "convidado" está visualizando o módulo "Popular Channels" em um "desktop"
    Quando o módulo é exibido
    Então o módulo não deve exibir "recomendações personalizadas"
    E o módulo não deve exibir "canais similares"
    E a lista de canais deve permanecer "estática e inalterada"

  Cenário: Módulo Não Exibido em Visualização Mobile
    Dado que um usuário "convidado" está na página inicial da plataforma
    E a visualização da tela é em um dispositivo "mobile"
    Quando a página é "completamente carregada"
    Então o módulo "Popular Channels" não deve ser exibido

  Cenário: Módulo Não Exibido em Visualização Tablet
    Dado que um usuário "convidado" está na página inicial da plataforma
    E a visualização da tela é em um dispositivo "tablet"
    Quando a página é "completamente carregada"
    Então o módulo "Popular Channels" não deve ser exibido

  Cenário: Módulo Oculto Quando a Lista Estática de Canais Está Vazia
    Dado que um usuário "convidado" está na página inicial da plataforma em um "desktop"
    E a configuração da lista de canais populares está "vazia"
    Quando a página é "completamente carregada"
    Então o módulo "Popular Channels" não deve ser exibido

  Cenário: Canais Inativos ou Inexistentes Não São Exibidos na Lista
    Dado que um usuário "convidado" está na página inicial da plataforma em um "desktop"
    E a lista estática de canais populares inclui "Minds Official (ativo)" e "Canal Desativado (inativo)"
    Quando a página é "completamente carregada"
    Então a lista de canais deve exibir "Minds Official"
    E a lista de canais não deve exibir "Canal Desativado"

  Cenário: Exibição de Canal com Nome Longo
    Dado que um usuário "convidado" está na página inicial da plataforma em um "desktop"
    E a lista estática de canais populares inclui "Minds Official - O Canal Mais Longo e Detalhado da Plataforma"
    Quando a página é "completamente carregada"
    Então o nome do canal "Minds Official - O Canal Mais Longo e Detalhado da Plataforma" deve ser exibido "visivelmente e sem quebra de layout"