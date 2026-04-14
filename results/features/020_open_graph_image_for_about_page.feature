# Story: Open Graph image for About page
# Model: flash | Score: 6.7/10

Funcionalidade: Imagem Open Graph para a Página "Sobre"

Cenário: Página "Sobre" exibe a tag Open Graph de imagem correta
  Dado que o sistema Minds.com está online
  Quando um usuário navega para a URL "https://minds.com/about"
  Então o código-fonte da página contém a meta tag `<meta property="og:image" content="https://www.minds.com/assets/images/about-page-og.jpg">`
  E a meta tag `og:image` possui o atributo `property`
  E a meta tag `og:image` possui o atributo `content`

Cenário: A imagem Open Graph especificada é acessível publicamente
  Dado que a página "https://minds.com/about" contém a meta tag `<meta property="og:image" content="https://www.minds.com/assets/images/about-page-og.jpg">`
  Quando uma requisição HTTP GET é feita para "https://www.minds.com/assets/images/about-page-og.jpg"
  Então o servidor responde com o código de status "200 OK"
  E o cabeçalho `Content-Type` da resposta é "image/jpeg"

Cenário: Compartilhamento no Facebook exibe a imagem Open Graph da página "Sobre"
  Dado que a página "https://minds.com/about" contém a meta tag `<meta property="og:image" content="https://www.minds.com/assets/images/about-page-og.jpg">`
  Quando a URL "https://minds.com/about" é inserida em uma postagem do Facebook
  Então a pré-visualização do Facebook exibe a imagem "https://www.minds.com/assets/images/about-page-og.jpg"

Cenário: Compartilhamento no Twitter exibe a imagem Open Graph da página "Sobre"
  Dado que a página "https://minds.com/about" contém a meta tag `<meta property="og:image" content="https://www.minds.com/assets/images/about-page-og.jpg">`
  E que a página "https://minds.com/about" contém a meta tag `<meta name="twitter:card" content="summary_large_image">`
  E que a página "https://minds.com/about" contém a meta tag `<meta name="twitter:image" content="https://www.minds.com/assets/images/about-page-og.jpg">`
  Quando a URL "https://minds.com/about" é inserida em um tweet do Twitter
  Então a pré-visualização do Twitter exibe a imagem "https://www.minds.com/assets/images/about-page-og.jpg"

Cenário: Página "Sobre" sem tag og:image usa imagem padrão em compartilhamentos sociais
  Dado que o sistema Minds.com está online
  E que a página "https://minds.com/about" não contém a meta tag `og:image`
  Quando a URL "https://minds.com/about" é inserida em uma postagem do Facebook
  Então a pré-visualização do Facebook exibe a imagem "https://www.minds.com/assets/images/default-minds-logo.jpg"

Cenário: Imagem Open Graph com URL inválida resulta em pré-visualização sem imagem
  Dado que a página "https://minds.com/about" contém a meta tag `<meta property="og:image" content="https://www.minds.com/assets/images/imagem-inexistente-404.jpg">`
  E que uma requisição HTTP GET para "https://www.minds.com/assets/images/imagem-inexistente-404.jpg" retorna status "404 Not Found"
  Quando a URL "https://minds.com/about" é inserida em uma postagem do Facebook
  Então a pré-visualização do Facebook não exibe a imagem "https://www.minds.com/assets/images/imagem-inexistente-404.jpg"
  E a pré-visualização do Facebook exibe uma imagem padrão do Minds.com