# Story: Boost inventory: Add boosts to Discovery
# Model: flash | Score: 4.8/10

Cenário: Conteúdo impulsionado aparece com destaque no feed Discovery
  Dado que um administrador criou um impulsionamento válido para o conteúdo "Minha Postagem Incrível" (ID: 12345) com duração de 24 horas
  E que o impulsionamento está ativo
  Quando um usuário acessa o feed "Discovery"
  Então o conteúdo "Minha Postagem Incrível" deve ser exibido com destaque
  E o conteúdo deve conter um rótulo visível "Promovido"

Cenário: Impulsionamento expira e conteúdo retorna à exibição normal
  Dado que um administrador criou um impulsionamento para o conteúdo "Oferta Especial" (ID: 67890) com duração de 1 minuto
  E que o impulsionamento expirou após 1 minuto
  Quando um usuário acessa o feed "Discovery"
  Então o conteúdo "Oferta Especial" deve ser exibido como um item comum
  E o conteúdo não deve exibir o rótulo "Promovido"

Cenário: Nenhum impulsionamento ativo exibe apenas conteúdo orgânico no Discovery
  Dado que não há impulsionamentos ativos configurados no sistema
  Quando um usuário acessa o feed "Discovery"
  Então o feed deve exibir apenas conteúdo orgânico
  E nenhum conteúdo deve exibir o rótulo "Promovido"

Cenário: Tentativa de criação de impulsionamento com duração inválida
  Dado que um administrador está na interface de criação de impulsionamento
  Quando o administrador tenta criar um impulsionamento para o conteúdo "Notícia Urgente" (ID: 11223) com duração de -5 horas
  Então uma mensagem de erro "Duração inválida" deve ser exibida
  E o impulsionamento não deve ser criado

Cenário: Tentativa de criação de impulsionamento para conteúdo inexistente
  Dado que um administrador está na interface de criação de impulsionamento
  Quando o administrador tenta criar um impulsionamento para um conteúdo com ID "ID_INEXISTENTE"
  Então uma mensagem de erro "Conteúdo não encontrado" deve ser exibida
  E o impulsionamento não deve ser criado