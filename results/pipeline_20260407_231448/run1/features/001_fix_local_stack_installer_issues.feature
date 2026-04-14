# Story: Fix local stack installer issues
# Model: flash | Score: 7.4/10

Funcionalidade: Correção de Problemas no Instalador da Stack Local

  Cenário: Instalação Padrão Bem-Sucedida em Windows
    Dado que o sistema operacional é "Windows 10 Pro"
    E que todos os requisitos de sistema são atendidos
    E que não há instalação anterior da stack local
    Quando o usuário executa o instalador
    E seleciona a opção de "Instalação Padrão"
    E aceita os "Termos e Condições"
    Então o instalador deve exibir o "Progresso da Instalação"
    E o instalador deve exibir a mensagem "Instalação Concluída com Sucesso"
    E a stack local deve estar operacional e acessível.

  Cenário: Instalação Personalizada Bem-Sucedida em Ubuntu
    Dado que o sistema operacional é "Ubuntu 22.04 LTS"
    E que todos os requisitos de sistema são atendidos
    E que não há instalação anterior da stack local
    Quando o usuário executa o instalador
    E seleciona a opção "Instalação Personalizada"
    E informa o caminho de instalação "/home/user/dev/mystack"
    Então o instalador deve exibir o "Progresso da Instalação"
    E o instalador deve exibir a mensagem "Instalação Concluída com Sucesso"
    E a stack local deve estar operacional no caminho "/home/user/dev/mystack".

  Cenário: Tratamento de Erro - Pré-requisito Java Ausente
    Dado que o sistema operacional é "Windows 10 Pro"
    E que o "Java Development Kit (JDK) versão 17" não está instalado
    Quando o usuário executa o instalador
    Então o instalador deve exibir a mensagem de erro "JDK 17 não encontrado"
    E o instalador deve sugerir "Baixar JDK 17" com um link.

  Cenário: Desinstalação Limpa da Stack Local
    Dado que a stack local "MyStack" está instalada e operacional
    Quando o usuário inicia o processo de desinstalação
    Então o desinstalador deve remover todos os arquivos da stack local
    E o desinstalador deve exibir a mensagem "Desinstalação Concluída".

  Cenário: Tratamento de Erro - Espaço em Disco Insuficiente
    Dado que o sistema operacional é "Windows 10 Pro"
    E que há "2 GB" de espaço livre em disco
    E que a stack local requer "5 GB" de espaço para instalação
    Quando o usuário executa o instalador e inicia a instalação
    Então o instalador deve exibir a mensagem de erro "Espaço em disco insuficiente"
    E a instalação deve ser abortada.

  Cenário: Tratamento de Erro - Permissões de Administrador Insuficientes
    Dado que o sistema operacional é "Ubuntu 22.04 LTS"
    E que o usuário atual não possui "privilégios de administrador"
    Quando o usuário executa o instalador
    Então o instalador deve exibir a mensagem de erro "Privilégios de administrador necessários"
    E a instalação deve ser abortada.

  Cenário: Tratamento de Erro - Problemas de Conexão durante Download
    Dado que o sistema operacional é "Windows 10 Pro"
    E que a conexão de rede está "ausente"
    Quando o usuário executa o instalador e inicia a instalação
    Então o instalador tenta baixar os componentes necessários
    E o instalador deve exibir a mensagem de erro "Falha ao baixar dependência X: Sem conexão com a internet"
    E a instalação deve ser abortada.

  Cenário: Resolução de Problema Conhecido - Erro de Permissão na Pasta Temporária
    Dado que o sistema operacional é "macOS Ventura"
    E que a versão anterior do instalador falhava com "erro de permissão na pasta /tmp"
    Quando o usuário executa a nova versão do instalador
    Então o instalador deve realizar a instalação com sucesso
    E o instalador não deve exibir o "erro de permissão na pasta /tmp".