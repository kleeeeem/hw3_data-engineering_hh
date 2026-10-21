import boto3
import json
from itertools import combinations
from collections import Counter
from botocore.config import Config
import time
import psutil
import os

s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='myaccesskey123',
    aws_secret_access_key='mysecretkey456',
    config=Config(signature_version='s3v4')
)

BUCKET = 'hh-lake'
KEY = 'python_vacancies.jsonl'

def read_chunks(bucket, key, chunk_size=1024*1024):
    obj = s3.get_object(Bucket=bucket, Key=key)
    stream = obj['Body']
    buffer = ''
    
    while True:
        chunk = stream.read(chunk_size).decode('utf-8')
        if not chunk:
            break
        buffer += chunk
        lines = buffer.split('\n')
        buffer = lines.pop()
        
        for line in lines:
            if line.strip():
                yield json.loads(line)
                
    if buffer.strip():
        yield json.loads(buffer)

def main():
    start_time = time.time()
    
    skill_counter = Counter()
    pair_counter = Counter()
    triple_counter = Counter()

    for vacancy in read_chunks(BUCKET, KEY, chunk_size=1024*512):
        skills = list(set(s.strip().lower() for s in vacancy.get('key_skills', []) if s.strip()))
        skills.sort() 
        
        # одиночные навыки
        for skill in skills:
            skill_counter[skill] += 1
            
        # пары навыков
        for pair in combinations(skills, 2):
            pair_counter[pair] += 1
            
        # тройки навыков
        if len(skills) >= 3:
            for triple in combinations(skills, 3):
                triple_counter[triple] += 1

    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / 1024 / 1024
    exec_time = time.time() - start_time

    print(f"Уникальных навыков: {len(skill_counter)}")
    print(f"Уникальных пар: {len(pair_counter)}")
    print(f"Уникальных троек: {len(triple_counter)}")
    print(f"Время выполнения: {exec_time:.2f} сек.")
    print(f"Пиковая память: {mem_mb:.2f} МБ")

    def save_results(counter, filename, is_tuple=False):
        if is_tuple:
            result_list = [{"skills": list(k), "count": v} for k, v in counter.most_common()]
        else:
            result_list = [{"skill": k, "count": v} for k, v in counter.most_common()]
            
        json_data = json.dumps(result_list, ensure_ascii=False, indent=2)
        s3.put_object(Bucket=BUCKET, Key=f'results/{filename}', Body=json_data)
        print(f"Сохранено в s3: results/{filename}")

    save_results(skill_counter, 'skills.json', is_tuple=False)
    save_results(pair_counter, 'pairs.json', is_tuple=True)
    save_results(triple_counter, 'triples.json', is_tuple=True)

if __name__ == "__main__":
    main()