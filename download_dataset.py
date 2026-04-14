from datasets import load_dataset

# Carrega o dataset diretamente (baixa apenas os metadados, não o arquivo inteiro de uma vez)
dataset = load_dataset("giseldo/neodataset", split="train", streaming=True)

# Agora você pode iterar sobre os exemplos sem baixar tudo
issues = []
for i, item in enumerate(dataset):
    if i >= 150:  # Pega os primeiros 150
        break
    issues.append({
        "title": item.get("title", ""),
        "description": item.get("description", ""),
        "storypoints": item.get("storypoints", "")
    })

# Salva em CSV local
import csv
with open('neodataset_150.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['title', 'description', 'storypoints'])
    writer.writeheader()
    writer.writerows(issues)

print(f"✅ Dataset criado com {len(issues)} issues")