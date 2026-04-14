# Story: Discontinue holding rewards
# Model: flash | Score: 2.4/10

Funcionalidade: Descontinuação das Recompensas Diárias por Holding

Cenário: Usuário com tokens em holding não recebe recompensas diárias após descontinuação
  Dado que o usuário "Alice" possui "1000" tokens MINDS em sua carteira `span[data-testid="minds-balance"]`
  E que o programa de recompensas por holding foi descontinuado
  E que a data atual é posterior à data de descontinuação
  Quando o sistema executa o processamento diário de recompensas
  Então o saldo de recompensas por holding do usuário "Alice" `span[data-testid="holding-rewards-balance"]` permanece inalterado
  E o histórico de transações `div[data-testid="transaction-history"]` não exibe uma nova entrada de "Recompensa por Holding"
  E o usuário "Alice" não recebe uma notificação `div[data-testid="notification-badge"]` de nova recompensa

Cenário