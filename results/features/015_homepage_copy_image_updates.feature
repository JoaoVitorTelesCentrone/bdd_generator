# Story: Homepage: Copy / image updates
# Model: flash | Score: 4.3/10

Funcionalidade: Atualização da Página Inicial Clássica

Cenário: Exibição da Nova Visão do Produto
  Dado que o usuário acessa a página inicial "https://www.example.com/"
  Quando a página é carregada completamente
  Então o texto "Nossa visão: Capacitar criadores e comunidades" é exibido no elemento `p[data-testid="product-vision"]`
  E o texto "Visão antiga da empresa" não é exibido na página

Cenário: Exibição da Nova Declaração de Missão
  Dado que o usuário acessa a página inicial "https://www.example.com/"
  Quando a página é carregada completamente
  Então o texto "Nossa missão: Conectar o mundo com liberdade e inovação" é exibido no elemento `h2[data-testid="mission-statement"]`
  E o texto "Missão desatualizada da empresa" não é exibido na página

Cenário: Exibição da Nova Imagem Principal da Seção Hero
  Dado que o usuário acessa a página inicial "https://www.example.com/"
  Quando a página é carregada completamente
  Então a imagem `img[alt="Pessoas colaborando em um ambiente moderno"]` é exibida no elemento `div[data-testid="hero-section"]`
  E a imagem `img[alt="Imagem antiga do produto"]` não é exibida na página

Cenário: Presença da Nova Seção de Destaque "Como Funciona"
  Dado que o usuário acessa a página inicial "https://www.example.com/"
  Quando a página é carregada completamente
  Então a seção `section[data-testid="como-funciona-section"]` é exibida
  E o título "Descubra como funciona" é exibido dentro da seção `section[data-testid="como-funciona-section"]`

Cenário: Botão de Cadastro (Call to Action) Funcional
  Dado que o usuário acessa a página inicial "https://www.example.com/"
  Quando o usuário clica no botão `button[data-testid="signup-button"]`
  Então o usuário é redirecionado para a URL "https://www.example.com/cadastro"

Cenário: Aplicação de Estilos Visuais Modernizados (Tema e Fonte)
  Dado que o usuário acessa a página inicial "https://www.example.com/"
  Quando a página é carregada completamente
  Então o elemento `body` possui a classe CSS "theme-modern"
  E o texto "Explore agora" no botão `button[data-testid="explore-button"]` usa a fonte "Inter"

Cenário: Conteúdo Antigo e Descontinuado Removido da Página
  Dado que o usuário acessa a página inicial "https://www.example.com/"
  Quando a página é carregada completamente
  Então o elemento `div[data-testid="outdated-promo"]` não é exibido
  E o texto "Promoção descontinuada" não é exibido na página