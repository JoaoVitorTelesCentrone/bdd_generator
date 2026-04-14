# Story: A-B test new Minds homepage / guest mode
# Model: flash | Score: 5.6/10

Cenário: Usuário é direcionado para a nova homepage (Variante A)
  Dado que o usuário não está logado
  E que a distribuição do A/B test o atribui à Variante A
  Quando o usuário acessa a URL raiz do Minds
  Então a "Nova Homepage" deve ser exibida
  E a variante "A" deve ser registrada para o usuário

Cenário: Usuário é direcionado para a homepage atual (Controle B)
  Dado que o usuário não está logado
  E que a distribuição do A/B test o atribui ao Controle B
  Quando o usuário acessa a URL raiz do Minds
  Então a "Homepage Atual" deve ser exibida
  E a variante "B" deve ser registrada para o usuário

Cenário: Conversão de registro na Nova Homepage (Variante A)
  Dado que o usuário está visualizando a "Nova Homepage" (Variante A)
  Quando o usuário clica em "Cadastre-se" e completa o formulário com dados válidos
  Então o registro do novo usuário deve ser concluído com sucesso
  E a métrica de conversão da Variante A deve ser incrementada

Cenário: Conversão de registro na Homepage Atual (Controle B)
  Dado que o usuário está visualizando a "Homepage Atual" (Controle B)
  Quando o usuário clica em "Cadastre-se" e completa o formulário com dados válidos
  Então o registro do novo usuário deve ser concluído com sucesso
  E a métrica de conversão do Controle B deve ser incrementada

Cenário: Rastreamento de pageviews na Nova Homepage (Variante A)
  Dado que o usuário está visualizando a "Nova Homepage" (Variante A)
  Quando o usuário navega para 3 páginas diferentes na plataforma
  Então 4 pageviews (homepage + 3) devem ser registrados para o usuário
  E a métrica de pageviews da Variante A deve refletir o total

Cenário: Rastreamento de pageviews na Homepage Atual (Controle B)
  Dado que o usuário está visualizando a "Homepage Atual" (Controle B)
  Quando o usuário navega para 2 páginas diferentes na plataforma
  Então 3 pageviews (homepage + 2) devem ser registrados para o usuário
  E a métrica de pageviews do Controle B deve refletir o total

Cenário: Usuário não registra na Nova Homepage (Variante A)
  Dado que o usuário está visualizando a "Nova Homepage" (Variante A)
  Quando o usuário permanece por 30 segundos e não clica em "Cadastre-se"
  Então nenhum novo registro deve ser concluído
  E a métrica de conversão da Variante A não deve ser incrementada

Cenário: Usuário não registra na Homepage Atual (Controle B)
  Dado que o usuário está visualizando a "Homepage Atual" (Controle B)
  Quando o usuário permanece por 30 segundos e não clica em "Cadastre-se"
  Então nenhum novo registro deve ser concluído
  E a métrica de conversão do Controle B não deve ser incrementada