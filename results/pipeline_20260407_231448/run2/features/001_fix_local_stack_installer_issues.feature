# Story: Fix local stack installer issues
# Model: flash | Score: 7.0/10

Funcionalidade: Gerenciamento do Instalador do Stack Local

Cenário: Instalação completa do stack local com sucesso
  Dado que o sistema operacional é "Windows 10"
  E que todos os pré-requisitos de instalação estão "satisfeitos"
  E que o usuário possui "permissões de administrador"
  Quando eu inicio o instalador do stack local
  E eu confirmo o diretório de instalação padrão "C:\Program Files\MeuStackLocal"
  E eu clico no botão "Instalar"
  Então eu visualizo a mensagem de sucesso "Instalação concluída com sucesso!"
  E eu verifico que todos os serviços do stack local estão "iniciados e operacionais"
  E eu verifico que o console administrativo está acessível na porta "8080"

Cenário: Instalação falha devido a pré-requisitos ausentes
  Dado que o sistema operacional é "Windows 10"
  E que o pré-requisito "Java JDK" não está "instalado"
  E que o usuário possui "permissões de administrador"
  Quando eu inicio o instalador do stack local
  Então eu visualizo a mensagem de erro "Pré-requisito ausente: Java JDK"
  E eu verifico que a instalação é "interrompida"

Cenário: Instalação falha devido a permissões insuficientes
  Dado que o sistema operacional é "Windows 10"
  E que todos os pré-requisitos de instalação estão "satisfeitos"
  E que o usuário não possui "permissões de administrador"
  Quando eu inicio o instalador do stack local
  Então eu visualizo a mensagem de erro "Permissões de administrador