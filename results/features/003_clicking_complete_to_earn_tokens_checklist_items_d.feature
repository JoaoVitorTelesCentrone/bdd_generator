# Story: Clicking "Complete to earn tokens" checklist items doesn't work
# Model: flash | Score: 4.7/10

Cenário: Clicar no item "Selecionar tags" redireciona corretamente
  Dado que o usuário está logado e visualiza a lista de verificação 'Completar para ganhar tokens'
  E o item "Selecionar tags" está pendente de conclusão
  Quando o usuário clica no item "Selecionar tags"
  Então o usuário é redirecionado para a página de seleção de tags

Cenário: Clicar no item "Configurar canal" redireciona corretamente
  Dado que o usuário está logado e visualiza a lista de verificação 'Completar para ganhar tokens'
  E o item "Configurar canal" está pendente de conclusão
  Quando o usuário clica no item "Configurar canal"
  Então o usuário é redirecionado para a página de configuração do canal

Cenário: Clicar no item "Verificar unicidade" redireciona corretamente
  Dado que o usuário está logado e visualiza a lista de verificação 'Completar para ganhar tokens'
  E o item "Verificar unicidade" está pendente de conclusão
  Quando o usuário clica no item "Verificar unicidade"
  Então o usuário é redirecionado para a página de verificação de unicidade

Cenário: Clicar em um item já concluído permite revisitar a tarefa
  Dado que o usuário está logado e visualiza a lista de verificação 'Completar para ganhar tokens'
  E o item "Selecionar tags" já foi marcado como concluído
  Quando o usuário clica no item "Selecionar tags"
  Então o usuário é redirecionado para a página de seleção de tags

Cenário: Usuário não logado é impedido de acessar tarefas da lista
  Dado que o usuário não está logado na plataforma
  E o usuário visualiza a lista de verificação 'Completar para ganhar tokens'
  Quando o usuário clica no item "Selecionar tags"
  Então o usuário é redirecionado para a página de login ou registro