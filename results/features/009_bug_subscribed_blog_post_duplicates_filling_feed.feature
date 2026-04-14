# Story: (bug): subscribed blog post duplicates filling feed
# Model: flash | Score: 6.9/10

Funcionalidade: Gerenciamento de Feed de Notícias

Cenário: Novo post de um blog assinado aparece uma única vez no feed
  Dado que o usuário "leitor@exemplo.com" está logado
  E que o usuário está assinado ao blog "Blog de Tecnologia"
  E que o blog "Blog de Tecnologia" publicou um novo post "Novidades em IA"
  Quando o usuário acessa a página do feed de notícias "https://app.exemplo.com/feed"
  Então o feed exibe o post "Novidades em IA" no elemento ".post-card[data-post-id='101']"
  E o feed contém apenas uma ocorrência do post "Novidades em IA"

Cenário: Múltiplos novos posts de um blog assinado aparecem uma única vez cada no feed
  Dado que o usuário "leitor@exemplo.com" está logado
  E que o usuário está assinado ao blog "Blog de Esportes"
  E que o blog "Blog de Esportes" publicou os posts "Resultados da Partida" e "Análise Pós-Jogo"
  Quando o usuário acessa a página do feed de notícias "https://app.exemplo.com/feed"
  Então o feed exibe o post "Resultados da Partida" no elemento ".post-card[data-post-id='102']"
  E o feed exibe o post "Análise Pós-Jogo" no elemento ".post-card[data-post-id='103']"
  E o feed contém apenas uma ocorrência de "Resultados da Partida"
  E o feed contém apenas uma ocorrência de "Análise Pós-Jogo"

Cenário: Novos posts de múltiplos blogs assinados aparecem uma única vez cada no feed
  Dado que o usuário "leitor@exemplo.com" está logado
  E que o usuário está assinado ao blog "Blog de Culinária"
  E que o usuário está assinado ao blog "Blog de Viagens"
  E que o blog "Blog de Culinária" publicou o post "Receita de Bolo de Chocolate"
  E que o blog "Blog de Viagens" publicou o post "Destinos Exóticos para 2024"
  Quando o usuário acessa a página do feed de notícias "https://app.exemplo.com/feed"
  Então o feed exibe o post "Receita de Bolo de Chocolate" no elemento ".post-card[data-post-id='104']"
  E o feed exibe o post "Destinos Exóticos para 2024" no elemento ".post-card[data-post-id='105']"
  E o feed contém apenas uma ocorrência de "Receita de Bolo de Chocolate"
  E o feed contém apenas uma ocorrência de "Destinos Exóticos para 2024"

Cenário: Reacessar o feed não gera posts duplicados
  Dado que o usuário "leitor@exemplo.com" está logado
  E que o usuário está assinado ao blog "Blog de Notícias"
  E que o blog "Blog de Notícias" publicou um novo post "Eleições Locais 2024"
  E que o usuário acessou a página do feed de notícias "https://app.exemplo.com/feed"
  Quando o usuário navega para a página inicial "https://app.exemplo.com" e depois acessa o feed "https://app.exemplo.com/feed"
  Então o feed exibe o post "Eleições Locais 2024" no elemento ".post-card[data-post-id='106']"
  E o feed contém apenas uma ocorrência do post "Eleições Locais 2024"