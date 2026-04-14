# Story: (bug): Cant delete a reply to a comment on a blog post
# Model: flash | Score: 3.5/10

Funcionalidade: Gerenciamento de Conteúdo em Posts

Cenário: Falha ao tentar excluir uma resposta em um comentário de post de blog próprio
  Dado que o usuário "autor@blog.com" está logado
  E que o usuário "autor@blog.com" é o autor do post de blog "Meu Post Importante" `div[data-testid="post-blog-Meu Post Importante"]`
  E que o post de blog "Meu Post Importante" contém um comentário "Comentário do Usuário A" `div[data-testid="comment-123"]`
  E que o comentário "Comentário do Usuário A" contém uma resposta "Resposta do Usuário B" `div[data-testid="reply