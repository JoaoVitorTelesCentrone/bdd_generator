# Story: (bug): Cant delete a reply to a comment on a blog post
# Model: flash | Score: 4.7/10

Funcionalidade: Gerenciamento de Respostas em Posts de Blog

  Cenário: Verificar a ausência da opção "Deletar" para respostas em posts de blog
    Dado que estou logado como "autor@blog.com" com senha "Senha123!"
    E que existe um post de blog "Meu Post Incrível" com ID "post-456"
    E que o post "post-456" contém um comentário com ID "comment-789"
    E que o comentário "comment-789" possui uma resposta com ID "reply-123"
    Quando acesso a URL "https://blog.exemplo.com/meu-post-incrivel"
    E quando clico no botão `button[data-testid="reply-options-123"]`
    Então não vejo o elemento `li[data-action="delete-reply"]`
    E que a resposta com ID "reply-123" ainda está visível

  Cenário: Deletar um comentário principal em post de blog (Comportamento Atual e Esperado)
    Dado que estou logado como "autor@blog.com" com senha "Senha123!"
    E que existe um post de blog "Meu Post Incrível" com ID "post-456"
    E que o post "post-456" contém um comentário com ID "comment-789"
    Quando acesso a URL "https://blog.exemplo.com/meu-post-incrivel"
    E quando clico no botão `button[data-testid="comment-options-78