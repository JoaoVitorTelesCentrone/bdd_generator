# Story: Add Popular Channels module
# Model: flash | Score: 5.6/10

Funcionalidade: Gerenciamento do Módulo de Canais Populares

Cenário: Exibição do módulo de canais populares para usuário guest em desktop
  Dado que o usuário não está logado
  E o dispositivo de acesso é um "desktop"
  E a lista de canais populares contém "@MindsOfficial", "@MindsGaming", "@MindsMusic"
  Quando o usuário navega para a página inicial da plataforma
  Então o módulo "Popular Channels" é exibido no "right rail"
  E o módulo exibe o título "Popular Channels"
  E o módulo exibe os canais "@MindsOfficial", "@MindsGaming", "@MindsMusic"
  E cada canal exibe um avatar, o nome do canal e um botão "Subscribe"

Cenário: Não exibição do módulo de canais populares em dispositivos não-desktop
  Dado que o usuário não está logado
  E o dispositivo de acesso é um "mobile"
  Quando o usuário navega para a página inicial da plataforma
  Então o módulo "Popular Channels" não é exibido

Cenário: Redirecionamento para login ao tentar se inscrever como guest
  Dado que o usuário não está logado
  E o dispositivo de acesso é um "desktop"
  E o módulo "Popular Channels" está visível
  Quando o usuário clica no botão "Subscribe" do canal "@MindsOfficial"
  Então o usuário é redirecionado para a página de "Login/Cadastro"

Cenário: Navegação para a página do canal ao clicar no nome do canal como guest
  Dado que o usuário não está logado
  E o dispositivo de acesso é um "desktop"
  E o módulo "Popular Channels" está visível
  Quando o usuário clica no nome do canal "@MindsGaming"
  Então o usuário é redirecionado para a página de perfil do canal "@MindsGaming"

Cenário: Ordem consistente dos canais na lista estática
  Dado que o usuário não está logado
  E o dispositivo de acesso é um "desktop"
  E a configuração da lista estática de canais é "@MindsOfficial", "@MindsGaming", "@MindsMusic"
  Quando o usuário navega para a página inicial da plataforma
  Então o módulo "Popular Channels" exibe os canais na ordem: "1º @MindsOfficial", "2º @MindsGaming", "3º @MindsMusic"

Cenário: Lista de canais scrollável quando há muitos canais configurados
  Dado que o usuário não está logado
  E o dispositivo de acesso é um "desktop"
  E a lista de canais populares contém "10" canais, excedendo o espaço visível
  Quando o usuário navega para a página inicial da plataforma
  Então o módulo "Popular Channels" é exibido
  E a lista de canais dentro do módulo é "scrollável"

Cenário: Módulo não exibido quando a lista de canais populares está vazia
  Dado que o usuário não está logado
  E o dispositivo de acesso é um "desktop"
  E a lista de canais populares configurada está "vazia"
  Quando o usuário navega para a página inicial da plataforma
  Então o módulo "Popular Channels" não é exibido

Cenário: Exibição de placeholder para canal com avatar ausente
  Dado que o usuário não está logado
  E o dispositivo de acesso é um "desktop"
  E a lista de canais populares inclui um canal "@NoAvatarChannel" com avatar "ausente"
  Quando o usuário navega para a página inicial da plataforma
  Então o módulo "Popular Channels" exibe o canal "@NoAvatarChannel"
  E o canal "@NoAvatarChannel" exibe um "avatar placeholder padrão"

Cenário: Canal excluído não é exibido na lista
  Dado que o usuário não está logado
  E o dispositivo de acesso é um "desktop"
  E a lista de canais populares configurada inclui o canal "@DeletedChannel" que foi "excluído"
  Quando o usuário navega para a página inicial da plataforma
  Então o módulo "Popular Channels" é exibido
  E o canal "@DeletedChannel" não é exibido na lista

Cenário: Exibição única de canais quando há duplicatas na configuração estática
  Dado que o usuário não está logado
  E o dispositivo de acesso é um "desktop"
  E a lista de canais populares configurada contém "@MindsOfficial" "duas" vezes
  Quando o usuário navega para a página inicial da plataforma
  Então o módulo "Popular Channels" é exibido
  E o canal "@MindsOfficial" é exibido "apenas uma" vez na lista

Cenário: Módulo não exibido em caso de falha no carregamento da configuração de canais
  Dado que o usuário não está logado
  E o dispositivo de acesso é um "desktop"
  E a configuração da lista estática de canais "não pôde ser carregada"
  Quando o usuário navega para a página inicial da plataforma
  Então o módulo "Popular Channels" não é exibido
  E uma mensagem "Não foi possível carregar os canais populares" é exibida