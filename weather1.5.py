import telebot
from telebot import types
import requests
import time
import requests

# Встановлення API-ключа OpenWeatherMap
API_KEY = ''

# Ініціалізація телеграм-бота
bot = telebot.TeleBot('')

# Словник для збереження останньої отриманої погоди для кожного користувача
user_weather = {}

# Функція для отримання погоди
def get_weather(city):
    weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
    response = requests.get(weather_url)
    data = response.json()
    temperature = data['main']['temp']

    description = data['weather'][0]['description']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    pressure = data['main']['pressure']
    rain_probability = data.get('rain', {}).get('1h', 0)  # Ймовірність дощу за годину, якщо доступно
    wind_direction = data['wind'].get('deg', 'Н/Д')  # Напрям вітру


    weather_info = f"🌤Погода в місті {city}:\n🌡️Температура: {temperature}°C\n🌤Опис: {description}\n💧Вологість: {humidity}%\n💨Швидкість вітру: {wind_speed} м/с\n🌬Вітер: {wind_direction}°\n☔️Ймовірність дощу: {rain_probability}%\n🌫Тиск: {pressure} гПа"


    return weather_info

# Функція для отримання погоди на 3 дні
def get_weather_3_days(city):
    weather_3_days_url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric'
    response = requests.get(weather_3_days_url)
    data = response.json()

    # Перевірка, чи є дані про погоду
    forecasts = data.get('list', [])

    if not forecasts:
        raise Exception("Немає даних про погоду на наступні 3 дні.")

    # Витягування інформації для кожного дня
    today_forecast = forecasts[0]
    tomorrow_forecast = forecasts[8]  # Передбачаємо 8 інтервалів для наступного дня
    day_after_tomorrow_forecast = forecasts[16]  # Передбачаємо 8 інтервалів для післязавтра

    # Витягування відповідної інформації для кожного дня
    today_info = format_weather_info(today_forecast)
    tomorrow_info = format_weather_info(tomorrow_forecast)
    day_after_tomorrow_info = format_weather_info(day_after_tomorrow_forecast)

    # Об'єднання інформації для всіх трьох днів
    weather_info_3_days = f"Прогноз погоди на сьогодні:\n{today_info}\n\nПрогноз погоди на завтра:\n{tomorrow_info}\n\nПрогноз погоди на післязавтра:\n{day_after_tomorrow_info}"

    return weather_info_3_days

def get_weather_5_days(city):
    weather_5_days_url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric'
    response = requests.get(weather_5_days_url)
    data = response.json()

    forecasts = data.get('list', [])

    if not forecasts:
        raise Exception("Немає даних про погоду на наступні 5 днів.")

    # Витягування інформації для кожного дня
    day1_forecast = forecasts[0]
    day2_forecast = forecasts[8]  # 8 інтервалів для наступного дня
    day3_forecast = forecasts[16]  # 8 інтервалів для післязавтра
    day4_forecast = forecasts[24]  # 8 інтервалів для через 3 дні
    day5_forecast = forecasts[32]  # 8 інтервалів для через 4 дні

    # Витягування відповідної інформації для кожного дня
    day1_info = format_weather_info(day1_forecast)
    day2_info = format_weather_info(day2_forecast)
    day3_info = format_weather_info(day3_forecast)
    day4_info = format_weather_info(day4_forecast)
    day5_info = format_weather_info(day5_forecast)

    # Об'єднання інформації для всіх п'яти днів
    weather_info_5_days = f"Прогноз погоди на сьогодні:\n{day1_info}\n\nПрогноз погоди на завтра:\n{day2_info}\n\nПрогноз погоди на післязавтра:\n{day3_info}\n\nПрогноз погоди через 3 дні:\n{day4_info}\n\nПрогноз погоди через 4 дні:\n{day5_info}"

    return weather_info_5_days

def format_weather_info(forecast):
    # Витягування відповідної інформації з прогнозу та форматування
    temperature = forecast.get('main', {}).get('temp', 'Н/Д')
    description = forecast.get('weather', [{}])[0].get('description', 'Н/Д')
    humidity = forecast.get('main', {}).get('humidity', 'Н/Д')
    wind_speed = forecast.get('wind', {}).get('speed', 'Н/Д')
    pressure = forecast.get('main', {}).get('pressure', 'Н/Д')
    rain_probability = forecast.get('rain', {}).get('1h', 0)  # Ймовірність дощу за годину, якщо доступно
    wind_direction = forecast.get('wind', {}).get('deg', 'Н/Д')  # Напрям вітру

    return f"🌤 Температура: {temperature}°C, Опис: {description}\n🌧 Вологість: {humidity}%, Швидкість вітру: {wind_speed} м/с\n🌤 Тиск: {pressure} гПа, Ймовірність дощу: {rain_probability}%, Напрям вітру: {wind_direction}°"



# Обробник команди /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id

    # Зображення за посиланням в Інтернеті
    image_url = 'https://m.lifecell.ua/uploads/cache/cf/b4/cfb49f1f7d5717b262aeef69f5b6bbbd.jpg'

    # Завантажте зображення за посиланням
    image = requests.get(image_url)

    # Відправте зображення
    bot.send_photo(chat_id, image.content, caption="Привіт! Я бот, який надає інформацію про погоду.🌤 Введи назву міста, щоб дізнатися погоду.")

    # Збереження міста в словнику user_weather
    user_weather[chat_id] = {'city': None, 'timestamp': 0}


# Обробник повідомлень з текстом
@bot.message_handler(func=lambda message: True)
def send_weather(message):
    chat_id = message.chat.id
    city = message.text

    if chat_id not in user_weather or time.time() - user_weather[chat_id]['timestamp'] >= 3 * 60 * 60:
        try:
            weather_info = get_weather(city)
            user_weather[chat_id] = {'weather': weather_info, 'city': city, 'timestamp': time.time()}
        except Exception as e:
            error_message = "Виникла помилка при отриманні погоди. Будь ласка, перевірте назву міста та спробуйте ще раз."
            bot.send_message(chat_id, error_message)
            return
    else:
        weather_info = user_weather[chat_id]['weather']

    markup = types.InlineKeyboardMarkup()
    button_change_city = types.InlineKeyboardButton('Змінити місто', callback_data='change_city')
    button_weather_3_days = types.InlineKeyboardButton('Погода на 3 дні', callback_data='weather_3_days')
    button_weather_5_days = types.InlineKeyboardButton('Погода на 5 днів', callback_data='weather_5_days')
    button_hourly_weather = types.InlineKeyboardButton('Погода кожні 3 години', callback_data='hourly_weather')
    markup.add(button_change_city, button_weather_3_days, button_weather_5_days, button_hourly_weather)

    bot.send_message(chat_id, weather_info, reply_markup=markup)


# ...

# Функція для отримання погоди кожні 3 години на сьогодні
def get_hourly_weather_today(city):
    hourly_weather_url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric'
    response = requests.get(hourly_weather_url)
    data = response.json()

    forecasts = data.get('list', [])

    if not forecasts:
        raise Exception("Немає даних про погоду наступних 3 годин.")

    # Витягування інформації для кожної 3-ї години на сьогодні
    today = time.strftime("%Y-%m-%d")
    hourly_info = ""
    for forecast in forecasts:
        forecast_time = forecast.get('dt_txt', 'Н/Д')
        if today in forecast_time and forecast_time.endswith(("00:00:00", "03:00:00", "06:00:00", "09:00:00", "12:00:00", "15:00:00", "18:00:00", "21:00:00")):
            hourly_info += format_hourly_weather_info(forecast) + "\n"

    return hourly_info

# ...


def format_hourly_weather_info(forecast):
    # Витягування відповідної інформації з прогнозу та форматування
    time = forecast.get('dt_txt', 'Н/Д')
    temperature = forecast.get('main', {}).get('temp', 'Н/Д')
    description = forecast.get('weather', [{}])[0].get('description', 'Н/Д')
    humidity = forecast.get('main', {}).get('humidity', 'Н/Д')
    wind_speed = forecast.get('wind', {}).get('speed', 'Н/Д')

    return f"⏰ Час: {time}, Температура: {temperature}°C, Опис: {description}, Вологість: {humidity}%, Швидкість вітру: {wind_speed} м/с"



# Обробник натискання кнопки "Погода кожні 3 години"
@bot.callback_query_handler(func=lambda call: call.data == 'hourly_weather')
def handle_hourly_weather(call):
    chat_id = call.message.chat.id
    city = user_weather.get(chat_id, {}).get('city')

    try:
        hourly_weather_info = get_hourly_weather_today(city)

        markup = types.InlineKeyboardMarkup()
        button_change_city = types.InlineKeyboardButton('Змінити місто', callback_data='change_city')
        button_weather_3_days = types.InlineKeyboardButton('Погода на 3 дні', callback_data='weather_3_days')
        button_weather_5_days = types.InlineKeyboardButton('Погода на 5 днів', callback_data='weather_5_days')
        markup.add(button_change_city, button_weather_3_days, button_weather_5_days)

        bot.send_message(chat_id, hourly_weather_info, reply_markup=markup)
    except Exception as e:
        error_message = "Виникла помилка при отриманні погоди кожні 3 години. Будь ласка, спробуйте ще раз."
        bot.send_message(chat_id, error_message)




# Функція для отримання погоди на 3 дні
def get_weather_3_days(city):
    weather_3_days_url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric'
    response = requests.get(weather_3_days_url)
    data = response.json()

    # Перевірка, чи є дані про погоду
    forecasts = data.get('list', [])

    if not forecasts:
        raise Exception("Немає даних про погоду на наступні 3 дні.")

    # Витягування інформації для кожного дня
    today_forecast = forecasts[0]
    tomorrow_forecast = forecasts[8]  # Передбачаємо 8 інтервалів для наступного дня
    day_after_tomorrow_forecast = forecasts[16]  # Передбачаємо 8 інтервалів для післязавтра

    # Витягування відповідної інформації для кожного дня
    today_info = format_weather_info(today_forecast)
    tomorrow_info = format_weather_info(tomorrow_forecast)
    day_after_tomorrow_info = format_weather_info(day_after_tomorrow_forecast)

    # Об'єднання інформації для всіх трьох днів
    weather_info_3_days = f"Прогноз погоди на сьогодні:\n{today_info}\n\nПрогноз погоди на завтра:\n{tomorrow_info}\n\nПрогноз погоди на післязавтра:\n{day_after_tomorrow_info}"

    return weather_info_3_days

# Обробник натискання кнопки "Погода на 3 дні"
@bot.callback_query_handler(func=lambda call: call.data == 'weather_3_days')
def handle_weather_3_days(call):
    chat_id = call.message.chat.id
    city = user_weather.get(chat_id, {}).get('city')

    try:
        weather_info_3_days = get_weather_3_days(city)

        markup = types.InlineKeyboardMarkup()
        button_change_city = types.InlineKeyboardButton('Змінити місто', callback_data='change_city')
        button_weather_5_days = types.InlineKeyboardButton('Погода на 5 днів', callback_data='weather_5_days')
        button_hourly_weather = types.InlineKeyboardButton('Погода кожні 3 години', callback_data='hourly_weather')
        markup.add(button_change_city, button_weather_5_days, button_hourly_weather)

        bot.send_message(chat_id, weather_info_3_days, reply_markup=markup)
    except Exception as e:
        error_message = "Виникла помилка при отриманні погоди на 3 дні. Будь ласка, спробуйте ще раз."
        bot.send_message(chat_id, error_message)

# Обробник натискання кнопки "Погода на 5 днів"
@bot.callback_query_handler(func=lambda call: call.data == 'weather_5_days')
def handle_weather_5_days(call):
    chat_id = call.message.chat.id
    city = user_weather.get(chat_id, {}).get('city')

    try:
        weather_info_5_days = get_weather_5_days(city)

        markup = types.InlineKeyboardMarkup()
        button_change_city = types.InlineKeyboardButton('Змінити місто', callback_data='change_city')
        button_weather_3_days = types.InlineKeyboardButton('Погода на 3 дні', callback_data='weather_3_days')
        button_hourly_weather = types.InlineKeyboardButton('Погода кожні 3 години', callback_data='hourly_weather')
        markup.add(button_change_city, button_weather_3_days, button_hourly_weather)

        bot.send_message(chat_id, weather_info_5_days, reply_markup=markup)
    except Exception as e:
        error_message = "Виникла помилка при отриманні погоди на 5 днів. Будь ласка, спробуйте ще раз."
        bot.send_message(chat_id, error_message)

# Обробник натискання кнопки
@bot.callback_query_handler(func=lambda call: call.data == 'change_city')
def handle_button_click(call):
    chat_id = call.message.chat.id
    bot.send_message(chat_id, 'Введіть назву нового міста:')

    # Записуємо стан розмови для відстеження бажання користувача змінити місто
    bot.register_next_step_handler(call.message, change_city)

    # Додаємо кнопку "Погода на 5 днів"
    markup = types.InlineKeyboardMarkup()
    button_change_city = types.InlineKeyboardButton('Змінити місто', callback_data='change_city')
    button_weather_5_days = types.InlineKeyboardButton('Погода на 5 днів', callback_data='weather_5_days')
    markup.add(button_change_city, button_weather_5_days)

    # Використання методу edit_message_reply_markup для зміни розмітки існуючого повідомлення
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)

# Опціонально: Ви можете змінити також функцію change_city для виведення кнопок "Погода на 3 та 5 днів" та "Погода кожні 3 години" після зміни міста.
def change_city(message):
    chat_id = message.chat.id
    city = message.text

    try:
        weather_info = get_weather(city)
        user_weather[chat_id] = {'weather': weather_info, 'city': city, 'timestamp': time.time()}
        success_message = f"Місто змінено на {city}."
        bot.send_message(chat_id, success_message)
    except Exception as e:
        error_message = "Виникла помилка при отриманні погоди. Будь ласка, перевірте назву міста та спробуйте ще раз."
        bot.send_message(chat_id, error_message)
        return

    # Створення клавіатури для зміни міста та погоди
    markup = types.InlineKeyboardMarkup()
    button_change_city = types.InlineKeyboardButton('Змінити місто', callback_data='change_city')
    button_weather_3_days = types.InlineKeyboardButton('Погода на 3 дні', callback_data='weather_3_days')
    button_weather_5_days = types.InlineKeyboardButton('Погода на 5 днів', callback_data='weather_5_days')
    button_hourly_weather = types.InlineKeyboardButton('Погода кожні 3 години', callback_data='hourly_weather')
    markup.add(button_change_city, button_weather_3_days, button_weather_5_days, button_hourly_weather)

    bot.send_message(chat_id, weather_info, reply_markup=markup)


# Запуск телеграм-бота
bot.polling()