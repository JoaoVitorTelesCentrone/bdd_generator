# Story: Subscribers list not complete, or not showing at all
# Model: flash | Score: 5.1/10

Funcionalidade: Visualização da Lista de Inscritos do Canal

  Cenário: Visualização completa da lista de inscritos
    Dado que o usuário "usuario_teste@exemplo.com" está logado
    E que o usuário possui 10 inscritos
    E que o usuário está na página do canal "https://app.exemplo.com/canal/usuario_teste"
    Quando clico no link "Subscription" #link-subscription
    E clico na aba "Subscribers" #tab-subscribers
    Então vejo "10 inscritos" #counter-subscribers
    E a lista #list-subscribers contém 10 itens
    E o botão "Ver mais" #button-view-more não