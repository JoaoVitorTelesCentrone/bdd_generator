# Story: Documentation on &26 and &30
# Model: flash | Score: 3.5/10

Funcionalidade: Verificação e Qualidade da Documentação de Suporte

Cenário: Acessar e visualizar documentação completa para o tópico "&26"
  Dado que o usuário está logado no sistema
  Quando o usuário navega para a URL "https://app.exemplo.com/docs/26"
  Então a página de documentação é exibida com o título `h1` "Guia do Tópico &26"
  E o conteúdo principal `div[data-testid="doc-content"]` contém a seção "Visão Geral do Recurso"
  E o conteúdo principal `div[data-testid="doc-content"]` contém a seção "Passos para Configuração"

Cen