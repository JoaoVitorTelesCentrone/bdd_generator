# Story: Permaweb spec tests
# Model: flash | Score: 4.6/10

Funcionalidade: Verificação da Conformidade da Permaweb com Especificações de Conteúdo

Cenário: Conteúdo publicado permanece inalterado após tentativa de modificação
  Dado que o usuário "autor@example.com" publicou o "documento_original.txt" com o ID "doc-123"
  E que o conteúdo original do documento é "Este é o texto original."
  Quando o usuário "autor@example.com" tenta atualizar o "documento_original.txt" com o ID "doc-123" para "Este é o texto modificado."
  Então o sistema rejeita a atualização com a mensagem de erro `text[data-testid="error-message-immutable"]` "Conteúdo da Permaweb é imutável"
  E o conteúdo do documento com ID "doc-123" permanece "Este é o texto original." ao ser acessado pela URL "https://permaweb.io/doc-123"

Cenário: Conteúdo publicado permanece acessível após um longo período
  Dado que o usuário "arquivista@example.com" publicou a "imagem_historica.png" com o ID "img-456"
  E que o conteúdo da imagem foi verificado com hash "hash_original_img456"
  Quando 5 anos se passam desde a publicação da "imagem_historica.png"
  E o usuário "leitor@example.com" tenta acessar a imagem pela URL "https://permaweb.io/img-456"
  Então a "imagem_historica.png" é exibida com sucesso
  E o hash do conteúdo da imagem acessada corresponde a "hash_original_img456"

Cenário: Integridade do conteúdo é mantida durante o armazenamento e recuperação
  Dado que o usuário "verificador@example.com" publicou o "video_ciencia.mp4" com o ID "vid-789"
  E que o hash SHA256 do arquivo original é "sha256_original_vid789"
  Quando o usuário "verificador@example.com" recupera o "video_ciencia.mp4" com o ID "vid-789"
  Então o hash SHA256 do arquivo recuperado corresponde a "sha256_original_vid789"
  E o tamanho do arquivo recuperado `span[data-testid="file-size"]` é "150 MB"

Cenário: Endereço do conteúdo é único e consistente
  Dado que o usuário "editor@example.com" publicou a "pagina_artigo.html" com o ID "art-001"
  E que a URL gerada para o conteúdo é "https://permaweb.io/art-001"
  Quando o usuário "editor@example.com" tenta publicar um novo conteúdo "pagina_nova.html" com o mesmo ID "art-001"
  Então o sistema rejeita a publicação com a mensagem de erro `text[data-testid="error-message-duplicate-id"]` "ID de conteúdo já existente"
  E a URL "https://permaweb.io/art-001" continua a exibir "pagina_artigo.html"

Cenário: Conteúdo inexistente não é acessível
  Dado que não existe nenhum conteúdo publicado com o ID "nao-existe-999"
  Quando o usuário "curioso@example.com" tenta acessar a URL "https://permaweb.io/nao-existe-999"
  Então o sistema exibe a página de erro `h1[data-testid="error-page-title"]` "404 - Conteúdo Não Encontrado"
  E a página não exibe nenhum conteúdo associado ao ID "nao-existe-999"