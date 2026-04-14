# Story: Remove sidebar chat widget from Groups
# Model: flash | Score: 6.3/10

Funcionalidade: Remoção do Widget de Chat da Barra Lateral em Páginas de Grupo

Cenário: Ausência do widget de chat em página de grupo (Desktop)
  Dado que um usuário "membro@exemplo.com" está autenticado
  E um grupo "Grupo de Teste Desktop" (ID: "grupo-desktop-123") existe com conteúdo
  Quando o usuário acessa a URL "/groups/grupo-desktop-123"
  Então o elemento ".sidebar-chat-widget" não deve estar visível
  E o elemento ".sidebar-chat-widget" não deve existir no DOM
  E o texto "Iniciar Chat" não deve ser exibido na página

Cenário: Coluna direita presente, vazia e sem funcionalidade de expansão/colapso (Desktop)
  Dado que um usuário "membro@exemplo.com" está autenticado
  E um grupo "Grupo com Coluna Vazia" (ID: "grupo-coluna-vazia-456") existe com conteúdo
  Quando o usuário acessa a URL "/groups/grupo-coluna-vazia-456"
  Então o elemento ".right-column" deve estar visível
  E o elemento ".right-column" não deve conter nenhum elemento filho com a classe ".chat-content"
  E o elemento ".right-column" deve estar vazio, exceto por elementos estruturais
  E o elemento "[data-testid='right-column-toggle-button']" não deve estar visível
  E o elemento "[data-testid='right-column-toggle-button']" não deve existir no DOM

Cenário: Layout da página de grupo em dispositivo móvel sem widget de chat
  Dado que um usuário "membro@exemplo.com" está autenticado
  E um grupo "Grupo Mobile Teste" (ID: "grupo-mobile-789") existe com conteúdo
  E o dispositivo é um smartphone com largura de tela máxima de 768px
  Quando o usuário acessa a URL "/groups/grupo-mobile-789"
  Então o elemento ".sidebar-chat-widget" não deve estar visível
  E o elemento ".sidebar-chat-widget" não deve existir no DOM
  E o conteúdo principal da página ".group-main-content" deve ocupar a largura total disponível
  E não deve haver uma coluna lateral vazia à direita

Cenário: Requisição ao endpoint do widget de chat retorna status 403 Forbidden
  Dado que o serviço de chat da barra lateral foi desativado no backend
  Quando uma requisição GET é feita para a API "/api/chat/group-widget-status"
  E a requisição inclui um token de autenticação válido
  Então a resposta da API deve ter o status HTTP 403 Forbidden
  E o corpo da resposta deve conter a mensagem de erro "Acesso Proibido" ou similar