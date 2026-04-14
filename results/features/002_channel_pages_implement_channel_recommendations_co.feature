# Story: Channel pages: Implement channel recommendations component
# Model: flash | Score: 3.5/10

Funcionalidade: Componente de Recomendações de Canais

Cenário: Componente de recomendações exibido com detalhes em página de canal com posts de atividade
  Dado que um usuário está logado
    E o canal "Marketing Digital" (https://app.exemplo.com/channel/marketing-digital) possui posts de atividade
    E existem canais recomendados para "Marketing Digital"
  Quando o usuário navega para a URL "https://app.exemplo.com/channel/marketing-digital"
  Então o componente "#channel-recommendations-component" deve estar visível
    E o componente "#channel-recommendations-component" exibe o título "Canais Recomendados" (h3.component-title)