# Story: Decide and set A/B percentages for experiment
# Model: flash | Score: 5.9/10

Funcionalidade: Configuração de Percentuais para Experimento A/B

  Cenário: Configurar um novo experimento com divisão 90/10
    DADO que estou na página de configuração de experimentos A/B em "https://app.exemplo.com/experimentos/novo"
    QUANDO preencho "90" no campo `input#percentual-a`
    E preencho "10" no campo `input#percentual-b`
    E clico no botão `button#salvar-configuracao`
    ENTÃO vejo a mensagem de sucesso "Configurações salvas com sucesso." no elemento `.success-message`

  Cenário: Configurar um novo experimento com divisão 50/50
    DADO que estou na página de configuração de experimentos A/B em "https://app.exemplo.com/experimentos/novo"
    QUANDO preencho "50" no campo `input#percentual-a`
    E preencho "50" no campo `input#percentual-b`
    E clico no botão `button#salvar-configuracao`
    ENTÃO vejo a mensagem de sucesso "Configurações salvas com sucesso." no elemento `.success-message`

  Cenário: Tentar salvar com percentuais que não somam 100%
    DADO que estou na página de configuração de experimentos A/B em "https://app.exemplo.com/experimentos/novo"
    QUANDO preencho "60" no campo `input#percentual-a`
    E preencho "30" no campo `input#percentual-b`
    E clico no botão `button#salvar-configuracao`
    ENTÃO vejo a mensagem de erro "A soma dos percentuais deve ser 100%." no elemento `#mensagem-erro-soma`

  Cenário: Tentar salvar com um percentual negativo
    DADO que estou na página de configuração de experimentos A/B em "https://app.exemplo.com/experimentos/novo"
    QUANDO preencho "110" no campo `input#percentual-a`
    E preencho "-10" no campo `input#percentual-b`
    E clico no botão `button#salvar-configuracao`
    ENTÃO vejo a mensagem de erro "Percentuais não podem ser negativos." no elemento `#mensagem-erro-negativo`

  Cenário: Tentar salvar com percentuais não numéricos
    DADO que estou na página de configuração de experimentos A/B em "https://app.exemplo.com/experimentos/novo"
    QUANDO preencho "noventa" no campo `input#percentual-a`
    E preencho "dez" no campo `input#percentual-b`
    E clico no botão `button#salvar-configuracao`
    ENTÃO vejo a mensagem de erro "Apenas valores numéricos são permitidos." no elemento `#mensagem-erro-numerico`

  Cenário: Tentar salvar com um campo de percentual vazio
    DADO que estou na página de configuração de experimentos A/B em "https://app.exemplo.com/experimentos/novo"
    QUANDO preencho "50" no campo `input#percentual-a`
    E não preencho o campo `input#percentual-b`
    E clico no botão `button#salvar-configuracao`
    ENTÃO vejo a mensagem de erro "Ambos os percentuais são obrigatórios." no elemento `#mensagem-erro-obrigatorio`

  Cenário: Configurar um experimento com divisão 0/100
    DADO que estou na página de configuração de experimentos A/B em "https://app.exemplo.com/experimentos/novo"
    QUANDO preencho "0" no campo `input#percentual-a`
    E preencho "100" no campo `input#percentual-b`
    E clico no botão `button#salvar-configuracao`
    ENTÃO vejo a mensagem de sucesso "Configurações salvas com sucesso." no elemento `.success-message`