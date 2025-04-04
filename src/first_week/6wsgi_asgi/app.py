import json
import requests
from wsgiref.simple_server import make_server


def fetch_exchange_rate(currency):
    url = f"https://api.exchangerate-api.com/v4/latest/{currency}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
    except Exception as e:
        print(f"Возникла ошибка при запросе данных: {e}")
    return None


def app(environ, response):
    # Получаем URL от нашего клиента
    path = environ.get("PATH_INFO", "/")

    # Извлекаем валюту из URL, например: /USD
    currency = path.strip("/").upper()

    # Получаем данные по валюте от API exchangerate-api.com
    exchange_data = fetch_exchange_rate(currency)

    if exchange_data:
        response_body = json.dumps(exchange_data).encode("utf-8")
        status = "200 OK"
    else:
        response_body = json.dumps(
            {"error": "Валюта не найдена или запрос завершился ошибкой"}
        ).encode("utf-8")
        status = "404 Not Found"

    headers = [("Content-Type", "application/json")]
    response(status, headers)
    return [response_body]


if __name__ == "__main__":
    # Создаем и запускаем WSGI сервер
    server = make_server("", 8000, app)
    print("App_currency is running on port 8000...")
    server.serve_forever()
