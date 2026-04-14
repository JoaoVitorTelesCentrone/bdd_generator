# Story: Spike: Create NIP for Delegated Event Signing
# Model: flash | Score: 4.2/10

Funcionalidade: Delegação de Assinatura de Eventos (NIP)

Cenário: Geração bem-sucedida de um token de delegação válido
  Dado que o usuário "Alice" possui uma chave privada válida
  Quando "Alice" solicita a criação de um token de delegação com permissão para o tipo de evento "1", para a chave pública "Bob" e com validade de "24" horas
  Então o sistema retorna um token de delegação "eyJ..." no formato NIP para assinatura delegada
  E o token "eyJ..." contém a chave pública do delegador "Alice" no campo `pubkey`
  E o token "eyJ..." contém a chave pública do delegado "Bob" no campo `delegatee_pubkey`
  E o token "eyJ..." especifica o tipo de evento permitido "1" no campo `event_kind`
  E o token "eyJ..." possui uma assinatura válida do delegador no campo `signature`

Cenário: Delegação de assinatura utilizada com sucesso para um evento permitido
  Dado que o usuário "Alice" gerou um token de delegação "eyJ..." para o tipo de evento "1" para a chave pública "Bob"
  Quando "Bob" envia uma requisição de assinatura para um evento do tipo "1" usando o token de delegação "eyJ..."
  Então o sistema retorna o evento assinado com sucesso
  E o evento assinado possui uma assinatura válida no campo `sig`
  E o sistema de validação de eventos Nostr aceita o evento como válido para "Alice"

Cenário: Tentativa de assinar um evento com tipo não permitido falha
  Dado que o usuário "Alice" gerou um token de delegação "eyJ..." para o tipo de evento "1" para a chave pública "Bob"
  Quando "Bob" envia uma requisição de assinatura para um evento do tipo "2" usando o token de delegação "eyJ..."
  Então o sistema retorna uma mensagem de erro `error_code: 400` com "Tipo de evento não permitido pela delegação"
  E o evento não é assinado

Cenário: Tentativa de assinar um evento com token de delegação expirado falha
  Dado que o usuário "Alice" gerou um token de delegação "eyJ..." para o tipo de evento "1" para a chave pública "Bob" com validade de "1" minuto
  E que o tempo atual é "2" minutos após a geração do token
  Quando "Bob" envia uma requisição de assinatura para um evento do tipo "1" usando o token de delegação "eyJ..."
  Então o sistema retorna uma mensagem de erro `error_code: 401` com "Token de delegação expirado"
  E o evento não é assinado

Cenário: Tentativa de assinar um evento com token de delegação inválido ou malformado falha
  Dado que o delegado "Bob" tenta assinar um evento
  Quando "Bob" envia uma requisição de assinatura usando um token de delegação "token_malformado_abc" inválido
  Então o sistema retorna uma mensagem de erro `error_code: 400` com "Formato do token de delegação inválido"
  E o evento não é assinado

Cenário: Geração de token de delegação com tempo de validade máximo excedido falha
  Dado que o usuário "Alice" possui uma chave privada válida
  Quando "Alice" solicita a criação de um token de delegação com permissão para o tipo de evento "1", para a chave pública "Bob" e com validade de "100" anos (excedendo o limite)
  Então o sistema retorna uma mensagem de erro `error_code: 400` com "Tempo de validade excede o limite máximo permitido"
  E nenhum token de delegação é gerado