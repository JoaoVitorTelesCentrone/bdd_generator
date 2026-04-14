# Story: Minds videos don't load when embedded
# Model: flash | Score: 4.4/10

Funcionalidade: Reprodução de Vídeos Minds Incorporados

Cenário: Vídeo Minds público incorporado carrega e é reproduzido com sucesso
  Dado que um vídeo público do Minds "Vídeo de Teste" existe
  E que o vídeo "Vídeo de Teste" está incorporado na página "Artigo sobre Tecnologia" do site "Corbett Report" em "https://corbettreport.com/artigo-tecnologia"
  Quando o usuário acessa a página "https://corbettreport.com/artigo-tecnologia"
  Então o player de vídeo `iframe[src*="minds.com/embed"]` é exibido
  E o vídeo "Vídeo de Teste" carrega dentro do player
  E o botão de play `button[aria-label="Play"]` é visível
  Quando o usuário clica no botão de play `button[aria-label="Play"]`
  Então o vídeo "Vídeo de Teste" começa a ser reproduzido
  E nenhum erro de carregamento é exibido no player

Cenário: Vídeo Minds público incorporado não carrega e não é reproduzível (Cenário de Bug Atual)
  Dado que um vídeo público do Minds "Vídeo com Falha" existe
  E que o vídeo "Vídeo com Falha" está incorporado na página "Artigo Problemático" do site "Corbett Report" em "https://corbettreport.com/artigo-problema"
  Quando o usuário acessa a página "https://corbettreport.com/artigo-problema"
  Então o player de vídeo `iframe[src*="minds.com/embed"]` é exibido
  E o vídeo "Vídeo com Falha" não carrega dentro do player
  E uma mensagem de erro `div[class*="error-message"]` com "Não foi possível carregar o vídeo" é exibida
  E o vídeo não começa a ser reproduzido mesmo após clicar no play `button[aria-label="Play"]`

Cenário: Vídeo Minds privado incorporado exibe mensagem de privacidade
  Dado que um vídeo privado do Minds "Vídeo Secreto" existe
  E que o vídeo "Vídeo Secreto" está incorporado na página "Artigo Exclusivo" do site "Corbett Report" em "https://corbettreport.com/artigo-exclusivo"
  Quando o usuário acessa a página "https://corbettreport.com/artigo-exclusivo"
  Então o player de vídeo `iframe[src*="minds.com/embed"]` é exibido
  E uma mensagem `div[class*="private-video-message"]` com "Este vídeo é privado" é exibida
  E o vídeo "Vídeo Secreto" não carrega dentro do player
  E o botão de play `button[aria-label="Play"]` não está visível

Cenário: Vídeo Minds excluído incorporado exibe mensagem de indisponibilidade
  Dado que um vídeo do Minds "Vídeo Removido" foi excluído
  E que o vídeo "Vídeo Removido" estava incorporado na página "Artigo Antigo" do site "Corbett Report" em "https://corbettreport.com/artigo-antigo"
  Quando o usuário acessa a página "https://corbettreport.com/artigo-antigo"
  Então o player de vídeo `iframe[src*="minds.com/embed"]` é exibido
  E uma mensagem `div[class*="deleted-video-message"]` com "Este vídeo não está mais disponível" é exibida
  E o vídeo "Vídeo Removido" não carrega dentro do player
  E o botão de play `button[aria-label="Play"]` não está visível

Cenário: Player de vídeo incorporado exibe controles padrão ao carregar
  Dado que um vídeo público do Minds "Vídeo com Controles" existe
  E que o vídeo "Vídeo com Controles" está incorporado na página "Artigo de Vídeos" do site "Corbett Report" em "https://corbettreport.com/artigo-videos"
  Quando o usuário acessa a página "https://corbettreport.com/artigo-videos"
  Então o player de vídeo `iframe[src*="minds.com/embed"]` é exibido
  E o botão de play/pause `button[aria-label="Play"]` é visível
  E o controle de volume `button[aria-label="Volume"]` é visível
  E a barra de progresso `div[aria-label="Barra de progresso"]` é visível
  E o botão de tela cheia `button[aria-label="Tela Cheia"]` é visível