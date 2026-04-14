# Story: Remove 401s / 404s from sitemaps
# Model: flash | Score: 5.2/10

Funcionalidade: Otimização de Sitemaps para Excluir Erros 401 e 404

Cenário: URL que retorna 404 NÃO é incluída no sitemap
  Dado que a URL "https://meusite.com/pagina-inexistente" retorna o status "404 Not Found"
  Quando o sistema gera o arquivo "sitemap.xml"
  Então o arquivo "sitemap.xml" não contém a URL "https://meusite.com/pagina-inexistente"

Cenário: URL que retorna 401 (requer autenticação) NÃO é incluída no sitemap
  Dado que a URL "https://meusite.com/area-restrita" retorna o status "401 Unauthorized" para rastreadores
  Quando o sistema gera o arquivo "sitemap.xml"
  Então o arquivo "sitemap.xml" não contém a URL "https://meusite.com/area-restrita"

Cenário: URL válida (retorna 200 OK) é incluída no sitemap
  Dado que a URL "https://meusite.com/pagina-valida" retorna o status "200 OK"
  Quando o sistema gera o arquivo "sitemap.xml"
  Então o arquivo "sitemap.xml" contém a URL "https://meusite.com/pagina-valida"

Cenário: URL previamente problemática (404/401) é corrigida e incluída no sitemap
  Dado que a URL "https://meusite.com/pagina-corrigida" anteriormente retornava "404 Not Found"
  E que a URL "https://meusite.com/pagina-corrigida" agora retorna o status "200 OK"
  Quando o sistema gera o arquivo "sitemap.xml"
  Então o arquivo "sitemap.xml" contém a URL "https://meusite.com/pagina-corrigida"

Cenário: URL previamente válida (200 OK) torna-se 404/401 e é removida do sitemap
  Dado que a URL "https://meusite.com/pagina-desativada" anteriormente retornava "200 OK"
  E que a URL "https://meusite.com/pagina-desativada" agora retorna o status "404 Not Found"
  Quando o sistema gera o arquivo "sitemap.xml"
  Então o arquivo "sitemap.xml" não contém a URL "https://meusite.com/pagina-desativada"