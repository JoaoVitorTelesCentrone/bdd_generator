# Story: Autoplay next video triggers even when writing a comment
# Model: flash | Score: 2.6/10

**Funcionalidade: Controle de Autoplay do Próximo Vídeo ao Comentar**

**Cenário: Autoplay do próximo vídeo é pausado ao digitar um comentário**
  Dado que o usuário está logado na plataforma Minds
  E que o usuário está na página do vídeo "https://www.minds.com/newsfeed/1204885945477804032"
  E que a funcionalidade de autoplay está ativada
  E que o vídeo de título "Título do Vídeo Atual" está em reprodução no elemento #video-player
  Quando o usuário digita "Este é um comentário de teste" no campo de texto textarea[placeholder="Escreva um comentário..."]