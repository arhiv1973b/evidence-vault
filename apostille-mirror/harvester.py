import json
from collections import Counter
import re

with open('mirrors/evidence_index.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Собираем все слова из названий файлов
words = []
for item in data:
    # Очистка от лишних символов и цифр (кроме лет)
    clean_name = re.sub(r'[^\w\s]', ' ', item['name'])
    words.extend([w.lower() for w in clean_name.split() if len(w) > 3])

# Топ-50 наиболее частотных терминов
common = Counter(words).most_common(50)
print("\n[ TOP KEYWORDS FOR MANIFESTS ]")
for word, count in common:
    print(f"{word}: {count} объектов")
