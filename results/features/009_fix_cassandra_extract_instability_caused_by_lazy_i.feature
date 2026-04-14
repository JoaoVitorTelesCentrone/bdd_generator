# Story: Fix Cassandra extract instability caused by lazy instantiation of SQLAlchemy `insert` operators
# Model: flash | Score: 4.3/10

Cenário: Resolução da Instabilidade por Instanciação Lazy
  Dado que o serviço de extração Cassandra está configurado com a versão "2.0.10" da biblioteca SQLAlchemy (com a correção aplicada)
  E uma tabela "dados_instaveis" no Cassandra possui "1.000.000" registros com esquema complexo
  Quando um job de extração para a tabela "dados_instaveis" é iniciado via API REST "/api/extract/cassandra?table=dados_instaveis"
  Então o job de extração completa com status "SUCESSO"
  E o log do serviço de extração não contém mensagens de erro com "LazyInstantiationError" ou "ResourceExhaustion"
  E "