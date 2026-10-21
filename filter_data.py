import pandas as pd
import json
import ast

FILE_NAME = 'IT_vacancies.csv'
OUTPUT_FILE = 'python_vacancies.jsonl'

df = pd.read_csv(FILE_NAME)

python_df = df[df['name'].str.contains('python', case=False, na=False)].copy()
print(f"найдено {len(python_df)} вакансий python-разработчиков")

def parse_skills(skills_str):
    if pd.isna(skills_str):
        return []
    try:
        parsed = ast.literal_eval(skills_str)
        return list(parsed) 
    except (ValueError, SyntaxError):
        return [s.strip().strip("'\"") for s in str(skills_str).split(',') if s.strip()]
python_df['key_skills_parsed'] = python_df['key_skills'].apply(parse_skills)

output_data = []
for _, row in python_df.iterrows():
    s_from = None if pd.isna(row['salary_from']) else int(row['salary_from'])
    s_to = None if pd.isna(row['salary_to']) else int(row['salary_to'])

    vacancy = {
        "id": str(row['id']),
        "name": str(row['name']),
        "area": str(row['area_name']),
        "salary_from": s_from,
        "salary_to": s_to,
        "key_skills": row['key_skills_parsed']
    }
    output_data.append(vacancy)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for v in output_data:
        f.write(json.dumps(v, ensure_ascii=False) + "\n")
