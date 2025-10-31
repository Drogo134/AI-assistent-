SwiftWhisper

Краткий запуск
- Установите зависимости:
  - python -m venv .venv
  - .venv\Scripts\pip install --upgrade pip
  - .venv\Scripts\pip install -r requirements.txt

- Вариант 1: только распознавание (терминал)
  - .venv\Scripts\python swiftwhisper.py

- Вариант 2: голосовой ассистент
  - .venv\Scripts\python swift_assistant.py

Примечания
- По умолчанию используется openai-whisper модель "small" (CPU).
- Для Linux-управления медиаплеером задействован модуль media_control (DBus/MPRIS).

Голосовые команды (для swift_assistant.py)
- Активация: "computer" (или фразы: "hey computer", "okay computer", "ok computer")
- Wikipedia: "computer wikipedia <запрос>", "computer wiki <запрос>"
- Музыка: "play", "pause", "stop", "next", "previous"
- Громкость: "volume up", "volume down"
- Погода: "weather"
- Время: "time"
- Дата: "date"
- День недели: "day", "today"
- Шутка: "joke"
- Завершение ассистента: "terminate"

