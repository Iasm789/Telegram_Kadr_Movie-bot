import json
import requests
from bs4 import BeautifulSoup
from Classifier import KNearestNeighbours
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler


# Загрузка данных
with open('./Data/movie_data.json', 'r+', encoding='utf-8') as f:
    data = json.load(f)
with open('./Data/movie_titles.json', 'r+', encoding='utf-8') as f:
    movie_titles = json.load(f)

hdr = {'User-Agent': 'Mozilla/5.0'}

# Этапы разговора
SELECTING_ACTION, SELECTING_MOVIE, SELECTING_GENRE, SELECTING_GENRE_MULTIPLE, SHOWING_RECOMMENDATIONS = range(5)


def get_main_keyboard():
    keyboard = [
        [KeyboardButton("Рекомендации по фильму"), KeyboardButton("Рекомендации по жанру")],
        [KeyboardButton("Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_genre_keyboard():
    genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
              'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News',
              'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Thriller', 'War', 'Western']
    keyboard = [[KeyboardButton(genre)] for genre in genres]
    keyboard.append([KeyboardButton("Готово"), KeyboardButton("Назад")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_genres():
    return ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
            'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News',
            'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Thriller', 'War', 'Western']


async def start(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("Посетите наш сайт", url="https://kadrmovie.streamlit.app/")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Привет! Я бот для рекомендаций фильмов. Выберите тип рекомендации:",
        reply_markup=get_main_keyboard()
    )
    await update.message.reply_text(
        "Вы также можете посетить наш сайт, нажав на кнопку ниже:",
        reply_markup=reply_markup
    )
    return SELECTING_ACTION


def fetch_url_data(url):
    try:
        response = requests.get(url, headers=hdr)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return None


def get_movie_info(imdb_link):
    url_data = fetch_url_data(imdb_link)
    if url_data:
        s_data = BeautifulSoup(url_data, 'html.parser')

        director_tag = s_data.find("a", {"data-testid": "title-pc-principal-credit"})
        movie_director = director_tag.text if director_tag else "Director information not available"

        cast_tags = s_data.select("a[data-testid='title-cast-item__actor']")
        movie_cast = ", ".join(tag.text for tag in cast_tags[:5]) if cast_tags else "Cast information not available"

        story_tag = s_data.find("span", {"data-testid": "plot-l"})
        movie_story = story_tag.text.strip() if story_tag else "Story information not available"

        rating_tag = s_data.find("span", {"class": "sc-7ab21ed2-1 jGRxWM"})
        movie_rating = f'IMDB Rating: {rating_tag.text}⭐' if rating_tag else 'Rating not available'

        return movie_director, movie_cast, movie_story, movie_rating
    return "Director information not available", "Cast information not available", "Story information not available", "Rating not available"


def KNN_Movie_Recommender(test_point, k):
    target = [0 for _ in movie_titles]
    model = KNearestNeighbours(data, target, test_point, k=k)
    model.fit()
    table = []
    for i in model.indices:
        table.append([movie_titles[i][0], movie_titles[i][2], data[i][-1]])
    return table


async def recommend_by_movie(update: Update, context: CallbackContext) -> int:
    movies = [title[0] for title in movie_titles]
    movie_list = "\n".join(
        f"{i + 1}. {movie}" for i, movie in enumerate(movies[:50]))  # Ограничение до 50 фильмов для удобства
    await update.message.reply_text(f"Выберите фильм из списка (введите номер):\n{movie_list}",
                                    reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True))
    return SHOWING_RECOMMENDATIONS


async def recommend_by_genre(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Выберите жанр из списка (можно выбрать несколько, и нажать Готово):", reply_markup=get_genre_keyboard())
    context.user_data['selected_genres'] = []
    return SELECTING_GENRE_MULTIPLE


async def show_recommendations(update: Update, context: CallbackContext) -> int:
    user_data = update.message.text
    movies = [title[0] for title in movie_titles]

    try:
        selected_index = int(user_data) - 1
        if selected_index < 0 or selected_index >= len(movies):
            await update.message.reply_text("Пожалуйста, выберите правильный номер фильма.",
                                            reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True))
            return SELECTING_MOVIE

        selected_movie = movies[selected_index]
        no_of_reco = 5  # Количество рекомендаций
        genres = data[selected_index]
        test_points = genres
        table = KNN_Movie_Recommender(test_points, no_of_reco + 1)
        table.pop(0)

        recommendations = "Ниже приведены некоторые фильмы из нашей рекомендации:\n"
        for movie, link, ratings in table:
            director, cast, story, total_rat = get_movie_info(link)
            recommendations += f"\n[{movie}]({link})\n"
            recommendations += f"**Director:** {director}\n"
            recommendations += f"**Cast:** {cast}\n"
            recommendations += f"**Story:** {story}\n"
            recommendations += f"**Rating:** {total_rat}\n"
            recommendations += f"IMDB Rating: {ratings}⭐\n"

        await update.message.reply_text(recommendations, parse_mode="Markdown", reply_markup=get_main_keyboard())
        return SELECTING_ACTION

    except ValueError:
        await update.message.reply_text("Пожалуйста, введите правильный номер.",
                                        reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True))
        return SELECTING_MOVIE


async def handle_genre_selection(update: Update, context: CallbackContext) -> int:
    genre = update.message.text
    if genre == "Готово":
        selected_genres = context.user_data.get('selected_genres', [])
        if not selected_genres:
            await update.message.reply_text("Пожалуйста, выберите хотя бы один жанр.",
                                            reply_markup=get_genre_keyboard())
            return SELECTING_GENRE_MULTIPLE

        imdb_score = 8
        no_of_reco = 5
        test_point = [1 if genre in selected_genres else 0 for genre in get_genres()]
        test_point.append(imdb_score)
        table = KNN_Movie_Recommender(test_point, no_of_reco)

        recommendations = "Ниже приведены некоторые фильмы из нашей рекомендации:\n"
        for movie, link, ratings in table:
            director, cast, story, total_rat = get_movie_info(link)
            recommendations += f"\n[{movie}]({link})\n"
            recommendations += f"**Director:** {director}\n"
            recommendations += f"**Cast:** {cast}\n"
            recommendations += f"**Story:** {story}\n"
            recommendations += f"**Rating:** {total_rat}\n"
            recommendations += f"IMDB Rating: {ratings}⭐\n"

        await update.message.reply_text(recommendations, parse_mode="Markdown", reply_markup=get_main_keyboard())
        return SELECTING_ACTION
    elif genre == "Назад":
        await update.message.reply_text("Выберите тип рекомендации:", reply_markup=get_main_keyboard())
        return SELECTING_ACTION
    else:
        selected_genres = context.user_data.get('selected_genres', [])
        if genre not in selected_genres:
            selected_genres.append(genre)
            context.user_data['selected_genres'] = selected_genres
        await update.message.reply_text(f"Вы выбрали жанры: {', '.join(selected_genres)}",
                                        reply_markup=get_genre_keyboard())
        return SELECTING_GENRE_MULTIPLE


async def handle_message(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    if text == "Рекомендации по фильму":
        return await recommend_by_movie(update, context)
    elif text == "Рекомендации по жанру":
        return await recommend_by_genre(update, context)
    elif text == "Отмена":
        await update.message.reply_text("Отменено. Введите /start для начала заново.", reply_markup=get_main_keyboard())
        return SELECTING_ACTION
    else:
        await update.message.reply_text("Я не понимаю эту команду. Пожалуйста, выберите один из вариантов ниже.",
                                        reply_markup=get_main_keyboard())
        return SELECTING_ACTION


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Действие отменено. Введите /start для начала заново.',
                                    reply_markup=get_main_keyboard())
    return SELECTING_ACTION


def main():
    application = Application.builder().token("Your_Telegram_token").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_ACTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
            ],
            SELECTING_GENRE_MULTIPLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_genre_selection)],
            SHOWING_RECOMMENDATIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, show_recommendations)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
