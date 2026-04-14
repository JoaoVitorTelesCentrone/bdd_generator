# Story: Switch out arweave remote config for local node
# Model: flash | Score: 4.5/10

Funcionalidade: Migração para Nó Arweave Local

Cenário: Operação de upload de dados bem-sucedida utilizando o nó local
  Dado que a aplicação está configurada para usar o nó Arweave local "http://localhost:1984"
  E que o nó Arweave local está "operacional"
  Quando a aplicação faz upload do arquivo "documento.txt" com conteúdo "Olá Arweave Local!"
  Então o log da aplicação exibe "Upload de arquivo 'documento.txt' concluído com sucesso"
  E nenhuma requisição de rede é feita para o endpoint "http://arweave.net"

Cenário: Recuperação de dados existentes através do nó local
  Dado que a aplicação está configurada para usar o nó Arweave local "http://localhost:1984"
  E que o nó Arweave local está "operacional"
  E que a transação "TX_ID_EXISTENTE_001" contém os dados "dados_recuperados_teste" no Arweave
  Quando a aplicação solicita a recuperação da transação "TX_ID_EXISTENTE_001"
  Então a aplicação recebe os dados "dados_recuperados_teste"
  E o log da aplicação exibe "Dados da transação 'TX_ID_EXISTENTE_001' recuperados com sucesso"

Cenário: Falha na conexão ao iniciar com nó local inacessível
  Dado que a aplicação está configurada para usar o nó Arweave local "http://localhost:1984"
  E que o nó Arweave local está "inativo"
  Quando a aplicação é inicializada
  Então o log da aplicação exibe "ERRO: Não foi possível conectar ao nó Arweave local em http://localhost:1984"
  E a funcionalidade de interação com Arweave é "indisponível"

Cenário: Verificação de que o nó remoto não é contatado após a migração
  Dado que a aplicação está configurada para usar o nó Arweave local "http://localhost:1984"
  E que o nó Arweave local está "operacional"
  Quando a aplicação executa 3 operações distintas de leitura e escrita Arweave
  Então nenhuma requisição de rede é observada para o endpoint "http://arweave.net"
  E todas as requisições de rede são direcionadas para "http://localhost:1984"

Cenário: Configuração de nó local inválida impede operações Arweave
  Dado que a aplicação está configurada com o nó Arweave local "http://endereco.invalido:1984"
  Quando a aplicação tenta fazer upload do arquivo "relatorio.pdf"
  Então o log da aplicação exibe "ERRO: Endereço do nó Arweave local inválido ou inacessível"
  E a operação de upload é "interrompida" com falha