# Story: (feat): As moderators, we should be able to simultaneously manage the queue.
# Model: flash | Score: 4.4/10

Funcionalidade: Gerenciamento Simultâneo da Fila de Moderação

Cenário: Moderador aprova um item da fila com sucesso
  Dado que o usuário "moderador1@exemplo.com" está logado como moderador
  E o item "post-123" está na fila de moderação com status "pendente"
  Quando o usuário "moderador1@exemplo.com" acessa a página "https://app.com/moderacao/fila"
  E o usuário "moderador1@exemplo.com" clica no botão `button[data-action="approve"][data-item-id="post-123"]`
  Então o item "post-123" é removido da lista de itens `div[data-testid="queue-list"]`
  E o item "post-123" possui o status "aprovado" no sistema

Cenário: Moderador rejeita um item da fila com sucesso
  Dado que o usuário "moderador1@exemplo.com" está logado como moderador
  E o item "comment-456" está na fila de moderação com status "pendente"
  Quando o usuário "moderador1@exemplo.com" acessa a página "https://app.com/moderacao/fila"
  E o usuário "moderador1@exemplo.com" clica no botão `button[data-action="reject"][data-item-id="comment-456"]`
  Então o item "comment-456" é removido da lista de itens `div[data-testid="queue-list"]`
  E o item "comment-456" possui o status "rejeitado" no sistema

Cenário: Dois moderadores aprovam itens diferentes simultaneamente
  Dado que o usuário "moderador1@exemplo.com" e "moderador2@exemplo.com" estão logados
  E o item "post-111" e "comment-222" estão na fila com status "pendente"
  Quando o usuário "moderador1@exemplo.com" clica no botão `button[data-action="approve"][data-item-id="post-111"]`
  E o usuário "moderador2@exemplo.com" clica no botão `button[data-action="approve"][data-item-id="comment-222"]`
  Então o item "post-111" é removido da lista de itens `div[data-testid="queue-list"]`
  E o item "post-111" possui o status "aprovado" no sistema
  E o item "comment-222" é removido da lista de itens `div[data-testid="queue-list"]`
  E o item "comment-222" possui o status "aprovado" no sistema

Cenário: Conflito ao tentar processar o mesmo item por dois moderadores
  Dado que o usuário "moderador1@exemplo.com" e "moderador2@exemplo.com" estão logados
  E o item "image-789" está na fila de moderação com status "pendente"
  Quando o usuário "moderador1@exemplo.com" clica no botão `button[data-action="approve"][data-item-id="image-789"]`
  E quase simultaneamente, o usuário "moderador2@exemplo.com" tenta clicar no botão `button[data-action="reject"][data-item-id="image-789"]`
  Então o item "image-789" é removido da lista de itens `div[data-testid="queue-list"]`
  E o item "image-789" possui o status "aprovado" no sistema
  E o botão `button[data-action="reject"][data-item-id="image-789"]` fica desabilitado para o usuário "moderador2@exemplo.com"
  E o usuário "moderador2@exemplo.com" vê uma mensagem `div[data-testid="toast-message"]` com "Item já foi processado por outro moderador"

Cenário: Fila de moderação é atualizada em tempo real para outros moderadores
  Dado que o usuário "moderador1@exemplo.com" e