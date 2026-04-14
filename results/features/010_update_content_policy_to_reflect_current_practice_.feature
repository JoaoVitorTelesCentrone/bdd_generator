# Story: Update content policy to reflect current practice on token manipulation
# Model: flash | Score: 5.6/10

Cenário: Atualização e verificação da política na página de conteúdo
  Dado que estou logado como um "administrador" no sistema de gerenciamento de conteúdo
  E a "página de política de conteúdo" em "https://example.com/politica-de-conteudo" contém a frase "manipulação de token resultará em banimento imediato"
  Quando eu navego para a "página de edição da política de conteúdo" (ex: "https://example.com/admin/policies/edit/content")
  E eu localizo o "campo de texto" com ID "policy-editor-token-manipulation-section"
  E eu altero o texto de "banimento imediato" para "rejeição de saques" dentro deste campo
  E eu clico no "botão Salvar" com ID "save-policy-button"
  Então a "página de política de conteúdo" em "https://example.com/politica-de-conteudo" deve exibir "rejeição de saques" para manipulação de token
  E a "página de política de conteúdo" em "https://example.com/politica-de-conteudo" não deve exibir "banimento imediato" para manipulação de token

Cenário: Atualização e verificação da política nos documentos GitLab
  Dado que estou logado na "plataforma de documentos GitLab" como um "mantenedor"
  E a "documentação GitLab sobre manipulação de token" em "https://gitlab.com/docs/policy/token-manipulation" contém a frase "banimento imediato"
  Quando eu navego para o "repositório de documentos GitLab" (ex: "https://gitlab.com/my-project/docs/-/edit/main/policy/token-manipulation.md")
  E eu localizo a "seção de política de manipulação de token" no editor de texto
  E eu altero o texto de "banimento imediato" para "rejeição de saques"
  E eu clico no "botão Commit Changes" com ID "commit-changes-button"
  Então a "documentação GitLab sobre manipulação de token" em "https://gitlab.com/docs/policy/token-manipulation" deve exibir "rejeição de saques"
  E a "documentação GitLab sobre manipulação de token" em "https://gitlab.com/docs/policy/token-manipulation" não deve exibir "banimento imediato"

Cenário: Consistência da política entre página de conteúdo e documentos GitLab
  Dado que a "página de política de conteúdo" em "https://example.com/politica-de-conteudo" foi atualizada com "rejeição de saques" para manipulação de token
  E a "documentação GitLab sobre manipulação de token" em "https://gitlab.com/docs/policy/token-manipulation" foi atualizada com "rejeição de saques"
  Quando um "usuário comum" acessa a "página de política de conteúdo"
  E o mesmo "usuário comum" acessa a "documentação GitLab sobre manipulação de