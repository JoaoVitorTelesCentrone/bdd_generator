# Story: (bug): subscribed blog post duplicates filling feed
# Model: flash | Score: 7.9/10

Funcionalidade: Gerenciamento de Subscrições de Posts no Feed

  Cenário: Exibição única de post subscrito no feed
    Dado que "usuario_comum@example.com" está logado
    E que "usuario_comum@example.com" está subscrito ao post "Primeiro Artigo" (ID: "001")
    Quando "usuario_comum@example.com" navega para o seu feed
    Então o feed exibe o post "Primeiro Artigo" (ID: "001") exatamente "uma" vez

  Cenário: Feed exibe a versão mais recente de post subscrito atualizado
    Dado que "usuario_comum@example.com" está logado
    E que "usuario_comum@example.com" está subscrito ao post "Primeiro Artigo" (ID: "001") com conteúdo "Versão Inicial"
    Quando o autor atualiza o post "Primeiro Artigo" (ID: "001") para o conteúdo "Versão Atualizada (15/03/2023)"
    E "usuario_comum@example.com" recarrega o seu feed
    Então o feed exibe o post "Primeiro Artigo" (ID: "001") com o conteúdo "Versão Atualizada (15/03/2023)"
    E o feed exibe o post "Primeiro Artigo" (ID: "001") exatamente "uma" vez

  Cenário: Múltiplas subscrições ao mesmo post resultam em exibição única
    Dado que "usuario_comum@example.com" está logado
    E que "usuario_comum@example.com" não está subscrito ao post "Segundo Artigo" (ID: "002")
    Quando "usuario_comum@example.com" subscreve ao post "Segundo Artigo" (ID: "002")
    E "usuario_comum@example.com" subscreve novamente ao post "Segundo Artigo" (ID: "002")
    E "usuario_comum@example.com" navega para o seu feed
    Então o feed exibe o post "Segundo Artigo" (ID: "002") exatamente "uma" vez

  Cenário: Post desubscrito não é mais exibido no feed
    Dado que "usuario_comum@example.com" está logado
    E que "usuario_comum@example.com" está subscrito ao post "Primeiro Artigo" (ID: "001")
    E que o feed exibe o post "Primeiro Artigo" (ID: "001")
    Quando "usuario_comum@example.com" desubscreve do post "Primeiro Artigo" (ID: "001")
    E "usuario_comum@example.com" navega para o seu feed
    Então o feed não exibe o post "Primeiro Artigo" (ID: "001")

  Cenário: Integridade do feed mantém unicidade de posts não subscritos
    Dado que "usuario_comum@example.com" está logado
    E que "usuario_comum@example.com" está subscrito ao post "Primeiro Artigo" (ID: "001")
    E que o feed contém o post "Terceiro Artigo" (ID: "003") como conteúdo popular
    Quando "usuario_comum@example.com" navega para o seu feed
    Então o feed exibe o post "Primeiro Artigo" (ID: "001") exatamente "uma" vez
    E o feed exibe o post "Terceiro Artigo" (ID: "003") exatamente "uma" vez

  Cenário: Recarregamento do feed mantém a exibição única de posts subscritos
    Dado que "usuario_comum@example.com" está logado
    E que "usuario_comum@example.com" está subscrito ao post "Primeiro Artigo" (ID: "001")
    E que o feed exibe o post "Primeiro Artigo" (ID: "001") exatamente "uma" vez
    Quando "usuario_comum@example.com" recarrega o seu feed
    Então o feed exibe o post "Primeiro Artigo" (ID: "001") exatamente "uma" vez

  Cenário: Post subscrito tornado privado não é exibido no feed
    Dado que "usuario_comum@example.com" está logado
    E que "usuario_comum@example.com" está subscrito ao post "Artigo Secreto" (ID: "003")
    Quando o autor torna o post "Artigo Secreto" (ID: "003") privado
    E "usuario_comum@example.com" navega para o seu feed
    Então o feed não exibe o post "Artigo Secreto" (ID: "003")

  Cenário: Feed exibe mensagem de nenhum conteúdo para usuário sem subscrições
    Dado que "usuario_novo@example.com" está logado
    E que "usuario_novo@example.com" não