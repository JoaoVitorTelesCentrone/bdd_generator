# Story: Auto-enroll users in Open Boosts
# Model: flash | Score: 5.4/10

Funcionalidade: Auto-inscrição de Usuários em Open Boosts

Cenário: Usuário é auto-inscrito quando todas as preferências atendem aos critérios mínimos
  Dado que o usuário "usuario.elegivel@exemplo.com" completou a pesquisa "Construa Seu Algoritmo"
  E sua preferência por "Conteúdo Adulto" é "75"
  E sua preferência por "Opiniões Desafiadoras" é "80"
  E sua preferência por "Desinformação: Deve ser debatida" é "8"
  Quando o sistema processa as respostas da pesquisa
  Então o usuário "usuario.elegivel@exemplo.com" é auto-inscrito em "Open Boosts"
  E o status de inscrição do usuário é "Ativo"

Cenário: Usuário NÃO é auto-inscrito quando a preferência por "Conteúdo Adulto" é insuficiente
  Dado que o usuário "usuario.nao.elegivel.conteudo@exemplo.com" completou a pesquisa "Construa Seu Algoritmo"
  E sua preferência por "Conteúdo Adulto" é "60"
  E sua preferência por "Opiniões Desafiadoras" é "80"
  E sua preferência por "Desinformação: Deve ser debatida" é "8"
  Quando o sistema processa as respostas da pesquisa
  Então o usuário "usuario.nao.elegivel.conteudo@exemplo.com" NÃO é auto-inscrito em "Open Boosts"
  E o status de inscrição do usuário é "Inativo"

Cenário: Usuário NÃO é auto-inscrito quando a preferência por "Opiniões Desafiadoras" é insuficiente
  Dado que o usuário "usuario.nao.elegivel.opiniao@exemplo.com" completou a pesquisa "Construa Seu Algoritmo"
  E sua preferência por "Conteúdo Adulto" é "75"
  E sua preferência por "Opiniões Desafiadoras" é "50"
  E sua preferência por "Desinformação: Deve ser debatida" é "8"
  Quando o sistema processa as respostas da pesquisa
  Então o usuário "usuario.nao.elegivel.opiniao@exemplo.com" NÃO é auto-inscrito em "Open Boosts"
  E o status de inscrição do usuário é "Inativo"

Cenário: Usuário NÃO é auto-inscrito quando a preferência por "Desinformação: Deve ser debatida" é insuficiente
  Dado que o usuário "usuario.nao.elegivel.desinformacao@exemplo.com" completou a pesquisa "Construa Seu Algoritmo"
  E sua preferência por "Conteúdo Adulto" é "75"
  E sua preferência por "Opiniões Desafiadoras" é "80"
  E sua preferência por "Desinformação: Deve ser debatida" é "5"
  Quando o sistema processa as respostas da pesquisa
  Então o usuário "usuario.nao.elegivel.desinformacao@exemplo.com" NÃO é auto-inscrito em "Open Boosts"
  E o status de inscrição do usuário é "Inativo"

Cenário: Usuário NÃO é auto-inscrito quando nenhuma preferência atende aos critérios
  Dado que o usuário "usuario.nenhum.criterio@exemplo.com" completou a pesquisa "Construa Seu Algoritmo"
  E sua preferência por "Conteúdo Adulto" é "30"
  E sua preferência por "Opiniões Desafiadoras" é "20"
  E sua preferência por "Desinformação: Deve ser debatida" é "2"
  Quando o sistema processa as respostas da pesquisa
  Então o usuário "usuario.nenhum.criterio@exemplo.com" NÃO é auto-inscrito em "Open Boosts"
  E o status de inscrição do usuário é "Inativo"

Cenário: Usuário NÃO é auto-inscrito quando a pesquisa "Construa Seu Algoritmo" não foi completada
  Dado que o usuário "usuario.pesquisa.pendente@exemplo.com" NÃO completou a pesquisa "Construa Seu Algoritmo"
  Quando o sistema tenta auto-inscrever usuários
  Então o usuário "usuario.pesquisa.pendente@exemplo.com" NÃO é auto-inscrito em "Open Boosts"
  E o status de inscrição do usuário é "Inativo"

Cenário: Usuário é auto-inscrito quando todas as preferências estão no limite mínimo de inclusão
  Dado que o usuário "usuario.limite.inclusao@exemplo.com" completou a pesquisa "Construa Seu Algoritmo"
  E sua preferência por "Conteúdo Adulto" é "70"
  E sua preferência por "Opiniões Desafiadoras" é "70"
  E sua preferência por "Desinformação: Deve ser debatida" é "7"
  Quando o sistema processa as respostas da pesquisa
  Então o usuário "usuario.limite.inclusao@exemplo.com" é auto-inscrito em "Open Boosts"
  E o status de inscrição do usuário é "Ativo"

Cenário: Usuário NÃO é auto-inscrito quando todas as preferências estão no limite máximo de exclusão
  Dado que o usuário "usuario.limite.exclusao@exemplo.com" completou a pesquisa "Construa Seu Algoritmo"
  E sua preferência por "