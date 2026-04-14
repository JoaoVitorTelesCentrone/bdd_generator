# Story: Refactor experiments to use events instead of contexts
# Model: flash | Score: 4.3/10

Funcionalidade: Refatorar Experimentos para Usar Eventos

Cenário: Usuário é incluído em experimento ao visualizar a variante
  Dado que o usuário não está em nenhum experimento
  E que a página "https://app.exemplo.com/pagina-promocional" contém o "Experimento X" ativo
  Quando o usuário acessa a URL "https://app.exemplo.com/pagina-promocional"
  Então o usuário vê o elemento "#experiment-x-variant-a"
  E o usuário é incluído no "Experimento X" com a "Variante A"

Cenário: Usuário não é incluído se não visualizar a variante do experimento
  Dado que o usuário não está em nenhum experimento
  E que a página "https://app.exemplo.com/pagina-sem-experimento" contém o "Experimento Y" ativo, mas não visível
  Quando o usuário acessa a URL "https://app.exemplo.com/pagina-sem-experimento"
  Então o usuário não vê o elemento "#experiment-y-variant-b"
  E o usuário não é incluído no "Experimento Y"

Cenário: Usuário é incluído em múltiplos experimentos ao visualizar suas variantes
  Dado que o usuário não está em nenhum experimento
  E que a página "https://app.exemplo.com/pagina-com-dois-experimentos" contém "Experimento A" e "Experimento B" ativos
  Quando o usuário acessa a URL "https://app.exemplo.com/pagina-com-dois-experimentos"
  Então o usuário vê o elemento "#experiment-a-variant-control"
  E o usuário vê o elemento "#experiment-b-variant-new-ui"
  E o usuário é incluído no "Experimento A" com a "Variante Control"
  E o usuário é incluído no "Experimento B" com a "Variante New UI"

Cenário: Experimento inativo não inclui o usuário
  Dado que o usuário não está em nenhum experimento
  E que a página "https://app.exemplo.com/pagina-com-experimento-inativo" contém o "Experimento Z" inativo
  Quando o usuário acessa a URL "https://app.exemplo.com/pagina-com-experimento-inativo"
  Então o usuário não vê o elemento "#experiment-z-variant-promo"
  E o usuário não é incluído no "Experimento Z"

Cenário: Persistência do bucketing para usuário que retorna
  Dado que o usuário está incluído no "Experimento X" como "Variante A"
  E que a página "https://app.exemplo.com/pagina-promocional" contém o "Experimento X" ativo
  Quando o usuário acessa a URL "https://app.exemplo.com/pagina-promocional"
  Então o usuário vê o elemento "#experiment-x-variant-a"
  E o usuário permanece na "Variante A" do "Experimento X"

Cenário: Evento de visualização de experimento é registrado para relatórios
  Dado que o usuário não está em nenhum experimento
  E que a página "https://app.exemplo.com/pagina-analitica" contém o "Experimento Relatório" ativo
  Quando o usuário acessa a URL "https://app.exemplo.com/pagina-analitica"
  Então um evento "experiment_viewed" é enviado
  E o evento contém o atributo "experiment_name": "Experimento Relatório"
  E o evento contém o atributo "variant_name": "Variante Teste"