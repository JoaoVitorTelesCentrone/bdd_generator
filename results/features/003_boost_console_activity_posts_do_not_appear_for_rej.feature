# Story: Boost console: Activity posts do not appear for rejected Boosts
# Model: flash | Score: 2.0/10

```gherkin
# language: pt

Funcionalidade: Gerenciamento de Postagens de Atividade no Console de Boosts

  Como usuário do console de Boosts
  Quero que postagens de atividade não apareçam para Boosts rejeitados
  Para que eu tenha clareza sobre o status e ações relevantes

  Cenário: Boost Rejeitado Não Exibe Postagens de Atividade
    Dado que um usuário está logado como "admin@empresa.com"
    E que existe um Boost com ID "boost-rejeitado-1" e status "Rejeitado"
    E que este Boost "boost-rejeitado-1" possui postagens de atividade associadas
    Quando o usuário acessa a URL "https://