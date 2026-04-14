📋 PLANO COMPLETO DE REGRAS DE NEGÓCIO
Qualoop - Sistema PDCA de Qualidade de Software

🎯 1. VISÃO DO PRODUTO
1.1 Propósito
Sistema que implementa PDCA automático no ciclo de desenvolvimento de software, transformando requisitos mal definidos em qualidade executável, validável e contínua.
1.2 Valor Entregue

Redução de bugs em produção
Aceleração do desenvolvimento com qualidade
Menos retrabalho
Melhoria contínua do processo de desenvolvimento

1.3 Público-Alvo
Primário:

QA Pleno/Sênior
Tech Leads
Engineering Managers
Product Managers

Secundário:

Desenvolvedores Pleno/Sênior
CTOs de startups/scale-ups

Segmento:

Empresas B2B no Brasil
Times de 5-50 pessoas
Empresas que usam metodologias ágeis


🔄 2. CICLO PDCA DO PRODUTO
2.1 PLAN (Planejar)
Funcionalidades:

Análise de User Story

Input: User Story (texto)
Processo:

Análise de clareza
Identificação de ambiguidades
Verificação de critérios de aceitação
Detecção de lacunas de regra de negócio


Output:

Score de qualidade (0-100)
Lista de problemas encontrados
Sugestões específicas de melhoria




Geração de BDD

Input: User Story validada
Processo:

Geração de cenários em Gherkin
Criação de casos positivos
Criação de casos negativos
Geração de edge cases


Output:

Feature completa em Gherkin
Cenários organizados por prioridade




Análise de Risco

Input: User Story + contexto do projeto
Processo:

Identificação de pontos críticos
Análise de dependências
Cálculo de impacto


Output:

Nível de risco (Baixo/Médio/Alto/Crítico)
Hotspots de risco
Recomendações de mitigação





2.2 DO (Executar)
Funcionalidades:

Checklist de Qualidade

Templates por tipo de feature
Validação de cumprimento de critérios
Registro de execução


Tracking de Execução

Status: Planejado → Em Execução → Validado → Concluído
Histórico de alterações
Responsáveis por etapa



2.3 CHECK (Verificar)
Funcionalidades:

Comparação Planejado vs Executado

Cenários planejados vs testados
Cobertura real vs esperada
Gaps identificados


Análise de Bugs

Classificação de bugs (evitável/inevitável)
Correlação com qualidade da US
Padrões de erro


Métricas de Qualidade

Taxa de bugs por feature
Tempo médio de detecção
Retrabalho por US mal definida



2.4 ACT (Agir/Melhorar)
Funcionalidades:

Recomendações Automáticas

Sugestões baseadas em histórico
Ajuste de padrões
Evolução de checklists


Base de Conhecimento

Problemas recorrentes
Soluções aplicadas
Aprendizados do time


Melhoria Contínua

Atualização de playbooks
Refinamento de templates
Evolução de critérios




💻 3. ARQUITETURA DO PRODUTO
3.1 Componentes
A) CLI (qctl)
Propósito: Ferramenta de linha de comando para uso diário
Comandos principais:
bash# Autenticação
qctl login                    # Login na conta
qctl logout                   # Logout
qctl whoami                   # Ver usuário logado

# Análise
qctl analyze <US>             # Analisar User Story
qctl analyze --file story.txt # Analisar de arquivo

# Geração
qctl bdd <US>                 # Gerar BDD
qctl bdd --output story.feature

# Risco
qctl risk <US>                # Análise de risco

# Histórico
qctl history                  # Ver histórico de análises
qctl history --limit 10

# Status
qctl status                   # Ver uso atual (requests/tokens)
qctl plan                     # Ver plano ativo
Regras do CLI:

Requer autenticação para todos comandos (exceto login/help)
Valida plano e limites antes de executar
Retorna erro claro quando limite atingido
Funciona offline para comandos de histórico local
Atualiza automaticamente quando há nova versão

B) WEB (Dashboard)
Propósito: Gestão, análise e PDCA completo
Módulos:

Dashboard Principal

Score de qualidade do time
Uso atual (requests/tokens)
Últimas análises
Alertas e recomendações


Análise de US

Editor de User Story
Análise em tempo real
Histórico de versões
Comparação antes/depois


Gestão de BDD

Visualização de cenários
Organização por features
Download/Export


PDCA

Visão completa do ciclo
Métricas por etapa
Evolução temporal


Analytics

Qualidade ao longo do tempo
Padrões de erro
ROI do processo


Configurações

Gestão de usuários
Plano e billing
Integrações
Preferências do time




🔐 4. AUTENTICAÇÃO E AUTORIZAÇÃO
4.1 Autenticação
Métodos suportados:

Email + senha
Google OAuth
GitHub OAuth

Fluxo CLI:

Usuário executa qctl login
Sistema abre navegador com página de auth
Usuário faz login
Sistema gera token de acesso (JWT)
Token salvo localmente (~/.qctl/config)
Token enviado em todas requisições

Regras:

Token expira em 30 dias (renovação automática)
Logout invalida token imediatamente
Máximo 5 sessões ativas por usuário
2FA obrigatório para planos Team/Enterprise

4.2 Autorização (Planos)
Free
Limites:

50 requests/mês
100k tokens/mês
Sem histórico (últimos 7 dias apenas)
Sem dashboard avançado
1 usuário
Sem suporte

Acesso:

analyze (limitado)
bdd (limitado)
risk (não)

Pro (R$ 297/usuário/mês)
Limites:

500 requests/mês
1M tokens/mês
Histórico completo (1 ano)
Dashboard completo
Até 5 usuários
Suporte email (48h)

Acesso:

Tudo do Free
risk
Insights PDCA
Export avançado

Team (R$ 997/mês flat)
Limites:

2000 requests/mês
5M tokens/mês
Histórico ilimitado
Dashboard + Analytics
Até 20 usuários
Suporte prioritário (24h)

Acesso:

Tudo do Pro
Analytics avançado
Integrações
API access

Enterprise (R$ 2.500+/mês)
Limites:

Customizado
Tokens negociados
Histórico ilimitado
Tudo customizado
Usuários ilimitados
Suporte dedicado

Acesso:

Tudo
Consultoria
Customização
On-premise (opcional)


💰 5. MODELO DE COBRANÇA
5.1 Estrutura de Custos
Custo por Request (estimado):

Modelo IA barato: R$ 0,005/request
Modelo IA médio: R$ 0,02/request
Modelo IA avançado: R$ 0,10/request

Custo por Token:

Input: $0.20-$3/1M tokens
Output: $0.60-$15/1M tokens

5.2 Controle de Uso
Sistema de Créditos:
Cada ação consome créditos:

analyze simples: 1 crédito
bdd geração: 3 créditos
risk análise: 5 créditos
Insight PDCA: 10 créditos

Limites por Plano:

Free: 50 créditos/mês
Pro: 500 créditos/mês
Team: 2000 créditos/mês
Enterprise: customizado

Regras de Limite:

Requests contados em tempo real
Tokens contados após resposta da IA
Limite verificado ANTES da execução
Se ultrapassar: bloqueio imediato
Reset todo dia 1º do mês
Compra de créditos extras: R$ 1/crédito (Pro+)

5.3 Billing
Ciclo:

Cobrança mensal (dia da assinatura)
Cartão de crédito (Stripe)
Boleto (Team/Enterprise)

Regras:

Trial: 14 dias grátis (Pro)
Cancelamento: fim do período pago
Upgrade: proporcional imediato
Downgrade: no próximo ciclo
Atraso: 7 dias de grace period → bloqueio


🧠 6. INTELIGÊNCIA DO SISTEMA (IA)
6.1 Análise de User Story
Critérios avaliados:

Clareza (0-25 pontos)

Objetivo bem definido
Linguagem não ambígua
Contexto presente


Completude (0-25 pontos)

Critérios de aceitação
Regras de negócio
Casos de exceção


Testabilidade (0-25 pontos)

Cenários identificáveis
Resultados mensuráveis
Edge cases considerados


Risco (0-25 pontos)

Complexidade técnica
Dependências
Impacto no negócio



Score Final:

0-40: Crítico (não desenvolver)
41-60: Ruim (precisa melhoria)
61-80: Bom (pode melhorar)
81-100: Excelente (pronto)

6.2 Geração de BDD
Template Gherkin:
gherkinFeature: [extraído da US]

  Background:
    [contexto comum]

  Scenario: [Caso positivo principal]
    Given [pré-condição]
    When [ação]
    Then [resultado esperado]

  Scenario: [Caso negativo]
    Given [pré-condição]
    When [ação inválida]
    Then [mensagem de erro esperada]

  Scenario Outline: [Casos múltiplos]
    Given [pré-condição]
    When [ação com <parâmetro>]
    Then [resultado com <expectativa>]
    
    Examples:
      | parâmetro | expectativa |
      | valor1    | resultado1  |
Regras de Geração:

Sempre gerar pelo menos 1 positivo + 1 negativo
Máximo 10 cenários por feature
Usar linguagem da US (português)
Priorizar casos de alto impacto
Incluir edge cases quando risco > Médio

6.3 Análise de Risco
Fatores de Risco:

Complexidade Técnica (peso 30%)

Integrações externas
Lógica complexa
Performance crítica


Impacto no Negócio (peso 40%)

Área crítica (pagamento, auth, etc)
Volume de usuários afetados
Consequência de falha


Histórico (peso 30%)

Área já problemática
Tipo de feature já deu bug
Time com dificuldade nessa área



Níveis de Risco:

Baixo: Score 0-25 (verde)
Médio: Score 26-50 (amarelo)
Alto: Score 51-75 (laranja)
Crítico: Score 76-100 (vermelho)


📊 7. MÉTRICAS E ANALYTICS
7.1 Métricas de Qualidade
Por User Story:

Score médio de qualidade
% de US com score > 80
Tempo médio de análise
Taxa de retrabalho

Por Time:

Evolução de qualidade (mensal)
Bugs evitados (estimado)
Tempo economizado
Maturidade do processo (1-5)

Por Projeto:

Cobertura de cenários BDD
Taxa bugs/feature
Velocity com qualidade

7.2 Dashboard Analytics
Visões:

Visão Geral

Score atual do time
Tendência (↑↓)
Alerts pendentes


Qualidade ao Longo do Tempo

Gráfico de evolução (6 meses)
Comparação com benchmark


Hotspots

Áreas mais problemáticas
Tipos de erro recorrentes
Features de alto risco


ROI

Bugs evitados (estimado)
Horas economizadas
Valor monetário




🔗 8. INTEGRAÇÕES (Roadmap)
8.1 Prioridade 1 (MVP+)

Jira

Sync automático de US
Comentário com análise
Update de status


GitHub

Review de PR
Comentário com sugestões



8.2 Prioridade 2

Slack

Notificações
Comandos via bot


Azure DevOps

Sync de work items



8.3 Prioridade 3

Notion
Linear
Webhooks customizados


🔄 9. FLUXO COMPLETO DO SISTEMA
9.1 Fluxo CLI → API → IA → Resposta
1. Dev executa: qctl analyze "User story aqui"

2. CLI envia request:
   POST /api/analyze
   Headers:
     Authorization: Bearer {token}
   Body:
     {
       "userStory": "texto",
       "action": "analyze"
     }

3. API valida:
   - Token válido?
   - Plano ativo?
   - Tem créditos?
   - Está dentro do limite de tokens?

4. API chama IA:
   - Monta prompt otimizado
   - Envia para modelo
   - Recebe resposta
   - Conta tokens usados

5. API processa:
   - Extrai score
   - Identifica problemas
   - Gera sugestões
   - Salva histórico
   - Atualiza uso

6. API responde:
   {
     "score": 75,
     "status": "good",
     "problems": [...],
     "suggestions": [...],
     "creditsUsed": 1,
     "creditsRemaining": 49
   }

7. CLI exibe resultado formatado
9.2 Fluxo Web
1. Usuário cola US no editor

2. Frontend envia request em tempo real (debounce 500ms)

3. API processa (mesmo fluxo CLI)

4. Frontend atualiza UI:
   - Score visual
   - Problemas listados
   - Sugestões exibidas
   - BDD gerado (se solicitado)

5. Usuário pode:
   - Aceitar sugestões
   - Gerar BDD
   - Salvar no histórico
   - Exportar resultado

🛡️ 10. SEGURANÇA E COMPLIANCE
10.1 Segurança de Dados
Armazenamento:

User Stories: criptografadas em repouso
Tokens: hashed (bcrypt)
Dados sensíveis: nunca em logs

Transmissão:

HTTPS obrigatório
TLS 1.3
Certificate pinning (CLI)

Retenção:

Free: 7 dias
Pro: 1 ano
Team: ilimitado
Enterprise: customizado

LGPD:

Usuário pode exportar dados (JSON)
Usuário pode deletar conta (hard delete após 30 dias)
Opt-out de analytics

10.2 Rate Limiting
Por IP:

100 requests/hora (não autenticado)
1000 requests/hora (autenticado)

Por Usuário:

Conforme plano

Proteção:

DDoS protection (Cloudflare)
Captcha após 5 tentativas de login


📈 11. ROADMAP DE DESENVOLVIMENTO
Fase 1 - MVP (Mês 1-2)
CLI:

 Comandos básicos (login, analyze, bdd)
 Autenticação
 Limite de uso

Web:

 Landing page
 Dashboard simples
 Análise de US
 Geração BDD

Backend:

 API REST
 Integração IA
 Sistema de créditos
 Billing (Stripe)

Fase 2 - PDCA Básico (Mês 3)

 Histórico completo
 Análise de risco
 Métricas básicas
 Score de maturidade

Fase 3 - Analytics (Mês 4)

 Dashboard avançado
 Gráficos de evolução
 Hotspots
 Recomendações automáticas

Fase 4 - Integrações (Mês 5-6)

 Jira
 GitHub
 Slack
 Webhooks

Fase 5 - Enterprise (Mês 7+)

 Multi-tenant
 SSO
 Auditoria
 API pública


🎯 12. REGRAS DE NEGÓCIO CRÍTICAS
12.1 Limites Rígidos

Nunca ultrapassar limite do plano

Bloquear antes de executar
Mensagem clara de upgrade


Token sempre validado

Sem exceções
Expiração rigorosa


Billing falhou = bloqueio imediato

Grace period de 7 dias
Notificação a cada dia



12.2 Qualidade da Resposta

Timeout de IA

Máximo 30s por request
Retry 2x com exponential backoff
Erro claro se falhar


Validação de Output

Score sempre 0-100
BDD sempre em Gherkin válido
Problemas sempre listados


Fallback

Se IA falha → resposta genérica
Nunca deixar usuário sem resposta
Log do erro para análise



12.3 Experiência do Usuário

Performance

API response < 2s (95th percentile)
CLI startup < 500ms
Web load < 3s


Confiabilidade

Uptime > 99.5%
Backup diário
DR plan


Feedback

Loading states claros
Progresso visível
Erros acionáveis




📝 13. DOCUMENTAÇÃO OBRIGATÓRIA
13.1 Para Usuários

 Quick start (5 min)
 Referência de comandos CLI
 Guia de interpretação do score
 FAQs
 Changelog

13.2 Para Desenvolvedores

 API reference
 Webhook docs
 Rate limits
 Error codes
 SDKs (futuro)


🚀 14. ESTRATÉGIA GO-TO-MARKET
14.1 Canais de Aquisição
Primário:

LinkedIn (conteúdo de autoridade)
GitHub (CLI open-source freemium)
Dev.to / Medium (artigos técnicos)

Secundário:

YouTube (tutoriais)
Podcast (guest)
Eventos (palestras)

14.2 Conversão
Funil:

Conteúdo educacional (topo)
Quiz de diagnóstico (meio)
Trial 14 dias (fundo)
Onboarding guiado
Conversão para pago

Meta:

Trial → Pago: 20%
Churn mensal: < 5%
NPS: > 50


⚠️ 15. RISCOS E MITIGAÇÕES
15.1 Riscos Técnicos
RiscoImpactoProbabilidadeMitigaçãoAPI IA instávelAltoMédiaFallback para modelo alternativoCusto de IA explodeAltoBaixaLimite rígido de tokens + alertasPerformance ruimMédioMédiaCache + otimização de promptsSegurança violadaCríticoBaixaPentest + auditoria regular
15.2 Riscos de Negócio
RiscoImpactoProbabilidadeMitigaçãoMercado não pagaAltoMédiaValidação prévia + MVPs testadosConcorrente grandeMédioMédiaFoco em nicho + diferenciaçãoChurn altoAltoMédiaOnboarding forte + suporte ativoRegulação IAMédioBaixaMonitorar legislação + compliance

🎯 16. MÉTRICAS DE SUCESSO (KPIs)
16.1 Produto

Ativação: 60% dos signups fazem 1ª análise
Retenção D7: 40%
Retenção D30: 25%
MAU: 1000 (ano 1)

16.2 Negócio

MRR: R$ 30k (mês 6)
MRR: R$ 100k (ano 1)
CAC: < R$ 500
LTV/CAC: > 3
Payback: < 6 meses

16.3 Qualidade

Uptime: > 99.5%
P95 latency: < 2s
Error rate: < 0.1%
CSAT: > 4.5/5


FIM DO DOCUMENTO DE REGRAS DE NEGÓCIO