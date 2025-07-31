# Stripe тестовое
### Делал по бонусным заданиям через Stripe Payment Intent.
### Выполнил все бонусные задания.
 
## Запуск через докер

```cmd
    docker build . -t stripe
```

```cmd
    docker run -p 8000:8000 stripe
```

## Запуск через python.

###  Ставим виртуальное окружение
```cmd
    python -m venv venv
```

###  Активируем виртуальное окружение
```cmd
    \venv\Scripts\activate
```

###  Загружаем зависимости
```cmd
    pip install -r requirements.txt
```

###  Запускаем 
```cmd
    python manage.py runserver
```