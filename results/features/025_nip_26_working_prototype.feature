# Story: NIP-26 working prototype
# Model: flash | Score: 3.0/10

Funcionalidade: Gerenciamento de Delegações Nostr (NIP-26)

Cenário: Conceder uma nova delegação para notas de texto
  Dado que o usuário "Alice" está logado e acessa a página "https://app.minds.com/settings/delegations"
  Quando o usuário "Alice" clica no botão `button[data-testid="new-delegation"]`
  E o usuário "Alice" preenche o campo `input[data-testid="delegatee-pubkey"]` com "npub1delegateebexample"
  E o usuário "Alice" seleciona a opção "Notas de Texto (Kind 1)" no `select[data-testid="event-kind-selector"]`
  E o usuário "Alice" seleciona a opção "7 dias" no `select[data-testid="validity-period"]`
  E o usuário "Alice" clica no botão `button[data-testid="grant-delegation"]`
  Então o usuário "Alice" vê a delegação para "npub1delegateebexample" na `list[data-testid="active-delegations-list"]`
  E a delegação exibe "Notas de Texto" e "Válido por 7 dias"

Cenário: Usuário delegado publica uma nota de texto em nome do delegador
  Dado que o usuário "Alice" concedeu delegação para "npub1delegateebexample" para "Notas de Texto (Kind 1)"
  E que o usuário "Bob" (np