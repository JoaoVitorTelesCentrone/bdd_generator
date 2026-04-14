# Story: Fix Cassandra extract instability caused by lazy instantiation of SQLAlchemy `insert` operators
# Model: flash | Score: 3.5/10

```gherkin
Funcionalidade: Estabilização da Extração de Dados para Cassandra

  Cenário: Extração de Dados Padrão para Cassandra
    Dado que o sistema está configurado para extração de dados para Cassandra
    Dado que "5" registros válidos estão disponíveis na fonte de dados "source_db"
    Dado que o serviço de Cassandra está acessível em "cassandra.exemplo.com:9042"
    Quando o endpoint "POST /api/extract/cassandra" é acessado
    Então o código de status "200 OK" é retornado
    Então o banco de dados Cassandra contém "5" registros na tabela "tabela_dados"
    Então o log do sistema em "/var/log/cassandra-extractor.log" contém a mensagem "Extração Cassandra concluída com sucesso"

  Cenário: Extração de Grande Volume de Dados com Estabilidade
    Dado que o sistema está configurado para extração de dados para Cassandra
    Dado que "100000" registros válidos estão disponíveis na fonte de dados "source_db"
    Dado que o serviço de Cassandra está acessível em "cassandra.exemplo.com:9042"
    Quando o endpoint "POST /api/extract/cassandra" é acessado
    Então o código de status "200 OK" é retornado
    Então o banco de dados Cassandra contém "100000" registros na tabela "tabela_dados"
    Então o tempo de execução da extração é de no máximo "120" segundos
    Então o log do sistema em "/var/log/cassandra-extractor.log" não contém erros de "lazy instantiation"

  Cenário: Integridade dos Dados Extraídos para Cassandra
    Dado que o sistema está configurado para extração de dados para Cassandra
    Dado que "3" registros específicos estão disponíveis na fonte de dados "source_db"
    Dado que o serviço de Cassandra está acessível em "cassandra.exemplo.com:9042"
    Quando o endpoint