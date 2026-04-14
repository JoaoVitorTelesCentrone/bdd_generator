# Story: YouTube sync double-posts when video is edited on YouTube
# Model: flash | Score: 4.8/10

Funcionalidade: Sincronização de Vídeos do YouTube sem Duplicação em Edições

Cenário: Sincronização inicial de um vídeo novo cria um único post
  Dado que o usuário "canal_minds@exemplo.com" possui seu canal do YouTube "Meu Canal YT" conectado ao Minds
  E que um novo vídeo "ID_VIDEO_123" com título "Meu Primeiro Vídeo" é publicado no YouTube
  Quando o serviço de sincronização do YouTube é executado
  Então um único post de atividade `div[data-post-id="ID_POST_VIDEO_123"]` é criado no Minds
  E o post `div[data-post-id="ID_POST_VIDEO_12