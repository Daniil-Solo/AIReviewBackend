## Модель данных проекта

```mermaid
erDiagram
    users {
        integer id PK
        string fullname
        string email
        string hashed_password
        bool is_verified
        bool is_admin
        datetime created_at
    }
    
    workspaces {
        integer id PK
        string name
        string description
        datetime created_at
    }

    workspace_members  {
        integer id PK
        integer workspace_id FK
        integer user_id FK
        workspace_member_role_enum  role
    }

    workspace_member_role_enum {
        string OWNER
        string TEACHER
        string STUDENT
    }
    
    workspace_join_rules {
        integer id PK
        integer workspace_id FK
        string slug
        workspace_member_role_enum role
        datetime expired_at
    }

    tasks {
        integer id PK
        string name
        string description
        bool is_active
        integer created_by FK
        datetime created_at
        bool use_exam
    }
    
    criteria {
        integer id PK
        string code
        integer task_id FK
        string description
        bool is_public
        array tags
        integer created_by
    }
    
    task_criteria {
        integer id PK
        integer task_id FK
        integer criterion_id FK
        float weight
    }

    solutions {
        integer id PK
        integer task_id FK
        solution_format_enum format
        string link
        solution_status_enum status
        integer created_by FK
        datetime created_at
        integer human_grade
        string human_comment
    }

    solution_status_enum {
        string CREATED
        string FAILED
        string AI_REVIEW
        string WAITING_EXAM
        string EXAMINATION
        string HUMAN_REVIEW
        string REVIEWED
    }

    solution_format_enum {
        string ZIP
        string GITHUB
    }

    solution_artifacts {
        integer solution_id PK, FK
        %% Raw data
        string project_tree_link
        string project_content_link
        %% Project-doc
        string project_doc
        %% Criteria checks
        jsonb project_doc_criteria_checks
        jsonb codebase_criteria_checks
        jsonb agent_criteria_checks
        %% code, comment, confidence, value
        %% Exam questions
        jsonb questions
        %% code, text
    }
    
    solution_exams {
        integer solution_id PK, FK
        datetime expired_at
        %% code, text
        jsonb answers
    }
    
    transactions {
        integer id PK
        integer user_id FK
        float amount
        transaction_type_enum type
        jsonb metadata
    }

    transaction_type_enum {
        string WELCOME_BONUS
        string REVIEW
        string ADMIN_TOP_UP
        string DEPOSIT
    }

    users ||--|{ workspace_members   : "is a part of"
    workspaces ||--|{ workspace_join_rules   : uses
    workspaces ||--|{ workspace_members   : contains
    workspace_members   ||..|| workspace_member_role_enum : has
    workspace_join_rules   ||..|| workspace_member_role_enum : has
    
    workspaces ||--|{ tasks : contains
    users ||--|{ tasks : creates
    users ||--|{ criteria : creates

    users ||--|{ solutions : creates

    tasks ||--|{ solutions : "solved in"
    solutions ||..|| solution_format_enum : has
    solutions ||..|| solution_status_enum : has
    solutions ||--|| solution_artifacts: "extra described in"
    solutions ||--|| solution_exams: "extra estimated in"
    
    tasks ||--|{ task_criteria : "has"
    criteria ||--|{ task_criteria : "included in"
    
    users ||..|{ transactions : has
    transactions ||..|| transaction_type_enum : has
```
