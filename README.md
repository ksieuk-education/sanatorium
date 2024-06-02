# Сервис для работы с ИС Витриной данных

Задача в JIRA: https://wiki.mogt.ru/jira/browse/ISOGD-1811

## Начало работы

```bash
cd src
```

## Подготовка к запуску

```bash
cp .env.example .env
cp .example.config.yaml .config2.yaml
```

## Запуск через Virtual Venv

```bash
python -m venv .venv
```

Активируем виртуальное окружение

На OX системах:

```bash
source .venv/bin/activate
```

На Windows:

```bash
.\.venv\Scripts\activate
```

```bash
pip install poetry
poetry install
```

## Запуск через Docker

```bash
docker-compose up --build -d
```
