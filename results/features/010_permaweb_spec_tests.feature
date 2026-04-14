# Story: Permaweb spec tests
# Model: flash | Score: 4.7/10

**Funcionalidade: Testes de Especificação do Permaweb**

**Cenário: Upload de conteúdo de texto simples com sucesso**
  DADO que o usuário está na página de upload do Permaweb "https://permaweb.app/upload"
  QUANDO o usuário seleciona o arquivo "documento_teste.txt" no input #file-upload
  E o usuário clica no botão "Upload" button[type="submit"]
  ENTÃO o sistema exibe o hash do conteúdo "QmXyz123ABCDEF" no elemento .content-hash
  E o sistema exibe a mensagem "Conteúdo armazenado permanentemente" no .success-message

**Cenário: Recuperação de conteúdo por hash**
  DADO que o conteúdo com hash "QmXyz123ABCDEF" foi previamente carregado
  QUANDO o usuário navega para a URL "https://permaweb.app/QmXyz123ABCDEF"
  ENTÃO o sistema exibe o texto "Este é o conteúdo do meu documento." no elemento pre#content-display
  E o sistema retorna o status HTTP "200 OK"

**Cenário: Tentativa de sobrescrever conteúdo existente (Imutabilidade)**
  DADO que o conteúdo com hash "QmXyz123ABCDEF" já existe no Permaweb
  QUANDO o usuário seleciona o arquivo "novo_documento.txt" no input #file-upload
  E o usuário clica no botão "Upload" button[type="submit"]
  ENTÃO o sistema exibe a mensagem de erro "Conteúdo já existe e é imutável" no .error-message
  E o sistema não altera o hash "QmXyz123ABCDEF"

**Cenário: Upload de arquivo grande**
  DADO que o usuário está na página de upload do Permaweb "https://permaweb.app/upload"
  QUANDO o usuário seleciona o arquivo "video_grande.mp4" (50 MB) no input #file-upload
  E o usuário clica no botão "Upload" button[type="submit"]
  ENTÃO o sistema exibe o hash do conteúdo "QmWXYZ789UVW" no elemento .content-hash
  E o sistema exibe a mensagem "Upload concluído com sucesso" no .success-message

**Cenário: Tentativa de recuperar conteúdo inexistente**
  DADO que nenhum conteúdo está associado ao hash "QmNonExistentHash"
  QUANDO o usuário navega para a URL "https://permaweb.app/QmNonExistentHash"
  ENTÃO o sistema exibe a mensagem "Conteúdo não encontrado" no .error-page-message
  E o sistema retorna o status HTTP "404 Not Found"