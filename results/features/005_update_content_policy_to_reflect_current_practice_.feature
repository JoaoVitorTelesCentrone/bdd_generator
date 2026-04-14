# Story: Update content policy to reflect current practice on token manipulation
# Model: flash | Score: 5.4/10

Funcionalidade: Atualização da Política de Conteúdo sobre Manipulação de Tokens

Cenário: A política de conteúdo oficial reflete a prática de rejeição de saques
  Dado que a página de política de conteúdo "https://example.com/politica-de-conteudo" contém o texto "banimento imediato"
  Quando a política de conteúdo é atualizada para a nova prática
  Então a página de política de conteúdo "https://example.com/politica-de-conteudo" exibe o texto "rejeitar os saques" no elemento `div[data-policy-section="token-manipulation"]`
  E a página de política de conteúdo "https://example.com/politica-de-conteudo" não exibe o texto "banimento imediato" no elemento `div[data-policy-section="token-manipulation"]`

Cenário: A documentação do GitLab reflete a prática de rejeição de saques
  Dado que a página de documentação do GitLab "https://gitlab.com/docs/politica-de-tokens" contém o texto "banimento imediato"
  Quando a documentação do GitLab é atualizada para a nova prática
  Então a página de documentação do GitLab "https://gitlab.com/docs/politica-de-tokens" exibe o texto "rejeitar os saques" no elemento `div[data-doc-section="token-manipulation"]`
  E a página de documentação do GitLab "https://gitlab.com/docs/politica-de-tokens" não exibe o texto "banimento imediato" no elemento `div[data-doc-section="token-manipulation"]`