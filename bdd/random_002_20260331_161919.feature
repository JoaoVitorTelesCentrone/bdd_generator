# ============================================
# BDD Scenario Suite
# Gerado em: 2026-03-31 16:19:19.211874
# Modelo: deepseek-coder:6.7b
# Total de Cenários: 6
#
# User Story:
# "Switch to app" overlay overlaps Guest Mode banner
#
# Issue: "Switch to app" overlay overlaps Guest Mode banner
# Story Points: 1.0
# ============================================

## Switch to app overlay overlaps Guest Mode banner

Cenário: Overlap do "Switch to app" sobre o banner de Guest Mode
    Dado que o usuário está em um dispositivo móvel (aqui: simulando iOS)
    E o usuário visita a nova página inicial de Guest Mode
    Quando a página é carregada
    Então aparece sobre a tela um "Switch to the app" overlay

Cenário: Usuários não registrados estão mais satisfeitos com o novo sistema de conta convidado (Guest Mode)
    Dado que o usuário é convidado para fazer uma visita pela primeira vez
    Quando ele aceita os termos e condições de uso
    Então um overlay "Switch to app" aparece na parte inferior da tela

Cenário: O usuário escolhe ir para o aplicativo no overlay
    Dado que o usuário vê o overlay "Switch to app"
    Quando ele clica em "Continue with the App"
    Então o usuário é redirecionado para a tela principal do aplicativo

Cenário: O usuário escolhe continuar na versão simplificada (Light Mode) no overlay
    Dado que o usuário vê o overlay "Switch to app"
    Quando ele clica em "Continue in Light Mode"
    Então o usuário é redirecionado para a tela principal de Guest Mode na versão simplificada (Light Mode)

Cenário: O usuário já fez login no aplicativo e não quer voltar à tela inicial do convidado
    Dado que o usuário está logado no aplicativo
    Quando ele vê o overlay "Switch to app"
    Então a opção para continuar na versão simplificada (Light Mode) não é mostrada.

Cenário: O usuário escolhe cancelar na tela de login do aplicativo e não quer ir à versão simplificada (Guest Mode)
    Dado que o usuário está na tela de login do aplicativo
    Quando ele clica em "Cancel"
    Então o usuário é redirecionado para a página inicial da plataforma.