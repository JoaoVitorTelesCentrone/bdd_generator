# Story: Create page with links to tools to aide development
# Model: flash | Score: 4.8/10

Cenário: Acesso direto à página de ferramentas e exibição de conteúdo padrão
  Dado que o usuário não está autenticado
  E que as ferramentas "Visual Studio Code", "Docker" e "Git" estão cadastradas com seus links válidos
  Quando o usuário navega diretamente para a URL "/dev-tools"
  Então o título principal "Ferramentas Essenciais para Desenvolvedores" é exibido no elemento `h1#page-title`
  E a lista de ferramentas (`ul#tool-list`) contém 3 itens
  E o item da ferramenta "Visual Studio Code" (`li[data-tool-name="Visual Studio Code"]`) exibe o nome, uma descrição e um link clicável para "https://code.visualstudio