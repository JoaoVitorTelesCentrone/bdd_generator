# Story: Code-based email verifications in mobile app
# Model: flash | Score: 5.1/10

Funcionalidade: Verificação de Email Baseada em Código no Aplicativo Móvel

  Cenário: Verificação de email bem-sucedida com código válido
    Dado que o usuário "usuario@exemplo.com" possui o email não verificado
    E que um código de verificação "123456" foi enviado para "usuario@exemplo.com"
    Quando o usuário digita "123456" no campo input[data-testid="campo-codigo-verificacao"]
    E o usuário clica no botão button[data-testid="botao-verificar"]
    Então o email "usuario@exemplo.com" é marcado como verificado
    E o usuário vê a mensagem ".alert-success" com "Email verificado com sucesso!"
    E o usuário é redirecionado para a URL "https://app.exemplo.com/dashboard"

  Cenário: Falha na verificação de email com código incorreto
    Dado que o usuário "usuario@exemplo.com" possui o email não verificado
    E que um código de verificação "123456" foi enviado para "usuario@exemplo.com"
    Quando o usuário digita "999999" no campo input[data-testid="campo-codigo-verificacao"]
    E o usuário clica no botão button[data-testid="botao-verificar"]
    Então o email "usuario@exemplo.com" permanece não verificado
    E o usuário vê a mensagem ".error-msg" com "Código de verificação inválido."
    E o campo input[data-testid="campo-codigo-verificacao"] exibe um estado de erro

  Cenário: Falha na verificação de email com código expirado
    Dado que o usuário "usuario@exemplo.com" possui o email não verificado
    E que um código de verificação "654321" foi enviado para "usuario@exemplo.com"
    E que o código "654321" expirou há "5" minutos
    Quando o usuário digita "654321" no campo input[data-testid="campo-codigo-verificacao"]
    E o usuário clica no botão button[data-testid="botao-verificar"]
    Então o email "usuario@exemplo.com" permanece não verificado
    E o usuário vê a mensagem ".error-msg" com "Código de verificação expirado. Solicite um novo."
    E o campo input[data-testid="campo-codigo-verificacao"] exibe um estado de erro

  Cenário: Solicitar um novo código de verificação
    Dado que o usuário "usuario@exemplo.com" possui o email não verificado
    E que um código de verificação "111222" foi enviado para "usuario@exemplo.com"
    Quando o usuário clica no botão button[data-testid="botao-reenviar-codigo"]
    Então um novo código de verificação é enviado para "usuario@exemplo.com"
    E o código anterior "111222" é invalidado
    E o usuário vê a mensagem ".alert-info" com "Novo código enviado para seu email."
    E o botão button[data-testid="botao-reenviar-codigo"] é desabilitado por "60" segundos

  Cenário: Interface de usuário para verificação de email
    Dado que o usuário "usuario@exemplo.com" precisa verificar seu email
    E que o usuário está na tela de verificação de email "https://app.exemplo.com/verificar-email"
    Quando a tela de verificação é carregada
    Então o campo input[data-testid="campo-codigo-verificacao"] é exibido
    E o botão button[data-testid="botao-verificar"] é exibido
    E o botão button[data-testid="botao-reenviar-codigo"] é exibido
    E o texto "Verifique seu email" é visível no elemento `h1`
    E o texto "Um código foi enviado para usuario@exemplo.com" é visível no elemento `.info-text`

  Cenário: Limitação de taxa ao reenviar códigos de verificação
    Dado que o usuário "usuario@exemplo.com" possui o email não verificado
    E que o usuário solicitou um código de verificação há "30" segundos
    Quando o usuário clica no botão button[data-testid="botao-reenviar-codigo"]
    Então o usuário vê a mensagem ".error-msg" com "Por favor, aguarde antes de reenviar um novo código."
    E nenhum novo código de verificação é enviado para "usuario@exemplo.com"
    E o botão button[data-testid="botao-reenviar-codigo"] permanece desabilitado por "30" segundos

  Cenário: Verificação de email após alteração de endereço de email
    Dado que o usuário "usuario@exemplo.com" alterou seu email para "novo.email@exemplo.com"
    E que um código de verificação "789012" foi enviado para "novo.email@exemplo.com"
    Quando o usuário digita "789012" no campo input[data-testid="campo-codigo-verificacao"]
    E o usuário clica no botão button[data-testid="botao-verificar"]
    Então o email "novo.email@exemplo.com" é marcado como verificado
    E o usuário vê a mensagem ".alert-success" com "Email verificado com sucesso!"
    E o perfil do usuário exibe "novo.email@exemplo.com" como email principal