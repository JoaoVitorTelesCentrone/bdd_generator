# Story: (feat): Convert ES reports data to standard format for api return.
# Model: flash | Score: 4.3/10

Funcionalidade: Conversão de Dados de Relatórios Elasticsearch

Cenário: Conversão bem-sucedida de um relatório Elasticsearch completo
  Dado que existe um documento de relatório Elasticsearch com `id` "report-123", `status` "COMPLETO" e `metrics` `{"views": 100, "clicks": 10}`
  Quando o serviço de conversão processa o documento Elasticsearch
  Então o serviço retorna um objeto do tipo `Report`
  E o `Report` retornado possui o `id` "report-123"
  E o `Report` retornado possui o `status` "COMPLETO"
  E o `Report` retornado possui `metrics.views` com o valor numérico `100`

Cenário: Conversão de relatório Elasticsearch com campos opcionais ausentes
  Dado que existe um documento de relatório Elasticsearch com `id` "report-456" e `status` "PENDENTE"
  E o documento não possui o campo `metrics`
  Quando o serviço de conversão processa o documento Elasticsearch
  Então o serviço retorna um objeto do tipo `Report`
  E o `Report` retornado possui o `id` "report-456"
  E o `Report` retornado possui o `status` "PENDENTE"
  E o `Report` retornado possui `metrics` com o valor nulo

Cenário: Conversão de relatório Elasticsearch com tipos de dados numéricos e booleanos
  Dado que existe um documento de relatório Elasticsearch com `id` "report-789", `is_active` `true` e `score` `95.5`
  Quando o serviço de conversão processa o documento Elasticsearch
  Então o serviço retorna um objeto do tipo `Report`
  E o `Report` retornado possui `id` "report-789"
  E o `Report` retornado possui `isActive` com o valor booleano `true`
  E o `Report` retornado possui `score` com o valor numérico `95.5`

Cenário: Campos não mapeados no Elasticsearch são ignorados na conversão
  Dado que existe um documento de relatório Elasticsearch com `id` "report-001" e um campo `es_internal_field` com valor "dados-internos"
  Quando o serviço de conversão processa o documento Elasticsearch
  Então o serviço retorna um objeto do tipo `Report`
  E o `Report` retornado possui o `id` "report-001"
  E o `Report` retornado não possui o campo `es_internal_field`

Cenário: Tratamento de documento Elasticsearch com estrutura inválida
  Dado que existe um documento de relatório Elasticsearch com estrutura JSON inválida `{"id": "report-002", "status": `
  Quando o serviço de conversão tenta processar o documento Elasticsearch
  Então o sistema lança uma exceção do tipo `InvalidReportDataException`
  E a exceção contém a mensagem "Formato de dados do relatório inválido"

Cenário: Tratamento de documento Elasticsearch vazio ou nulo
  Dado que existe um documento de relatório Elasticsearch vazio ou nulo
  Quando o serviço de conversão tenta processar o documento Elasticsearch
  Então o sistema lança uma exceção do tipo `MissingReportDataException`
  E a exceção contém a mensagem "Dados do relatório ausentes ou incompletos"

Cenário: Repositório retorna o modelo Report após conversão
  Dado que o repositório de relatórios está configurado para buscar dados do Elasticsearch
  E que o Elasticsearch contém um documento de relatório com `id` "repo-report-1" e `status` "GERADO"
  Quando o repositório busca o relatório com `id` "repo-report-1"
  Então o repositório retorna um objeto do tipo `Report`
  E o `Report` retornado possui o `id` "repo-report-1"
  E o `Report` retornado possui o `status` "GERADO"