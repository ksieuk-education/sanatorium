#!/bin/bash

# Функция для проверки доступности URL
check_url() {
    local url=$1
    if curl --max-time 10 --silent --output /dev/null --get --fail "$url"; then
        echo "URL $url доступен"
        return 0
    else
        echo "URL $url недоступен"
        return 1
    fi
}


# Функция для циклической проверки URL
check_url_cycle() {
    local url=$1
    local attempts=$2
    local interval=$3

    for ((i = 1; i <= $attempts; i++)); do
        echo "Попытка $i:"
        check_url "$url"
        if [ $? -eq 0 ]; then
            return 0
        fi
        sleep "$interval"
    done
    echo "Не удалось подключиться к $url после $attempts попыток"
    return 1
}

health_url="${PROJECT_MEDIA_PROTOCOL}://${PROJECT_MEDIA_HOST}:${PROJECT_MEDIA_PORT}/api/v1/health"
rabbitmq_url="${RABBITMQ_PROTOCOL}://${RABBITMQ_HOST}:${RABBITMQ_MANAGEMENT_PORT}"

if check_url_cycle "$health_url" 20 15; then
    if check_url_cycle "$rabbitmq_url" 3 5; then
        exec .venv/bin/python -m bin
    else
        echo "Не удалось выполнить команду из-за недоступности URL $rabbitmq_url"
    fi
else
    echo "Не удалось выполнить команду из-за недоступности URL $health_url"
fi
