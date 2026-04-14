# Story: "Switch to app" overlay overlaps Guest Mode banner
# Model: flash | Score: 4.5/10

Funcionalidade: Exibição do Overlay "Mudar para o aplicativo" em Modo Convidado Móvel

Cenário: Overlay "Mudar para o aplicativo" é exibido e banner "Modo Convidado" é removido em dispositivo móvel iOS
  Dado que o usuário está em um dispositivo móvel iOS
  E que o usuário acessa a página inicial do Modo Convidado "https://www.minds.com/guest-mode"
  Quando a página é carregada
  Então o overlay "Mudar para o aplicativo" `div[data-testid="switch-to-app-overlay"]` é exibido
  E o overlay `div[data-testid="switch-to-app-overlay"]` está fixado na parte inferior da tela
  E o banner "Modo Convidado" `div[data-testid="guest-mode-banner"]` não é exibido