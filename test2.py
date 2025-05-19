import pyarrow.parquet as pq
import pandas as pd
import json
import numpy as np  # Импортируем NumPy

# Чтение файла Parquet
try:
    table = pq.read_table('11.parquet')
except FileNotFoundError:
    print("Ошибка: Файл '11.parquet' не найден.")
    exit()
except Exception as e:
    print(f"Ошибка при чтении Parquet файла: {e}")
    exit()

# Преобразование в DataFrame Pandas
try:
    df = table.to_pandas()
except Exception as e:
    print(f"Ошибка при преобразовании в Pandas DataFrame: {e}")
    exit()

# Функция для преобразования ndarray в список
def convert_numpy_array(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


# Конвертация в JSON
try:
    # Преобразуем DataFrame, применяя функцию к каждому элементу
    df = df.applymap(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)


    # Option 1:  Convert DataFrame to a list of dictionaries
    data = df.to_dict(orient='records')

    # Запись в JSON файл
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Файл 'output.json' успешно создан.")

except Exception as e:
    print(f"Ошибка при конвертации в JSON и записи в файл: {e}")
    exit()