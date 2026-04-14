# Story: NIP-26 working prototype
# Model: flash | Score: 5.1/10

Funcionalidade: Protótipo de Processamento de Gorjetas NIP-26

Cenário: Envio bem-sucedido de uma gorjeta
  Dado que o usuário "alice@nostr.com" está logado
  E que o usuário "alice@nostr.com" possui um saldo de "0.01 NIP"
  Quando o usuário acessa a página "https://app.nostr.com/gorjetas/enviar"
  E preenche o campo `input#npub-destinatario` com "npub123destinatario"
  E preenche o campo `input#valor-gorjeta` com "0.001"
  E clica no botão `button#enviar-gorjeta`
  Então vejo a mensagem ".mensagem-sucesso" com "Gorjeta enviada com sucesso para npub123destinatario!"
  E o saldo do usuário "alice@nostr.com" é atualizado para "0.009 NIP"

Cenário: Tentativa de envio de gorjeta com saldo insuficiente
  Dado que o usuário "bob@nostr.com" está logado
  E que o usuário "bob@nostr.com" possui um saldo de "0.0005 NIP"
  Quando o usuário acessa a página "https://app.nostr.com/gorjetas/enviar"
  E preenche o campo `input#npub-destinatario` com "npub456destinatario"
  E preenche o campo `input#valor-gorjeta` com "0.001"
  E clica no botão `button#enviar-gorjeta`
  Então vejo a mensagem ".mensagem-erro" com "Saldo insuficiente para enviar a gorjeta."
  E o saldo do usuário "bob@nostr.com" permanece "0.0005 NIP"

Cenário: Visualização do histórico de gorjetas recebidas
  Dado que o usuário "charlie@nostr.com" está logado
  E que o usuário "charlie@nostr.com" recebeu uma gorjeta de "0.002 NIP" de "npub789remetente"
  Quando o usuário acessa a página "https://app.nostr.com/gorjetas/historico"
  Então a lista `.lista-transacoes` exibe uma transação com "Recebido de npub789remetente"
  E a lista `.lista-transacoes` exibe o valor "0.002 NIP"

Cenário: Visualização do histórico de gorjetas enviadas
  Dado que o usuário "diana@nostr.com" está logado
  E que o usuário "diana@nostr.com" enviou uma gorjeta de "0.0005 NIP" para "npub012destinatario"
  Quando o usuário acessa a página "https://app.nostr.com/gorjetas/historico"
  Então a lista `.lista-transacoes` exibe uma transação com "Enviado para npub012destinatario"
  E a lista `.lista-transacoes` exibe o valor "-0.0005 NIP"

Cenário: Histórico de gorjetas vazio
  Dado que o usuário "eve@nostr.com" está logado
  E que o usuário "eve@nostr.com" não possui transações de gorjetas
  Quando o usuário acessa a página "https://app.nostr.com/gorjetas/historico"
  Então vejo a mensagem ".mensagem-sem-transacoes" com "Nenhuma transação de gorjeta encontrada."
  E o elemento `.lista-transacoes` não é exibido

Cenário: Envio de gorjeta para destinatário inválido
  Dado que o usuário "frank@nostr.com" está logado
  E que o usuário "frank@nostr.com" possui um saldo de "0.01 NIP"
  Quando o usuário acessa a página "https://app.nostr.com/gorjetas/enviar"
  E preenche o campo `input#npub-destinatario` com "npub_invalido"
  E preenche o campo `input#valor-gorjeta` com "0.001"
  E clica no botão `button#enviar-gorjeta`
  Então vejo a mensagem ".mensagem-erro" com "Endereço Nostr (npub) do destinatário inválido."
  E o saldo do usuário "frank@nostr.com" permanece "0.01 NIP"