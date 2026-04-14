# Story: Auto-enroll users in Open Boosts
# Model: flash | Score: 6.1/10

Funcionalidade: Inscrição Automática de Usuários em Open Boosts

Cenário: Usuário é inscrito automaticamente ao atender todos os critérios da pesquisa
  Dado que o usuário "usuario_completo@email.com" preencheu a pesquisa "Construa Seu Algoritmo"
  E que a resposta para "Eu prefiro: Conteúdo maduro" é "75" `input[name="matureContent"]`
  E que a resposta para "Eu prefiro: Opiniões desafiadoras" é "80" `input[name="challengingOpinions"]`
  E que a resposta para "Desinformação: Deve ser debatida" é "8" `input[name="misinformationDebate"]`
  Quando o sistema processa as respostas da pesquisa do usuário "usuario_completo@email.com"
  Então o usuário "usuario_completo@email.com" é inscrito automaticamente em "Open Boosts"
  E o status de visualização de "Open Boosts" do usuário é "Ativado" `user-profile[data-user-id="usuario_completo"] span[data-feature="open-boosts-status"]`

Cenário: Usuário não é inscrito se "Conteúdo maduro" for exatamente o limite (69)
  Dado que o usuário "usuario_limite_maduro@email.com" preencheu a pesquisa "Construa Seu Algoritmo"
  E que a resposta para "Eu prefiro: Conteúdo maduro" é "69" `input[name="matureContent"]`
  E que a resposta para "Eu prefiro: Opiniões desafiadoras" é "80" `input[name="challengingOpinions"]`
  E que a resposta para "Desinformação: Deve ser debatida" é "8" `input[name="misinformationDebate"]`
  Quando o sistema processa as respostas da pesquisa do usuário "usuario_limite_maduro@email.com"
  Então o usuário "usuario_limite_maduro@email.com" não é inscrito automaticamente em "Open Boosts"
  E o status de visualização de "Open Boosts" do usuário é "Desativado" `user-profile[data-user-id="usuario_limite_maduro"] span[data-feature="open-boosts-status"]`

Cenário: Usuário não é inscrito se "Opiniões desafiadoras" for exatamente o limite (69)
  Dado que o usuário "usuario_limite_opiniao@email.com" preencheu a pesquisa "Construa Seu Algoritmo"
  E que a resposta para "Eu prefiro: Conteúdo maduro" é "75" `input[name="matureContent"]`
  E que a resposta para "Eu prefiro: Opiniões desafiadoras" é "69" `input[name="challengingOpinions"]`
  E que a resposta para "Desinformação: Deve ser debatida" é "8" `input[name="misinformationDebate"]`
  Quando o sistema processa as respostas da pesquisa do usuário "usuario_limite_opiniao@email.com"
  Então o usuário "usuario_limite_opiniao@email.com" não é inscrito automaticamente em "Open Boosts"
  E o status de visualização de "Open Boosts" do usuário é "Desativado" `user-profile[data-user-id="usuario_limite_opiniao"] span[data-feature="open-boosts-status"]`

Cenário: Usuário não é inscrito se "Desinformação: Deve ser debatida" for exatamente o limite (6)
  Dado que o usuário "usuario_limite_desinfo@email.com" preencheu a pesquisa "Construa Seu Algoritmo"
  E que a resposta para "Eu prefiro: Conteúdo maduro" é "75" `input[name="matureContent"]`
  E que a resposta para "Eu prefiro: Opiniões desafiadoras" é "80" `input[name="challengingOpinions"]`
  E que a resposta para "Desinformação: Deve ser debatida" é "6" `input[name="misinformationDebate"]`
  Quando o sistema processa as