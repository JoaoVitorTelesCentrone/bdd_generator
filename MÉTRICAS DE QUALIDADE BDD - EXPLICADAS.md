MÉTRICAS DE QUALIDADE BDD \- EXPLICADAS  
Vou usar exemplos ruins vs bons pra cada métrica ficar cristalina:  
📊 MÉTRICA 1: COBERTURA (0-10)  
O que mede: % das funcionalidades do código/user story que têm cenários BDD correspondentes.  
Exemplo Prático  
User Story:  
Como usuário, quero fazer login no sistema para acessar minha conta.

Critérios de aceitação:  
\- Login com email/senha  
\- Recuperação de senha  
\- Bloqueio após 3 tentativas  
\- Login social (Google/GitHub)  
❌ COBERTURA BAIXA (score: 3/10)  
gherkin  
Cenário: Login bem-sucedido  
  Dado que estou na página de login  
  Quando insiro credenciais válidas  
  Então devo ver minha dashboard  
→ Cobre apenas 1 de 4 critérios \= 25% \= 2.5/10  
✅ COBERTURA ALTA (score: 10/10)  
gherkin  
Cenário: Login com credenciais válidas  
  Dado que estou na página de login  
  Quando insiro "user@email.com" e senha "Pass123"  
  Então devo ser redirecionado para "/dashboard"

Cenário: Recuperação de senha  
  Dado que estou na página de login  
  Quando clico em "Esqueci minha senha"  
  E insiro "user@email.com"  
  Então devo receber um email de recuperação

Cenário: Bloqueio após tentativas falhas  
  Dado que tentei fazer login 3 vezes com senha incorreta  
  Quando tento fazer login novamente  
  Então devo ver "Conta bloqueada temporariamente"

Cenário: Login via Google  
  Dado que estou na página de login  
  Quando clico em "Continuar com Google"  
  E autorizo o acesso  
  Então devo ser redirecionado para "/dashboard"  
→ Cobre 4 de 4 critérios \= 100% \= 10/10  
Como Calcular Programaticamente  
python  
def calcular\_cobertura(user\_story: str, cenarios\_bdd: str) \-\> float:  
    """  
    Extrai critérios de aceitação da user story  
    Verifica quantos são cobertos pelos cenários  
    """  
    \# 1\. Extrai critérios (usando regex ou NLP)  
    criterios \= extrair\_criterios(user\_story)  
    \# Ex: \["login email/senha", "recuperação senha", "bloqueio 3 tentativas", "login social"\]  
      
    \# 2\. Verifica cobertura (busca palavras-chave nos cenários)  
    cobertos \= 0  
    for criterio in criterios:  
        palavras\_chave \= extrair\_palavras\_chave(criterio)  
        \# Ex: \["email", "senha", "credenciais"\]  
          
        if any(palavra in cenarios\_bdd.lower() for palavra in palavras\_chave):  
            cobertos \+= 1  
      
    \# 3\. Calcula score  
    if len(criterios) \== 0:  
        return 5.0  \# fallback se não houver critérios explícitos  
      
    return (cobertos / len(criterios)) \* 10

📝 MÉTRICA 2: CLAREZA (0-10)  
O que mede: Legibilidade \+ ausência de ambiguidade \+ tamanho adequado dos steps.  
Exemplo Prático  
❌ CLAREZA BAIXA (score: 3/10)  
gherkin  
Cenário: Fazer algo no sistema  
  Dado que o contexto está configurado corretamente  
  Quando o usuário realiza a operação necessária  
  Então o resultado esperado deve ocorrer adequadamente  
Problemas:  
"Fazer algo" → vago demais  
"contexto configurado" → que contexto?  
"operação necessária" → qual operação?  
"resultado esperado" → qual resultado?  
Steps com 6-10 palavras genéricas  
✅ CLAREZA ALTA (score: 9/10)  
gherkin  
Cenário: Adicionar produto ao carrinho  
  Dado que estou na página do produto "iPhone 15"  
  Quando clico no botão "Adicionar ao carrinho"  
  Então devo ver "1 item no carrinho"  
  E o total deve ser "R$ 7.299,00"  
Por que é bom:  
Título específico  
Steps entre 7-12 palavras  
Elementos UI concretos ("botão Adicionar")  
Dados explícitos ("R$ 7.299,00")  
Ação → resultado claro  
Como Calcular  
python  
import textstat  
import re

def calcular\_clareza(cenarios\_bdd: str) \-\> float:  
    """  
    Combina múltiplos indicadores de clareza  
    """  
    scores \= \[\]  
      
    cenarios \= cenarios\_bdd.split("\\nCenário:")  
      
    for cenario in cenarios:  
        if not cenario.strip():  
            continue  
          
        \# 1\. Legibilidade Flesch-Kincaid (0-100, quanto maior melhor)  
        flesch \= textstat.flesch\_reading\_ease(cenario)  
        score\_flesch \= min(flesch / 10, 10\)  \# normaliza pra 0-10  
          
        \# 2\. Tamanho dos steps (ideal: 7-15 palavras)  
        steps \= re.findall(r'(Dado|Quando|Então|E|Mas) (.+)', cenario)  
        tamanhos \= \[len(step\[1\].split()) for step in steps\]  
          
        penalidade\_tamanho \= 0  
        for tam in tamanhos:  
            if tam \< 5:  \# step muito curto (vago)  
                penalidade\_tamanho \+= 1  
            elif tam \> 20:  \# step muito longo (complexo)  
                penalidade\_tamanho \+= 1  
          
        score\_tamanho \= max(0, 10 \- penalidade\_tamanho \* 2\)  
          
        \# 3\. Detecta termos vagos  
        termos\_vagos \= \['algo', 'coisa', 'corretamente', 'adequadamente',   
                        'necessário', 'esperado', 'apropriado', 'relevante'\]  
        count\_vagos \= sum(1 for termo in termos\_vagos if termo in cenario.lower())  
        score\_especificidade \= max(0, 10 \- count\_vagos \* 2\)  
          
        \# 4\. Score final do cenário (média ponderada)  
        score\_cenario \= (score\_flesch \* 0.3 \+   
                        score\_tamanho \* 0.4 \+   
                        score\_especificidade \* 0.3)  
          
        scores.append(score\_cenario)  
      
    return sum(scores) / len(scores) if scores else 0

🏗️ MÉTRICA 3: ESTRUTURA GWT (0-10)  
O que mede: Aderência ao padrão Given-When-Then \+ uso correto de cada seção.  
Exemplo Prático  
❌ ESTRUTURA RUIM (score: 2/10)  
gherkin  
Cenário: Comprar produto  
  Dado que clico no botão comprar        \# ❌ Given tem AÇÃO  
  Quando o produto está no carrinho      \# ❌ When não tem ação do usuário  
  Então estou na página de produtos      \# ❌ Then é contexto, não validação  
Problemas:  
Given deveria ter só contexto (não "clico")  
When deveria ter ação do usuário (não estado passivo)  
Then deveria validar resultado (não navegar)  
✅ ESTRUTURA BOA (score: 10/10)  
gherkin  
Cenário: Comprar produto  
  Dado que estou na página do produto "MacBook Pro"     \# ✅ Contexto  
  E o produto está em estoque                           \# ✅ Precondição  
  Quando clico no botão "Comprar agora"                 \# ✅ Ação do usuário  
  Então devo ver a confirmação "Adicionado ao carrinho" \# ✅ Validação  
  E o contador do carrinho deve exibir "1"              \# ✅ Resultado observável  
Como Calcular  
python  
import re

def calcular\_estrutura\_gwt(cenarios\_bdd: str) \-\> float:  
    """  
    Valida estrutura Given-When-Then  
    """  
    scores \= \[\]  
      
    cenarios \= cenarios\_bdd.split("\\nCenário:")  
      
    for cenario in cenarios:  
        if not cenario.strip():  
            continue  
          
        pontos \= 0  
          
        \# 1\. Tem Given/When/Then? (2 pontos)  
        tem\_given \= bool(re.search(r'\\bDado\\b', cenario))  
        tem\_when \= bool(re.search(r'\\bQuando\\b', cenario))  
        tem\_then \= bool(re.search(r'\\bEntão\\b', cenario))  
          
        if tem\_given and tem\_when and tem\_then:  
            pontos \+= 2  
          
        \# 2\. Given não tem verbos de ação (2 pontos)  
        givens \= re.findall(r'Dado (?:que )?(.+)', cenario)  
        verbos\_acao \= \['clico', 'preencho', 'envio', 'seleciono', 'digito'\]  
          
        given\_sem\_acao \= True  
        for given in givens:  
            if any(verbo in given.lower() for verbo in verbos\_acao):  
                given\_sem\_acao \= False  
                break  
          
        if given\_sem\_acao and givens:  
            pontos \+= 2  
          
        \# 3\. When tem exatamente 1 ação clara (3 pontos)  
        whens \= re.findall(r'Quando (.+)', cenario)  
          
        if len(whens) \== 1:  \# idealmente 1 When por cenário  
            when \= whens\[0\]  
            if any(verbo in when.lower() for verbo in verbos\_acao):  
                pontos \+= 3  
          
        \# 4\. Then valida resultado observável (3 pontos)  
        thens \= re.findall(r'Então (?:devo )?(.+)', cenario)  
          
        verbos\_validacao \= \['ver', 'exibir', 'mostrar', 'conter', 'ser redirecionado'\]  
        validacao\_clara \= False  
          
        for then in thens:  
            if any(verbo in then.lower() for verbo in verbos\_validacao):  
                validacao\_clara \= True  
                break  
          
        if validacao\_clara:  
            pontos \+= 3  
          
        scores.append(min(pontos, 10))  
      
    return sum(scores) / len(scores) if scores else 0

⚙️ MÉTRICA 4: EXECUTABILIDADE (0-10)  
O que mede: Steps podem ser traduzidos em código de automação? Têm dados concretos?  
Exemplo Prático  
❌ NÃO EXECUTÁVEL (score: 1/10)  
gherkin  
Cenário: Fazer login  
  Dado que o sistema está funcionando  
  Quando o usuário faz login corretamente  
  Então tudo deve funcionar como esperado  
Problemas:  
"sistema funcionando" → como testar isso?  
"faz login corretamente" → quais credenciais?  
"tudo funcionar" → o que validar?  
Impossível mapear pra código Playwright/Cypress  
✅ TOTALMENTE EXECUTÁVEL (score: 10/10)  
gherkin  
Cenário: Login com credenciais válidas  
  Dado que estou na página "https://app.com/login"  
  Quando preencho o campo "input\[name='email'\]" com "test@example.com"  
  E preencho o campo "input\[name='password'\]" com "Pass123\!"  
  E clico no botão "button\[type='submit'\]"  
  Então devo ser redirecionado para "https://app.com/dashboard"  
  E devo ver o elemento "h1" contendo "Bem-vindo"  
Por que é executável:  
URLs concretas  
Seletores CSS específicos  
Dados de teste explícitos  
Validações verificáveis  
Mapeamento pra Playwright  
python  
\# O step acima pode ser traduzido diretamente pra:

page.goto("https://app.com/login")  
page.fill("input\[name='email'\]", "test@example.com")  
page.fill("input\[name='password'\]", "Pass123\!")  
page.click("button\[type='submit'\]")  
expect(page).to\_have\_url("https://app.com/dashboard")  
expect(page.locator("h1")).to\_contain\_text("Bem-vindo")  
Como Calcular  
python  
import re

def calcular\_executabilidade(cenarios\_bdd: str) \-\> float:  
    """  
    Verifica se steps podem ser traduzidos em automação  
    """  
    scores \= \[\]  
      
    cenarios \= cenarios\_bdd.split("\\nCenário:")  
      
    for cenario in cenarios:  
        if not cenario.strip():  
            continue  
          
        pontos \= 0  
        steps \= re.findall(r'(Dado|Quando|Então|E|Mas) (.+)', cenario)  
          
        for keyword, step in steps:  
            step\_lower \= step.lower()  
              
            \# 1\. Tem dados concretos? (não "um valor", "algum texto")  
            termos\_vagos \= \['algum', 'qualquer', 'um valor', 'algo', 'etc'\]  
            if not any(termo in step\_lower for termo in termos\_vagos):  
                pontos \+= 1  
              
            \# 2\. Tem seletor específico? (CSS, XPath, ID)  
            seletores \= \['\#', '.', '\[', 'input', 'button', 'div', 'span', 'id=', 'class='\]  
            if any(sel in step for sel in seletores):  
                pontos \+= 2  
              
            \# 3\. Tem URL concreta?  
            if re.search(r'https?://\[\\w\\./\]+', step):  
                pontos \+= 1  
              
            \# 4\. Tem ação mapeável?  
            acoes\_mapeaveis \= \['preencho', 'clico', 'seleciono', 'marco', 'desmarco',   
                              'navego', 'espero', 'vejo', 'não vejo'\]  
            if any(acao in step\_lower for acao in acoes\_mapeaveis):  
                pontos \+= 1  
          
        \# Normaliza pra 0-10  
        max\_pontos \= len(steps) \* 5  \# cada step pode ter até 5 pontos  
        score\_cenario \= (pontos / max\_pontos) \* 10 if max\_pontos \> 0 else 0  
          
        scores.append(min(score\_cenario, 10))  
      
    return sum(scores) / len(scores) if scores else 0

📊 SCORE FINAL AGREGADO  
python  
def calcular\_score\_final(user\_story: str, cenarios\_bdd: str) \-\> dict:  
    """  
    Calcula todas as métricas e retorna score final  
    """  
    cobertura \= calcular\_cobertura(user\_story, cenarios\_bdd)  
    clareza \= calcular\_clareza(cenarios\_bdd)  
    estrutura \= calcular\_estrutura\_gwt(cenarios\_bdd)  
    executabilidade \= calcular\_executabilidade(cenarios\_bdd)  
      
    \# Pesos ajustáveis  
    score\_final \= (  
        cobertura \* 0.30 \+       \# 30% \- cobre tudo?  
        clareza \* 0.20 \+          \# 20% \- é legível?  
        estrutura \* 0.30 \+        \# 30% \- segue GWT?  
        executabilidade \* 0.20    \# 20% \- dá pra automatizar?  
    )  
      
    return {  
        "cobertura": round(cobertura, 2),  
        "clareza": round(clareza, 2),  
        "estrutura": round(estrutura, 2),  
        "executabilidade": round(executabilidade, 2),  
        "score\_final": round(score\_final, 2),  
        "aprovado": score\_final \>= 7.0  \# threshold  
    }

🎯 RESUMO VISUAL  
┌─────────────────────────────────────────────────────────┐  
│  SCORE FINAL \= 8.2/10 ✅ APROVADO                       │  
├─────────────────────────────────────────────────────────┤  
│  📊 Cobertura:       9.0/10  ████████████████████░░     │  
│     → Cobre 90% dos critérios de aceitação             │  
│                                                          │  
│  📝 Clareza:         7.5/10  ███████████████░░░░░       │  
│     → Steps legíveis, alguns termos vagos              │  
│                                                          │  
│  🏗️  Estrutura GWT:  8.0/10  ████████████████░░░░       │  
│     → Given/When/Then corretos, falta Scenario Outline │  
│                                                          │  
│  ⚙️  Executabilidade: 8.5/10  █████████████████░░░      │  
│     → Seletores específicos, faltam alguns dados       │  
└─────────────────────────────────────────────────────────┘

