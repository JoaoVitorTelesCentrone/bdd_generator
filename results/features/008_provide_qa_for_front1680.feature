# Story: Provide QA for front!1680
# Model: flash | Score: 4.6/10

Funcionalidade: Verificação de Qualidade Frontend

Cenário: Carregamento e Exibição Correta da Página Inicial
  Dado que o navegador está aberto
  Quando o usuário acessa a URL "https://app.example.com/"
  Então o título da página é "Bem-vindo ao Aplicativo" no elemento `head > title`
  E o cabeçalho principal "Bem-vindo!" é exibido no elemento `h1#main-title`
  E o botão de login "Entrar" é visível no elemento `button#login-button`

Cenário: Navegação entre Páginas via Menu Principal
  Dado que o usuário está na página inicial "https://app.example.com/"
  Quando o usuário clica no link "Sobre Nós" no elemento `nav#main-menu a[href="/sobre"]`
  Então o usuário é redirecionado para a URL "https://app.example.com/sobre"
  E o cabeçalho "Nossa História" é exibido no elemento `h1.page-title`

Cenário: Submissão Bem-sucedida de um Formulário de Contato
  Dado que o usuário está na página de contato "https://app.example.com/contato"
  Quando preencho o campo input[name="nome"] com "João Silva"
  E preencho o campo input[name="email"] com "joao.silva@teste.com"
  E preencho o campo textarea[name="mensagem"] com "Gostaria de mais informações sobre seus serviços."
  E clico no botão button[type="submit"] com texto "Enviar Mensagem"
  Então vejo a mensagem ".alert-success" com "Sua mensagem foi enviada com sucesso!"
  E o campo input