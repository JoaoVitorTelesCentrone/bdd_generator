# Story: Add Popular Channels module
# Model: flash | Score: 7.7/10

Funcionalidade: Módulo de Canais Populares

Cenário: Módulo de Canais Populares visível para usuário não autenticado em desktop
  Dado que o usuário não autenticado acessa a página inicial "https://www.minds.com/feed"
  Quando a página é carregada
  Então o módulo "Canais Populares" `div[data-testid="popular-channels-module"]` é exibido
  E o módulo `div[data-testid="popular-channels-module"]` está na barra lateral direita `aside[data-testid="right-rail"]`

Cenário: Módulo de Canais Populares visível para usuário autenticado em desktop
  Dado que o usuário "usuario@example.com" está logado
  E que o usuário acessa a página inicial "https://www.minds.com/feed"
  Quando a página é carregada
  Então o módulo "Canais Populares" `div[data-testid="popular-channels-module"]` é exibido
  E o módulo `div[data-testid="popular-channels-module"]` está na barra lateral direita `aside[data-testid="right-rail"]`

Cenário: Módulo de Canais Populares exibe lista estática de canais pré-definidos
  Dado que o usuário está na página inicial "https://www.minds.com/feed" em um desktop
  E que o módulo "Canais Populares" `div[data-testid="popular-channels-module"]` é exibido
  Quando o usuário visualiza o conteúdo do módulo
  Então o módulo contém um canal "@Minds" `a[href="/@Minds"]`
  E o módulo contém um canal "@MindsNews" `a[href="/@MindsNews"]`
  E o módulo contém um canal "@MindsOfficial" `a[href="/@MindsOfficial"]`
  E o módulo exibe "5" canais na lista

Cenário: Módulo de Canais Populares não exibe canais personalizados para usuário não autenticado
  Dado que o usuário não autenticado acessa a página inicial "https://www.minds.com/feed"
  E que o módulo "Canais Populares" `div[data-testid="popular-channels-module"]` é exibido
  Quando o usuário visualiza o conteúdo do módulo
  Então a seção "Canais Recomendados para Você" `div[data-testid="recommended-channels-section"]` não é exibida

Cenário: Módulo de Canais Populares não visível em dispositivos móveis
  Dado que o usuário acessa a página inicial "https://www.minds.com/feed" em um dispositivo móvel
  Quando a página é carregada
  Então o módulo "Canais Populares" `div[data-testid="popular-channels-module"]` não é exibido

Cenário: Canais da lista estática possuem links funcionais
  Dado que o usuário está na página inicial "https://www.minds.com/feed" em um desktop
  E que o módulo "Canais Populares" `div[data-testid="popular-channels-module"]` é exibido
  Quando o usuário clica no canal "@Minds" `a[href="/@Minds"]` dentro do módulo
  Então o usuário é redirecionado para "https://www.minds.com/@Minds"