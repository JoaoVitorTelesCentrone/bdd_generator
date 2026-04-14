# Story: Discovery: Add "Top" tab (mobile app)
# Model: flash | Score: 4.8/10

Funcionalidade: Aba "Top" na página Discovery

  Cenário: Verificar a presença da aba "Top" na página Discovery
    Dado que o usuário está logado no aplicativo
    Quando acesso a página Discovery através do ícone "#discovery-icon"
    Então vejo a aba "Top" com o seletor "#top-tab"
    Então vejo a aba "Trending" com o seletor "#trending-tab"

  Cenário: A aba "Top" é a aba padrão ao acessar a página Discovery
    Dado que o usuário está logado no aplicativo
    Quando acesso a página Discovery através do ícone "#discovery-icon"
    Então a aba com o seletor "#top-tab" possui o estado "ativo"