import pandas as pd
from collections import Counter
from itertools import combinations

df = pd.read_csv('IT_vacancies.csv')
df = df[df['name'].str.contains('python', case=False, na=False)].copy()

def parse_skills(skills_str):
    if pd.isna(skills_str): return []
    s = str(skills_str).lower().replace('[', '').replace(']', '').replace('{', '').replace('}', '').replace("'", "").replace('"', '')
    skills = [item.strip() for item in s.split(',')]
    return list(set([item for item in skills if item and len(item) < 25]))

df['skills'] = df['key_skills'].apply(parse_skills)

df['salary'] = df.apply(lambda r: (r['salary_from'] + r['salary_to'])/2 if pd.notna(r['salary_from']) and pd.notna(r['salary_to']) 
                        else r['salary_from'] if pd.notna(r['salary_from']) 
                        else r['salary_to'], axis=1)

df_salary = df[(df['salary'] >= 20000) & (df['salary'] <= 1000000)].copy()

base_median = df_salary['salary'].median()
print(f"\nбазовая медианная зарплата: {base_median:.0f} рублей")

def analyze_pairs(df_salary, base_median, min_vacancies=3):
    counter = Counter()
    for skills in df_salary['skills']:
        for pair in combinations(sorted(skills), 2): 
            counter[pair] += 1
            
    results = []
    for combo, count in counter.items():
        if count >= min_vacancies:
            mask = df_salary['skills'].apply(lambda x: set(combo).issubset(set(x)))
            median_sal = df_salary.loc[mask, 'salary'].median()
            diff = median_sal - base_median
            results.append((combo, median_sal, diff, count))
            
    results.sort(key=lambda x: x[2], reverse=True)
    return results

top_pairs = analyze_pairs(df_salary, base_median)

for p in top_pairs[:5]:
    print(f"{p[0]}: медиана {p[1]:.0f} (прибавка +{p[2]:.0f}), вакансий: {p[3]}")

for p in top_pairs[-5:]:
    print(f"{p[0]}: медиана {p[1]:.0f} (падение {p[2]:.0f}), вакансий: {p[3]}")

top_areas = df['area_name'].value_counts().head(3).index.tolist()

for area in top_areas:
    area_df = df_salary[df_salary['area_name'] == area]
    if len(area_df) == 0: continue
    
    area_median = area_df['salary'].median()
    all_skills = [s for skills in area_df['skills'] for s in skills]
    top_skill = Counter(all_skills).most_common(1)[0] if all_skills else ("нет данных", 0)
    
    print(f"\nРегион: {area}")
    print(f"  кол-во вакансий с зарплатой: {len(area_df)}")
    print(f"  медианная зарплата: {area_median:.0f} руб.")
    print(f"  самый частый навык: {top_skill[0]} ({top_skill[1]} раз)")