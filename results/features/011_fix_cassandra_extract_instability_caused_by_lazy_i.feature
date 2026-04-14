# Story: Fix Cassandra extract instability caused by lazy instantiation of SQLAlchemy `insert` operators
# Model: flash | Score: 3.7/10

Funcionalidade: Estabilização da Extração de Dados do Cassandra

Cenário: Extração de dados de tabela pequena é concluída com sucesso
  Dado que o módulo de extração de dados está ativo
  E que a tabela "usuarios_teste" no Cassandra contém "100" registros
  E que os operadores `SQLAlchemy insert` foram instanciados corretamente
  Quando o processo de extração de dados para "usuarios_teste" é acionado
  Então o processo de extração registra "sucesso" nos logs
  E o arquivo de saída da extração contém "100" registros

Cenário: Extração de dados de grande volume mantém estabilidade e completude
  Dado que o módulo de extração de dados está ativo
  E que a tabela "logs_auditoria" no Cassandra contém "1 milhão" de registros
  E que os operadores `SQLAlchemy insert` foram instanciados corretamente
  Quando o processo de extração de dados para "logs_auditoria" é acionado
  Então o processo de extração registra "sucesso" nos logs
  E o arquivo de saída da extração contém "1 milhão" de registros
  E a soma de verificação do arquivo de saída corresponde à soma de origem

Cenário: Extração de dados com múltiplas colunas complexas é estável
  Dado que o módulo de extração de dados está ativo
  E que a tabela "configuracoes_sistema" no Cassandra contém "500" registros com "15" colunas complexas
  E que os operadores `SQLAlchemy insert` foram instanciados corretamente
  Quando o processo de extração de dados para "configuracoes_sistema" é acionado
  Então o processo de extração registra "sucesso" nos logs
  E todos os "500" registros são extraídos corretamente
  E nenhuma coluna complexa apresenta truncamento ou erro de formato

Cenário: Tentativas repetidas de extração de dados são consistentes
  Dado que o módulo de extração de dados está ativo
  E que a tabela "eventos_app" no Cassandra contém "10000" registros
  E que os operadores `SQLAlchemy insert` foram instanciados corretamente
  Quando o processo de extração de dados para "eventos_app" é acionado "3" vezes consecutivas
  Então cada processo de extração registra "sucesso" nos logs
  E cada arquivo de saída da extração contém os mesmos "10