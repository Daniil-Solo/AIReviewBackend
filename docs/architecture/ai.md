## Архитектура использования AI

### Взаимодействие студента, преподавателя и системы

```mermaid
sequenceDiagram
    participant Студент
    participant Преподаватель
    participant Система

    Студент->>Система: Отправка проекта

    Система->>Система: Генерация документации проекта

    Студент->>Система: Валидация сгенерированной документации

    Система->>Система: Генерация комментариев по критериям на основе документации
    Система->>Система: Генерация комментариев по критериям на основе кода

    Преподаватель->>Система: Внесение дополнительных комментариев по критериям

    Система->>Система: Генерация обратной связи по проверке

    Преподаватель->>Система: Корректировка финального вердикта
```


### Общая схема генерации артефактов ревью

```mermaid
flowchart TB
    A2([Project Tree])
    A1([Project Codebase])
    A3[ProjectDoc Generation]
    A4[ProjectDoc Validation]
    A5([Raw ProjectDoc])
    A6([Validated ProjectDoc])

    A1 --> A3
    A2 --> A3 --> A5 --> A4
    A4 --> A6 

    B1([Criteria])
    B2[Grading by ProjectDoc]
    B3([Criteria Checks v1])
    B4[Grading by Code]
    B5([Criteria Checks v2])
    B6[Grading by Teacher]
    B7([Criteria Checks v3])
    B1 --> B2
    A6 --> B2 --> B3 --> B4 --> B5
    A1 --> B4
    B1 --> B4
    B5 --> B6 --> B7

    C1[Feedback Generation]
    C2([Feedback Generation])
    B7 --> C1 --> C2

    %% Input Data
    style A1 fill:#c9f,stroke:#333
    style A2 fill:#c9f,stroke:#333
    style B1 fill:#c9f,stroke:#333

    %% Artifacts
    style A6 fill:#ff0,stroke:#333
    style A5 fill:#ff0,stroke:#333
    style B3 fill:#ff0,stroke:#333
    style B5 fill:#ff0,stroke:#333
    style B7 fill:#ff0,stroke:#333
    style C2 fill:#ff0,stroke:#333
```

### Общая схема генерации артефактов ревью (на русском языке)
flowchart TB
    A2([Дерево проекта])
    A1([Кодовая база проекта])

    subgraph PG [Формирование проектной документации]
        direction LR
        Gen[Первичная генерация]
        Val[Валидация студентом]
        Gen --> Val
    end

    ValidatedDoc([Валидная документация])
    PG --> ValidatedDoc

    subgraph GR [Критериальная проверка]
        direction LR
        G1[Оценка по документации]
        G2[Оценка по коду]
        G3[Оценка преподавателем]
        G1 --> G2 --> G3
    end

    CriteriaChecks([Проверка критериев])
    GR --> CriteriaChecks

    FB[Генерация обратной связи]
    FB_out([Обратная связь])

    B1([Критерии])

    A1 --> PG
    A2 --> PG
    ValidatedDoc --> GR
    A1 --> GR
    B1 --> GR

    CriteriaChecks --> FB --> FB_out

    style A1 fill:#c9f,stroke:#333
    style A2 fill:#c9f,stroke:#333
    style B1 fill:#c9f,stroke:#333
    style ValidatedDoc fill:#ff0,stroke:#333
    style CriteriaChecks fill:#ff0,stroke:#333
    style FB_out fill:#ff0,stroke:#333
```