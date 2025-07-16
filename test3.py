import requests
import os
import time

# Настройки
TAGS = "mita_(miside)"  # Твои теги
TOTAL_IMAGES = 1000      # Сколько всего картинок нужно
PER_PAGE = 200           # Максимум 200 за раз
SAVE_FOLDER = "danbooru_mita"
API_URL = "https://danbooru.donmai.us/posts.json"

# Создаем папку
os.makedirs(SAVE_FOLDER, exist_ok=True)

downloaded = 0
page = 1

print(f"Начинаю парсить {TOTAL_IMAGES} картинок по тегу '{TAGS}'")

while downloaded < TOTAL_IMAGES:
    remaining = TOTAL_IMAGES - downloaded
    limit = min(PER_PAGE, remaining)

    params = {
        "tags": TAGS,
        "limit": limit,
        "page": page
    }

    print(f"\n[Страница {page}] Загружаю {limit} изображений...")

    response = requests.get(API_URL, params=params)
    if response.status_code != 200:
        print(f"Ошибка запроса: {response.status_code}, {response.text}")
        break

    data = response.json()

    if not data:
        print("Больше изображений нет.")
        break

    for post in data:
        file_url = post.get("file_url")
        tags = post.get("tag_string")
        post_id = post.get("id")

        if not file_url:
            continue

        try:
            img_data = requests.get(file_url).content
            filename = os.path.join(SAVE_FOLDER, f"{post_id}.jpg")

            with open(filename, "wb") as f:
                f.write(img_data)

            # Сохраняем теги
            tag_file = os.path.join(SAVE_FOLDER, f"{post_id}_tags.txt")
            with open(tag_file, "w", encoding="utf-8") as f:
                f.write(tags)

            downloaded += 1
            print(f"[{downloaded}/{TOTAL_IMAGES}] Сохранено: {filename}")

            if downloaded >= TOTAL_IMAGES:
                break


        except Exception as e:
            print(f"Ошибка при загрузке: {e}")

    if downloaded >= TOTAL_IMAGES:
        break

    page += 1

print("\nГотово! Скачано:", downloaded)
