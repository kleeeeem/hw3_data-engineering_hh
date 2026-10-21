import duckdb
import time
import psutil
import os

start_time = time.time()

con = duckdb.connect()
con.execute("INSTALL httpfs;")
con.execute("LOAD httpfs;")
con.execute("""
    CREATE OR REPLACE SECRET rustfs_secret (
        TYPE S3,
        KEY_ID 'myaccesskey123',
        SECRET 'mysecretkey456',
        ENDPOINT 'localhost:9000',
        USE_SSL false,
        URL_STYLE 'path'
    );
""")
con.execute("""
    CREATE OR REPLACE VIEW clean_vacancies AS
    SELECT id,
           list_sort(list_distinct(
               list_filter(
                   list_transform(key_skills, x -> lower(trim(x))),
                   x -> x != ''
               )
           )) as skills
    FROM read_json_auto('s3://hh-lake/python_vacancies.jsonl');
""")

# одиночные
skills_query = """
    SELECT COUNT(DISTINCT skill) 
    FROM (SELECT unnest(skills) as skill FROM clean_vacancies);
"""
unique_skills = con.execute(skills_query).fetchone()[0]

# пары
pairs_query = """
    WITH flat AS (SELECT id, unnest(skills) as skill FROM clean_vacancies)
    SELECT COUNT(*) FROM (
        SELECT a.skill, b.skill
        FROM flat a
        JOIN flat b ON a.id = b.id AND a.skill < b.skill
        GROUP BY a.skill, b.skill
    );
"""
unique_pairs = con.execute(pairs_query).fetchone()[0]

# тройки
triples_query = """
    WITH flat AS (SELECT id, unnest(skills) as skill FROM clean_vacancies)
    SELECT COUNT(*) FROM (
        SELECT a.skill, b.skill, c.skill
        FROM flat a
        JOIN flat b ON a.id = b.id AND a.skill < b.skill
        JOIN flat c ON a.id = c.id AND b.skill < c.skill
        GROUP BY a.skill, b.skill, c.skill
    );
"""
unique_triples = con.execute(triples_query).fetchone()[0]

process = psutil.Process(os.getpid())
mem_mb = process.memory_info().rss / 1024 / 1024
exec_time = time.time() - start_time

print(f"Уникальных навыков (DuckDB): {unique_skills}")
print(f"Уникальных пар (DuckDB): {unique_pairs}")
print(f"Уникальных троек (DuckDB): {unique_triples}")
print(f"Время выполнения: {exec_time:.2f} сек.")
print(f"Пиковая память: {mem_mb:.2f} МБ")