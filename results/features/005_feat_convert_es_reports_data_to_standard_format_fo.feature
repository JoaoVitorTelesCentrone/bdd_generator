# Story: (feat): Convert ES reports data to standard format for api return.
# Model: flash | Score: 3.4/10

Funcionalidade: Conversão de Dados de Relatórios ES para Formato Padrão da API

Cenário: Conversão e Retorno de Dados Completos do Elasticsearch
  Dado que o sistema está configurado para converter dados de relatórios do Elasticsearch
  E que o Elasticsearch possui um relatório com `_id:"rep123"`, `source.type:"spam"`, `source.createdAt:"2023-01-01T10:00:00Z"`, `source.status:"pending"`, `source.userId:"user456"`, `source.content:"Conteúdo de spam."`
  Quando uma requisição GET é feita para `/api/v1/reports`
  Então a API retorna um