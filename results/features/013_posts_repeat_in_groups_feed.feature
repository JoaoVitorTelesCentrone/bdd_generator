# Story: Posts repeat in Groups feed
# Model: flash | Score: 2.4/10

Funcionalidade: Prevenção de Duplicação de Posts no Feed de Grupos

Cenário: Um único post publicado aparece uma única vez no feed de um grupo
  Dado que o usuário "membro@exemplo.com" está logado
  E que o usuário é membro do grupo "Comunidade de Música" (ID: 569272650258460672)
  E que o post "Show de Talentos Online" foi publicado no grupo "Comunidade de Música"
  Quando o usuário acessa o feed do grupo "Comunidade de Música" na URL "https://www.minds.com/groups/profile/5692726502