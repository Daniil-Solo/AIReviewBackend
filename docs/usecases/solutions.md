## Решения

### Создание решения

Форма создания решения открывается из конкретной задачи

Форма создания задачи:
- Название (name)
- Описание (description)
- Формат решения (format): github-репозиторий или zip
- Ссылка на репозиторий GitHub (github_link), если format=github
- ZIP-файл с кодом проекта (zip_file), если format=zip

Для каждого задания студент может отправить только одно решение

Эндпоинты:
- `POST /solutions`: Request {task_id, format, github_link, zip_file} Response {id, task_id, format, status, created_at}


### Получение информации о решении

Операция разрешена только для автора решения или для пользователей с ролями Преподаватель и Владалец в пространстве

Для преподавателя доступны дополнительные секции: project_doc, критерии и результаты экзамена если есть.

Эндпоинты:
- `GET /solutions/:id`: Response {id, workspace_id, task_id, task_name, status, format, created_at, created_by}
- `GET /solutions/:id/report`: Response {project_doc, criteria_checks, exam}


### Экзаменация

Когда вопросы для экзамена будут готовы, у студента появится возможность начать экзамен.

Время на выполнение экзамена ограничено 60 минутами. После его истечения экзамен считается проваленным

После ответа на все вопросы необходимо прожать кнопку "Завершить экзамен", чтобы ответы были отправлены на проверку.

Эндпоинты:
- `POST /solutions/:id/exam/start`: Response {message}
- `GET /solutions/:id/exam`: Response {expired_at, items: [{code, query, answer}]}
- `POST /solutions/:id/exam/finish`: Request [{code, answer}], Response {message}


