import pandas as pd

FILE_NAME = 'IT_vacancies.csv' 

try:
    df = pd.read_csv(FILE_NAME, nrows=5)
    
    for col in df.columns:
        print(col)
        
    print(df.head(3))
    
except FileNotFoundError:
    print(f"ошибка")
except Exception as e:
    print(f"ошибка: {e}")