# Story: (feat): admin tools for help desk
# Model: flash | Score: 2.9/10

Funcionalidade: Ferramentas de Administração para Central de Ajuda

Cenário: Admin deleta uma pergunta da central de ajuda com sucesso
  Dado que o admin "admin@empresa.com" está logado no sistema
  E que uma pergunta de ajuda com ID "QUEST001" e título "Problema de Login" existe
  Quando o admin acessa a página de detalhes da pergunta "https://centralajuda.com/admin/perguntas/QUEST001"
  E o admin clica no botão `button[data-testid="btn-deletar-pergunta"]`
  E o admin clica no botão `button[data-testid="btn-confirmar-exclusao"]` no modal de confirmação