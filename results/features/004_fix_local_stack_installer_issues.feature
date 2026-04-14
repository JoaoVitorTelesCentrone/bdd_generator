# Story: Fix local stack installer issues
# Model: flash | Score: 6.6/10

Funcionalidade: Correção de Problemas do Instalador da Stack Local

Cenário: Instalação bem-sucedida da stack local em ambiente limpo
  Dado que o sistema operacional está em um estado limpo
  E que os pré-requisitos "Docker", "Node.js" e "Java" estão instalados
  Quando o usuário executa o instalador da stack local via "install.sh --headless"
  Então a mensagem "Instalação concluída com sucesso!" é exibida no console
  E o serviço "nginx" está "rodando" na porta "80"
  E o serviço "mysql" está "rodando" na porta "3306"
  E o diretório "/opt/local-stack/bin" contém os executáveis da stack

Cenário: Falha na instalação devido a pré-requisito Docker ausente
  Dado que o serviço "docker" não está instalado no sistema
  Quando o usuário executa o instalador da stack local via "install.sh"
  Então a mensagem de erro "Docker não encontrado. Por favor, instale o Docker antes de prosseguir." é exibida no console
  E o código de saída do processo é "1"
  E o diretório "/opt/local-stack" não existe ou está vazio

Cenário: Falha na instalação devido a conflito na porta 80
  Dado que o processo "apache2" está "escutando" na porta "80"
  Quando o usuário executa o instalador da stack local via "install.sh"
  Então a mensagem de aviso "Porta 80 já em uso. Tente liberar a porta ou configurar uma porta alternativa." é exibida no console
  E o instalador solicita "Deseja continuar com a porta alternativa (8080)? [s/N]"
  E o serviço "nginx" não está "rodando" na porta "80"

Cenário: Falha na instalação devido a permissões insuficientes de escrita
  Dado que o usuário atual não possui permissões de escrita no diretório "/opt"
  Quando o usuário executa o instalador da stack local via "install.sh"
  Então a mensagem de erro "Permissão negada ao tentar escrever em '/opt/local-stack'. Por favor, execute como administrador." é exibida no console
  E o código de saída do processo é "1"
  E o diretório "/opt/local-stack" não existe

Cenário: Verificação da funcionalidade básica do servidor web após instalação
  Dado que a stack local foi instalada com sucesso
  E que o serviço "nginx" está "rodando" na porta "80"
  Quando o usuário acessa a URL "http://localhost/"
  Então a página exibe o título "Bem-vindo à Stack Local" no elemento `h1`
  E o código de status HTTP da resposta é "200"

Cenário: Verificação da conexão com o banco de dados após instalação
  Dado que a stack local foi instalada com sucesso
  E que o serviço "mysql" está "rodando" na porta "3306"
  Quando o usuário executa o comando "mysql -u root -p -e 'SELECT VERSION();'" no terminal
  E insere a senha "root" quando solicitado
  Então a versão do MySQL é exibida no console
  E o comando retorna um código de saída "0"

Cenário: Interrupção da instalação e necessidade de nova execução limpa
  Dado que o instalador da stack local está em progresso
  Quando o processo do instalador é "encerrado abruptamente"
  E o usuário executa o instalador da stack local via "install.sh --clean-install"
  Então a mensagem "Inicializando nova instalação..." é exibida no console
  E o diretório "/opt/local-stack" é "limpo" antes de iniciar a nova instalação
  E a mensagem "Instalação concluída com sucesso!" é exibida no console