# Story: YouTube sync double-posts when video is edited on YouTube
# Model: flash | Score: 3.8/10

Funcionalidade: Prevenção de Duplicação de Posts na Sincronização YouTube

Cenário: Edição do título de um vídeo no YouTube gera post duplicado na Minds
  Dado que o usuário "canal_exemplo@youtube.com" tem um canal YouTube conectado à Minds
  E que o vídeo YouTube "ID_VIDEO_123" com título "Título Original do Vídeo" já foi sincronizado para a Minds
  E que o post original para "ID_VIDEO_123" está visível no feed do usuário em "https://minds.com/feed"
  Quando o título do vídeo YouTube "ID_VIDEO_123" é alterado externamente para "Novo Título Editado"
  E o sistema