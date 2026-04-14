# Story: Homepage: Copy / image updates
# Model: flash | Score: 6.1/10

Funcionalidade: Atualização da Homepage Classic

Cenário: Cabeçalho principal e missão refletem a nova visão do produto
  Dado que o usuário está na "Homepage Classic" na URL "https://www.example.com/classic"
  Quando o usuário visualiza o conteúdo da página
  Então o elemento "h1#main-headline" exibe o texto "Descubra o Futuro da Inovação com [Nome do Produto]"
  E o elemento "p#mission-statement" contém o texto "Nossa missão é empoderar usuários através de tecnologia de ponta e soluções intuitivas." (conforme "Product vision deck")

Cenário: Textos de destaque e CTAs alinhados com a nova visão
  Dado que o