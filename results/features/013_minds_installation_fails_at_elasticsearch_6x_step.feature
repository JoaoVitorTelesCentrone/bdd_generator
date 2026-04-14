# Story: Minds installation fails at ElasticSearch 6.x+ step
# Model: flash | Score: 2.4/10

Funcionalidade: Falha na Instalação do Minds Local Stack no WSL 2

Cenário: Reprodução do Timeout na Inicialização do ElasticSearch 6.x+ no WSL 2
  Dado que um terminal WSL 2 está aberto e configurado
  E que o projeto "minds-local-stack" está clonado em `/home/user/minds`
  Quando eu executo o script de instalação "setup.sh" na pasta `/home/user/minds`
  Então eu vejo a mensagem "Timeout waiting for Elasticsearch 6.x+" no console
  E que eu vejo o status "Falha" para o serviço "elasticsearch" ao final do log

Cenário: Falha de Instalação