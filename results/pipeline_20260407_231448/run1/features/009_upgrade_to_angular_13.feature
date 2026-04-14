# Story: Upgrade to Angular 13
# Model: flash | Score: 7.5/10

Cenário: Atualização bem-sucedida do Angular para a versão 13
  Dado que o projeto Angular está na versão "12.x.x"
    E a versão do Node.js é "14.x.x"
    E a versão do NPM é "6.x.x"
  Quando eu executo o comando de atualização para Angular "13"
    E eu compilo o projeto
    E eu implanto a aplicação no ambiente de "homologação"
  Então o arquivo "package.json" deve exibir a versão "13.x.x" para todos os pacotes "@angular/*"
    E o comando "ng version" deve reportar Angular CLI "13.x.x" e Angular Core "13.x.x"
    E a aplicação deve compilar com sucesso sem "erros críticos"
    E a aplicação deve iniciar e carregar com sucesso no ambiente de "homologação"
    E a aplicação deve ser implantável com sucesso no ambiente de "homologação"

Cenário: Verificação de funcionalidades existentes após a atualização
  Dado que a aplicação Angular foi atualizada com sucesso para a versão "13.x.x"
    E a aplicação está rodando no ambiente de "desenvolvimento"
  Quando eu executo a suíte de "testes automatizados E2E"
    E eu navego por todas as "funcionalidades críticas" da aplicação
  Então todos os "50 cenários de testes E2E" devem passar com sucesso
    E todas as "funcionalidades críticas" devem operar conforme o esperado
    E não deve haver "regressões visuais" nos componentes da interface
    E nenhum "novo bug crítico ou maior" deve ser identificado

Cenário: Compatibilidade de dependências de terceiros com Angular 13
  Dado que o projeto Angular foi atualizado para a versão "13.x.x"
    E as dependências de terceiros foram atualizadas para versões compatíveis
  Quando eu compilo a aplicação
    E eu executo a aplicação em ambiente de "desenvolvimento"
  Então a aplicação deve compilar com sucesso sem "erros de dependência"
    E as bibliotecas "rxjs 7.x.x" e "@angular/material 13.x.x" devem funcionar corretamente
    E não deve haver "erros em tempo de execução" relacionados a dependências de terceiros

Cenário: Manutenção do desempenho da aplicação pós-upgrade
  Dado que a aplicação Angular foi atualizada para a versão "13.x.x"
    E o tempo de carregamento da página inicial era "2.5s" antes do upgrade
    E o consumo de memória do navegador era "80MB" antes do upgrade
  Quando eu acesso a "página inicial" da aplicação em um navegador "Google Chrome"
    E eu monitoro as métricas de desempenho
  Então o tempo de carregamento da "página inicial" deve ser menor ou igual a "2.5s"
    E o consumo de memória do navegador deve ser menor ou igual a "80MB"
    E a aplicação deve manter a "responsividade" anterior ao upgrade

Cenário: Manutenção da compatibilidade com navegadores suportados
  Dado que a aplicação Angular foi atualizada para a versão "13.x.x"
    E a aplicação suportava "Google Chrome", "Mozilla Firefox" e "Microsoft Edge"
  Quando eu acesso a aplicação em um navegador "Google Chrome"