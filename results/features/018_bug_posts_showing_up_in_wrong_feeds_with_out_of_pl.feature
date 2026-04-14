# Story: (bug) Posts showing up in wrong feeds, with out of place timestamps
# Model: flash | Score: 4.3/10

**Cenário: Post fixado aparece na posição incorreta após impulsionamento de outros posts**
  Dado que um usuário está logado na plataforma "Minds"
  E que o usuário possui um post fixado com o título "Promoção Especial"
  E que existem outros três posts disponíveis para impulsionar na conta
  Quando o usuário acessa a console de impulsionamento em "https://www.minds.com/boost"
  E o usuário preenche o campo "input[name='boostAmount'][data-post-id='post-1']" com "0.5"
  E o usuário clica no botão "Impulsionar" para o post "button[data-post-id='post-1']"