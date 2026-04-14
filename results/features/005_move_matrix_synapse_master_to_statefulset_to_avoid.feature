# Story: Move Matrix Synapse Master to StatefulSet to avoid drive mounting issues
# Model: flash | Score: 5.7/10

Cenário: Migração Bem-Sucedida do Matrix Synapse para StatefulSet
  Dado que o ambiente Kubernetes possui um Deployment antigo do Matrix Synapse
  E que este Deployment utiliza PVCs com acesso `ReadWriteOnce`
  Quando o manifesto do StatefulSet do Matrix Synapse Master é aplicado
  Então os pods do StatefulSet são criados e inicializados com sucesso
  E o serviço Matrix Synapse Master está operacional

Cenário: Validação da Resolução de Conflito de Montagem de Drive
  Dado que o StatefulSet do Matrix Synapse Master está implantado
  E que cada réplica de pod possui seu próprio PVC dedicado
  Quando múltiplos pods do StatefulSet são escalados simultaneamente
  Então todos os pods iniciam sem erros de montagem de drive
  E cada pod acessa seu respectivo PVC sem conflitos

Cenário: Garantia de Anexo Único de PVC por Pod
  Dado que o StatefulSet do Matrix Synapse Master está em execução
  E possui 3 réplicas ativas
  Quando a configuração dos PVCs anexados é inspecionada
  Então cada pod do StatefulSet está vinculado a um único PVC exclusivo
  E nenhum PVC está sendo acessado por mais de um pod

Cenário: Comportamento de Escala do StatefulSet
  Dado que o StatefulSet do Matrix Synapse Master está com 1 réplica
  E o PVC correspondente está montado
  Quando o número de réplicas é aumentado para 5
  Então 4 novos pods são criados e iniciados com sucesso
  E 4 novos PVCs são provisionados e montados para os novos pods

Cenário: Reinício de Pods e Persistência de Dados
  Dado que o StatefulSet do Matrix Synapse Master está em execução
  E um pod `matrix-synapse-master-0` possui dados persistidos em seu PVC
  Quando o pod `matrix-synapse-master-0` é excluído
  Então um novo pod `matrix-synapse-master-0` é criado e iniciado
  E o novo pod monta o PVC original, acessando os dados persistidos