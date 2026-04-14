# Story: Discovery: Add "Top" tab
# Model: flash | Score: 6.3/10

```gherkin
Funcionalidade: Aba "Top" na Página Discovery

  Cenário: Visualização da nova aba "Top" na página Discovery
    Dado que o usuário está autenticado no sistema
    Quando o usuário acessa a URL "https://app.exemplo.com/discovery"
    Então a aba com texto "Top" é exibida no elemento `nav#discovery-tabs`
    E a aba com texto "Recomendado" é exibida no elemento `nav#discovery-tabs`

  Cenário: Aba "Top" é a aba padrão ao carregar a página Discovery
    Dado que o usuário está autenticado no sistema
    Quando o usuário navega para a URL "https://app.exemplo.com/discovery"
    Então a aba `button[data-tab-id="top"]` possui a classe CSS "active"
    E o conteúdo do feed "Top" é exibido no elemento `div#discovery-feed-content`

  Cenário: Conteúdo da aba "Top" reflete posts do feed Guest Mode
    Dado que o usuário está na página "https://app.exemplo.com/discovery"
    E a aba `button[data-tab-id="top"]` está ativa
    Quando o sistema carrega os posts do feed
    Então o post com título "Guia Essencial de Culinária" é visível
    E o autor "Maria Oliveira" é exibido no elemento `.post-card:nth-child(1) .post-author`

  Cenário: Usuário pode mudar para outra aba após o carregamento padrão
    Dado que o usuário está na página "https://app.exemplo.com/discovery"
    E a aba `button[data-tab-id="top"]` está ativa
    Quando o usuário clica no botão `button[data-tab-id="following"]`
    Então a aba `button[data-tab-id="following"]` possui a classe CSS "active"
    E o conteúdo do feed "Seguindo" é exibido no elemento `div#discovery-feed-content`
    E a aba `button[data-tab-id="top"]` não possui a classe CSS "active"

  Cenário: O feed "Top" exibe múltiplos posts relevantes
    Dado que o usuário está na página "https://app.exemplo.com/discovery"
    E a aba `button[data-tab-id="top"]` está selecionada
    Quando o feed de conteúdo é completamente carregado
    Então o elemento `div#discovery-feed-content` contém 3 ou mais posts
    E cada post possui uma imagem de destaque no elemento `.post-card-image`
```