# Story: Discovery: Implement channel recommendations component - web
# Model: flash | Score: 7.4/10

Funcionalidade: Componente de Recomendações de Canal na Página Discovery

Cenário: Exibição do componente para usuário logado
  Dado que um usuário autenticado está na página "Discovery / Top"
  Quando a página é carregada
  Então o componente "Channel Recommendations" é exibido

Cenário: Exibição do componente para visitante (não logado)
  Dado que um usuário não autenticado está na página "Discovery / Top"
  Quando a página é carregada
  Então o componente "Channel Recommendations" é exibido

Cenário: Conformidade visual do componente com o protótipo
  Dado que o componente "Channel Recommendations" é exibido na página "Discovery / Top"
  Quando o usuário visualiza a página
  Então o componente está posicionado conforme o protótipo de design
  E o componente possui o título "Canais Recomendados"
  E o componente exibe "3" recomendações de canal inicialmente

Cenário: Layout responsivo em tela de desktop
  Dado que o componente "Channel Recommendations" é exibido na página "Discovery / Top"
  E a largura da tela é "1280" pixels
  Quando o usuário visualiza a página
  Então o layout do componente se adapta para desktop

Cenário: Layout responsivo em tela de tablet
  Dado que o componente "Channel Recommendations" é exibido na página "Discovery / Top"
  E a largura da tela é "768" pixels
  Quando o usuário visualiza a página
  Então o layout do componente se adapta para tablet

Cenário: Layout responsivo em tela