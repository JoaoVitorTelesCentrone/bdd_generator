# Story: Gather requirements for improving refer flow
# Model: flash | Score: 5.4/10

Cenário: Descoberta Facilitada do Programa de Indicação
  Dado que o usuário "usuario@email.com" está logado na plataforma
  Quando o usuário clica no ícone de menu principal "#mainMenuIcon"
  Então vejo a opção "Indique e Ganhe" com o seletor "#referralMenuItem" no menu principal

Cenário: Exibição Clara dos Incentivos para o Indicador
  Dado que o usuário "indicador@email.com" está logado e na página de indicações em "/referrals"
  Quando o usuário visualiza o conteúdo da página
  Então vejo o título "Indique Amigos e Ganhe Tokens" com o seletor "#referralPageTitle"
  E vejo a descrição "Convide seus amigos para Minds e ganhe 5 tokens por cada cadastro bem-sucedido!" no seletor "#referrerIncentiveText"
  E vejo a descrição "Seu amigo também ganha 2 tokens ao se cadastrar!" no seletor "#refereeIncentiveText"

Cenário: Compartilhamento Bem-Sucedido do Link de Indicação
  Dado que o usuário "usuario@email.com" está logado e na página de indicações em "/referrals"
  Quando o usuário clica no botão "Copiar Link" com o seletor "#copyReferralLinkButton"
  Então o link de indicação "https://www.minds.com/join?ref=usuario@email.com" é copiado para a área de transferência

Cenário: Novo Usuário Cadastrando-se via Link de Indicação Válido
  Dado que um novo usuário acessa a URL de indicação "https://www.minds.com/join?ref=indicador@email.com"
  Quando o novo usuário preenche o campo "Email" com "novo.membro@email.com", o campo "Senha" com "SenhaSegura123" e clica no botão "Registrar" com o seletor "#registerButton"
  Então o novo usuário é redirecionado para a página "/dashboard"