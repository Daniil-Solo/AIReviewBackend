## Профиль

### Получение информации о пользователе

При переходе на страницу профиля пользователя видна информация по нему

Если пользователь зашел в свой профиль, ему доступны дополнительные секции:
- доступные пространства
- решаемые задачи

Эндпоинты:
- `GET /users/me`: Response {fullname, email, created_at}
- `GET /users/:id`: Response {fullname, email, created_at}
- `GET /users/me/workspaces`: Response [{id, name, role}]
- `GET /users/me/solutions`: Response [{id, workspace_id, task_id, task_name, status}]
