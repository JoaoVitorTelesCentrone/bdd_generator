# Story: (bug): subscribed blog post duplicates filling feed
# Model: flash | Score: 7.4/10

Funcionalidade: Gerenciamento de Feed de Usuário

  Cenário: Novo post de blog inscrito aparece uma única vez no feed
    Dado que "usuario_alice@exemplo.com" está logado
    E que "usuario_alice@exemplo.com" está inscrito no "Blog de Tecnologia" (ID: "BLOG001")
    Quando o "Blog de Tecnologia" (ID: "BLOG001") publica o novo post "Avanços em IA Generativa" (ID: "POST001")
    E "usuario_alice@exemplo.com" acessa seu feed
    Então o feed exibe o post "Avanços em IA Generativa" (ID: "POST001")