## Рабочие пространства

Рабочее пространство (workspace) - это единое пространство, куда можно добавлять участников, создавать задачи и смотреть аналитику.


### Создание рабочего пространства

Форма создания:
- Название (name)
- Описание (description)

После успешного заполнения:
- создается рабочее пространство
- создается первый участник с ролью владелец (OWNER)
- открывается страница пространства


Эндпоинты:
- `POST /workspaces`: Request: {name, description}, Response {id, name, description, created_at}


### Редактирование рабочего пространства

Форма редактирования:
- Название (name)
- Описание (description)

Эндпоинты:
- `PUT /workspaces/:id`: Request: {name, description}, Response {id, name, description, created_at}


### Архивация рабочего пространства

Эндпоинты:
- `DELETE /workspaces/:id`:  Response {message}

Пространство не удаляется физически


### Просмотр рабочего пространства

Рабочее пространство представляет собой страницу с информацией:
- Название и описание
- Задачи (tasks)
- Участники (members)
- Приглашения (join_rules)

Для пользователя, не являющегося участником пространства, доступ закрыт!

Эндпоинты:
- `GET /workspaces/:id`: Response {id, name, description, created_at}
- `GET /workspaces/:id/tasks`: Response [{id, name, description}]
- `GET /workspaces/:id/members`: Response [{id, fullname, email, role}]
- `GET /workspaces/:id/join_rules`: Response [{id, workspace_id, slug, role, expired_at}]


### Добавление участников по ссылке

Добавить участника в пространстве можно по специальной ссылке вида https://<website>/join/<slug>.

В интерфейсе можно задать правило приглашения для каждой ссылки:
- строка (slug), которая будет отображаться в ссылке (можно сгенерировать случайную строку)
- назначаемая роль по ссылке (role): преподаватель (TEACHER) или студент (STUDENT)
- дата прекращения действия ссылки (expired_at), но ее можно не указывать

При переходе по ссылке:
- пользователь становится участником пространства с указанной ролью
- пользователь переходит на страницу пространства

Эндпоинты:
- `POST /workspaces/:id/join_rules`: Request {slug, role, expired_at}, Response {id, workspace_id, slug, role, expired_at}
- `PUT /workspaces/:id/join_rules/:id`: Request {slug, role, is_active, expired_at}, Response {id, workspace_id, slug, role, expired_at}
- `DELETE /workspaces/:id/join_rules/:id`: Response {message}
- `POST /joins` Request {slug}, Response {workspace_id} - отправляется из фронтенда при переходе по ссылке


### Изменить роль участника

Эндпоинты:
- `PATCH /workspaces/:id/members/:id`:  Request {role} Response {id, fullname, email, role}

Нужно быть владельцем


### Выход из пространства

Эндпоинты:
- `POST /workspaces/:id/leave`:  Response {id, fullname, email, role}

Не доступен владельцу


### Передача владения

Эндпоинты:
- `PATCH /workspaces/:id/owner`:  Request {member_id} Response {id, name, description, created_at}

Доступна только владельцу