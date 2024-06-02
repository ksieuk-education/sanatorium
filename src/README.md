# SPD Uploader App

## Запуск

В проект добавлен файл `config.yaml` для настройки приложения

```bash
cp .env.example .env
cp .example.config.yaml .config.yaml
```

```bash
docker-compose up --build
```

## Тесты

```bash
docker-compose -f "docker-compose.tests.yml" up --build
```
