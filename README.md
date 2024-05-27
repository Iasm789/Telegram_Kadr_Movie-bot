# Telegram_Kadr_Movie-bot
 The telegram bot “Kadr” will help you decide on the choice of a movie based on your preferences and tastes. Answer the questions, save your time and start watching the movie right now!
[Ссылка на бота](https://t.me/kadr_movie_bot) /n
[Ссылка на сайт](https://kadrmovie.streamlit.app/), [на Github](https://github.com/Iasm789/Kadr_Movie_Recommender)



# Бот для рекомендаций фильмов

Этот проект представляет собой Telegram-бота, который предоставляет рекомендации по фильмам на основе предпочтений пользователя. Пользователи могут получать рекомендации, выбирая конкретный фильм или один или несколько жанров.

## Особенности

- **Рекомендации по фильму**: Получите рекомендации по фильмам на основе выбранного фильма.
- **Рекомендации по жанру**: Получите рекомендации по фильмам на основе выбранных жанров.
- **Интерактивный интерфейс**: Использует inline-клавиатуру и клавиатуру ответов Telegram для удобного взаимодействия с пользователем.

## Требования

- Python 3.7+
- Токен API Telegram-бота

## Установка

1. Клонируйте репозиторий:

    ```sh
    git clone 
    cd movie-recommendation-bot
    ```

2. Создайте виртуальное окружение и активируйте его:

    ```sh
    python -m venv venv
    source venv/bin/activate  # В Windows используйте `venv\Scripts\activate`
    ```

3. Установите необходимые зависимости:

    ```sh
    pip install -r requirements.txt
    ```

4. Установите ваш токен API Telegram-бота:

    Замените `YOUR_TELEGRAM_BOT_TOKEN` в функции `main` на ваш актуальный токен Telegram-бота.

5. Запустите бота:

    ```sh
    python bot.py
    ```

## Использование

1. Запустите бота, отправив команду `/start` в чате вашего Telegram-бота.
2. Выберите между "Рекомендации по фильму" или "Рекомендации по жанру".
3. Следуйте подсказкам для получения рекомендаций по фильмам.

## Структура проекта

- `bot.py`: Основной скрипт, содержащий логику бота и обработчики.
- `Classifier.py`: Содержит реализацию классификатора K-Nearest Neighbours.
- `Data/`: Каталог, содержащий данные о фильмах и названия фильмов в формате JSON.
- `requirements.txt`: Список зависимостей Python.

## Файлы данных

- `Data/movie_data.json`: Содержит характеристики фильмов.
- `Data/movie_titles.json`: Содержит названия и ссылки на IMDb фильмов.



