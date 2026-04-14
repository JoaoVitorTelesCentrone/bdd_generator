# Story: Bug Triage and Customer Support
# Model: flash | Score: 8.2/10

Funcionalidade: Gerenciamento de Relatórios de Bug

Cenário: Submissão bem-sucedida de um relatório de bug completo
  Dado que um usuário autenticado está na página de "Relatar um Bug"
  Quando preencho o campo "Título" com "Bug: Imagem de perfil não carrega"
  E preencho o campo "Descrição" com "A imagem de perfil do usuário não é exibida após o upload"
  E preencho o campo "Passos para Reproduzir" com "1. Acessar 'Minha Conta'. 2. Clicar em 'Editar Perfil'. 3. Fazer upload de nova imagem."
  E preencho o campo "Resultado Esperado" com "A imagem de perfil deve ser exibida corretamente"
  E clico no botão "Enviar Relatório"
  Então vejo uma mensagem de sucesso "Relatório de bug enviado com sucesso!"
  E sou redirecionado para a página de "Meus Relatórios"

Cenário: Tentativa de submissão de relatório de bug com campos obrigatórios vazios
  Dado que um usuário autenticado está na página de "Relatar um Bug"
  Quando preencho o campo "Título" com "Bug: Campo obrigatório não validado"
  E deixo o campo "Descrição" vazio
  E deixo o campo "Passos para Reproduzir" vazio
  E clico no botão "Enviar Relatório"
  Então vejo a mensagem de erro "O campo Descrição é obrigatório"
  E vejo a mensagem de erro "O campo Passos para Reproduzir é obrigatório"
  E o relatório de bug não é enviado