# bdd_generator_final.py
import subprocess
import csv
import os
import sys
import re
import random
from datetime import datetime
from pathlib import Path
import argparse

# Forçar UTF-8 no Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

class BDDGenerator:
    def __init__(self, dataset_file="neodataset.csv", model="deepseek-coder:6.7b", output_dir="bdd"):
        self.dataset_file = dataset_file
        self.model = model
        self.output_dir = Path(output_dir)
        self.issues = []
        
        # Criar pasta de saída
        self.output_dir.mkdir(exist_ok=True)
        print(f"📁 Pasta de saída: {self.output_dir.absolute()}")
        
        self.load_dataset()
        
    def load_dataset(self):
        """Carrega dataset CSV corretamente"""
        if not os.path.exists(self.dataset_file):
            print(f"❌ Arquivo {self.dataset_file} não encontrado!")
            return False
        
        try:
            # Forçar UTF-8 ao ler o CSV
            with open(self.dataset_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                header = next(reader)
                
                for row in reader:
                    if len(row) >= 3:
                        title = row[0].strip() if row[0] else ""
                        description = row[1].strip() if len(row) > 1 and row[1] else ""
                        storypoints = row[2].strip() if len(row) > 2 and row[2] else "N/A"
                        
                        if title:
                            self.issues.append({
                                'title': title,
                                'description': description,
                                'storypoints': storypoints
                            })
            
            print(f"✅ Dataset carregado: {len(self.issues)} issues")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar: {e}")
            return False
    
    def get_random_issues(self, count=10):
        """Retorna issues aleatórias"""
        if not self.issues:
            return []
        
        count = min(count, len(self.issues))
        return random.sample(self.issues, count)
    
    def search_similar_issues(self, user_story, top_k=3):
        """Busca issues similares"""
        if not self.issues:
            return []
        
        keywords = set(re.findall(r'\w+', user_story.lower()))
        keywords = {k for k in keywords if len(k) > 3}
        
        similar = []
        for issue in self.issues[:500]:
            title = issue['title'].lower()
            desc = issue['description'][:500].lower()
            
            score = sum(1 for kw in keywords if kw in title or kw in desc)
            
            if score > 0:
                similar.append({
                    'title': issue['title'],
                    'description': issue['description'][:400],
                    'storypoints': issue['storypoints'],
                    'score': score
                })
        
        similar.sort(key=lambda x: x['score'], reverse=True)
        return similar[:top_k]
    
    def generate_bdd(self, user_story, use_context=True):
        """Gera cenários BDD com suporte UTF-8"""
        
        context = ""
        if use_context:
            similar = self.search_similar_issues(user_story, top_k=2)
            if similar:
                context = "\n\n📚 EXEMPLOS REAIS DE ISSUES SIMILARES:\n"
                for i, ex in enumerate(similar, 1):
                    context += f"\nExemplo {i}:\n"
                    context += f"Título: {ex['title']}\n"
                    context += f"Descrição: {ex['description']}...\n"
        
        prompt = f"""Você é um especialista sênior em BDD.

Crie uma suíte COMPLETA de cenários Gherkin para:

HISTÓRIA: {user_story}
{context}

REGRAS:
- Analise a complexidade (simples: 3-4, média: 4-6, complexa: 6-8 cenários)
- Inclua: caminho feliz, variações, erros, validações
- Use formato:
  Cenário: [título]
    Dado que [contexto]
    Quando [ação]
    Então [resultado]

Retorne APENAS os cenários.
"""
        
        print(f"🔄 Gerando cenários BDD...")
        
        try:
            # Forçar UTF-8 na comunicação com subprocesso
            result = subprocess.run(
                ["ollama", "run", self.model],
                input=prompt,
                capture_output=True,
                text=True,
                encoding='utf-8',  # Forçar UTF-8
                timeout=120
            )
            
            if result.returncode == 0:
                scenario_text = result.stdout.strip()
                # Contar cenários
                scenario_count = len(re.findall(r'^Cenário:', scenario_text, re.MULTILINE))
                
                # Verificar qualidade
                has_given = 'dado que' in scenario_text.lower()
                has_when = 'quando' in scenario_text.lower()
                has_then = 'então' in scenario_text.lower()
                
                return {
                    "success": True,
                    "scenario": scenario_text,
                    "scenario_count": scenario_count if scenario_count > 0 else 1,
                    "quality_check": has_given and has_when and has_then,
                    "model": self.model,
                    "timestamp": datetime.now().isoformat(),
                    "user_story": user_story
                }
            else:
                return {"success": False, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout (120s)"}
        except UnicodeDecodeError as e:
            # Tentar com outra codificação se falhar
            print(f"⚠️ Erro de codificação, tentando recuperar...")
            try:
                result = subprocess.run(
                    ["ollama", "run", self.model],
                    input=prompt.encode('utf-8'),
                    capture_output=True,
                    timeout=120
                )
                scenario_text = result.stdout.decode('utf-8', errors='ignore').strip()
                scenario_count = len(re.findall(r'^Cenário:', scenario_text, re.MULTILINE))
                
                return {
                    "success": True,
                    "scenario": scenario_text,
                    "scenario_count": scenario_count if scenario_count > 0 else 1,
                    "quality_check": True,
                    "model": self.model,
                    "timestamp": datetime.now().isoformat(),
                    "user_story": user_story
                }
            except Exception as e2:
                return {"success": False, "error": f"Erro de codificação: {e2}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_from_issue(self, issue):
        """Gera BDD a partir de uma issue"""
        title = issue['title']
        desc = issue['description'][:500]
        
        # Criar user story natural
        if '(bug)' in title.lower():
            clean_title = title.replace('(bug):', '').strip()
            story = f"Como usuário, quero que o seguinte problema seja corrigido: {clean_title}"
        elif '(feat)' in title.lower():
            clean_title = title.replace('(feat):', '').strip()
            story = f"Como usuário, quero {clean_title}"
        else:
            story = title
        
        result = self.generate_bdd(story, use_context=True)
        result['issue_title'] = title
        result['storypoints'] = issue['storypoints']
        
        return result

def save_scenario(scenario, output_dir, filename=None):
    """Salva cenário em arquivo .feature com UTF-8"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if 'issue_title' in scenario:
            base_name = scenario['issue_title'][:50].lower()
            base_name = re.sub(r'[^\w\s-]', '', base_name)
            base_name = re.sub(r'[-\s]+', '_', base_name)
            filename = f"{base_name}_{timestamp}.feature"
        else:
            filename = f"bdd_{timestamp}.feature"
    
    filepath = output_dir / filename
    
    # Forçar UTF-8 ao salvar
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# ============================================\n")
        f.write(f"# BDD Scenario Suite\n")
        f.write(f"# Gerado em: {datetime.now()}\n")
        f.write(f"# Modelo: {scenario.get('model', 'N/A')}\n")
        f.write(f"# Total de Cenários: {scenario.get('scenario_count', 'N/A')}\n")
        if 'user_story' in scenario:
            f.write(f"#\n# User Story:\n# {scenario['user_story']}\n")
        if 'issue_title' in scenario:
            f.write(f"#\n# Issue: {scenario['issue_title']}\n")
            f.write(f"# Story Points: {scenario.get('storypoints', 'N/A')}\n")
        f.write(f"# ============================================\n\n")
        f.write(scenario.get('scenario', ''))
    
    print(f"💾 Salvo: {filepath}")
    print(f"📊 Total de cenários: {scenario.get('scenario_count', 'N/A')}")
    return filepath

def main():
    parser = argparse.ArgumentParser(description='BDD Generator')
    parser.add_argument('--story', type=str, help='User story')
    parser.add_argument('--dataset', type=str, default='neodataset.csv', help='Arquivo CSV')
    parser.add_argument('--model', type=str, default='deepseek-coder:6.7b', help='Modelo Ollama')
    parser.add_argument('--random', action='store_true', help='Gerar histórias aleatórias')
    parser.add_argument('--count', type=int, default=5, help='Número de histórias')
    parser.add_argument('--list', action='store_true', help='Listar issues')
    parser.add_argument('--output', type=str, default='bdd', help='Pasta de saída')
    parser.add_argument('--seed', type=int, default=None, help='Seed para randomização')
    
    args = parser.parse_args()
    
    if args.seed is not None:
        random.seed(args.seed)
        print(f"🎲 Seed: {args.seed}")
    
    print("🤖 BDD Generator")
    print("=" * 60)
    
    generator = BDDGenerator(
        dataset_file=args.dataset, 
        model=args.model,
        output_dir=args.output
    )
    
    if not generator.issues:
        print("❌ Nenhuma issue carregada!")
        return
    
    if args.list:
        print(f"\n📋 Issues ({len(generator.issues)}):\n")
        for i, issue in enumerate(generator.issues[:20], 1):
            print(f"{i:3}. {issue['title'][:80]}")
            print(f"     Story Points: {issue['storypoints']}")
        return
    
    if args.random:
        print(f"\n🎲 Selecionando {args.count} histórias aleatórias...")
        random_issues = generator.get_random_issues(args.count)
        
        print(f"📊 Gerando BDD para {len(random_issues)} histórias\n")
        
        stats = {'total_scenarios': 0, 'success_count': 0}
        
        for i, issue in enumerate(random_issues, 1):
            print(f"\n{'='*60}")
            print(f"[{i}/{len(random_issues)}] {issue['title'][:70]}...")
            print(f"   Story Points: {issue['storypoints']}")
            print(f"{'='*60}")
            
            result = generator.generate_from_issue(issue)
            
            if result['success']:
                stats['success_count'] += 1
                stats['total_scenarios'] += result.get('scenario_count', 0)
                
                print(f"\n✅ GERADO! ({result.get('scenario_count', 0)} cenários)")
                
                # Preview
                scenarios = result['scenario'].split('Cenário:')
                print(f"\n📝 Preview:")
                for j, sc in enumerate(scenarios[1:4], 1):
                    if sc.strip():
                        first_line = sc.strip().split('\n')[0][:70]
                        print(f"   {j}. {first_line}...")
                
                if len(scenarios) > 4:
                    print(f"   ... e mais {len(scenarios)-4} cenários")
                
                # Salvar
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"random_{i:03d}_{timestamp}.feature"
                save_scenario(result, generator.output_dir, filename)
            else:
                print(f"\n❌ ERRO: {result.get('error', 'Desconhecido')}")
        
        print(f"\n{'='*60}")
        print(f"📊 RELATÓRIO")
        print(f"{'='*60}")
        print(f"✅ Sucesso: {stats['success_count']}/{len(random_issues)}")
        print(f"📝 Total cenários: {stats['total_scenarios']}")
        if stats['success_count'] > 0:
            print(f"📈 Média: {stats['total_scenarios']/stats['success_count']:.1f}")
        return
    
    if not args.story:
        print("\n💡 Modo Interativo")
        args.story = input("📖 Digite a user story: ").strip()
    
    if not args.story:
        print("❌ Nenhuma história fornecida")
        return
    
    print(f"\n📖 User Story: {args.story}")
    
    result = generator.generate_bdd(args.story, use_context=True)
    
    if result['success']:
        print("\n📝 CENÁRIOS GERADOS:")
        print("-" * 60)
        print(result['scenario'])
        print("-" * 60)
        print(f"\n📊 Total: {result.get('scenario_count', 0)} cenários")
        
        save_option = input("\n💾 Salvar? (s/N): ").strip().lower()
        if save_option == 's':
            save_scenario(result, generator.output_dir)
    else:
        print(f"❌ Erro: {result.get('error', 'Desconhecido')}")

if __name__ == "__main__":
    main()