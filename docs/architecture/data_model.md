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
        bool is_archived
        datetime created_at
    }

    workspace_members  {
        integer id PK
        integer workspace_id FK
        integer user_id FK
        workspace_member_role_enum role
        datetime created_at
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
        string hashed_password
        integer used_count
        bool is_active
        workspace_member_role_enum role
        datetime expired_at
    }

    tasks {
        integer id PK
        integer workspace_id FK
        string name
        string description
        bool is_active
        integer created_by FK
        datetime created_at
        bool use_exam
    }

    task_steps_models {
        integer id PK
        integer task_id FK, U
        jsonb steps
        datetime created_at
        datetime updated_at
    }
    
    criteria {
        integer id PK
        string description
        array tags
        nullable_criterion_stage_enum stage
        string prompt
        integer workspace_id FK
        integer task_id FK
        integer created_by FK
        datetime created_at
    }
    
    criterion_stage_enum {
        string PROJECTDOC
        string CODEBASE
        string MANUAL
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
        string github_repo_link
        string github_repo_branch
        string artifact_path
        solution_status_enum status
        jsonb steps
        nullable_integer human_grade
        nullable_string human_feedback
        nullable_string ai_feedback
        integer created_by FK
        datetime created_at
    }
    
    solution_status_enum {
        string CREATED
        string ERROR
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
    
    solution_criteria_checks {
        integer id PK
        integer task_criterion_id FK
        integer solution_id FK
        string comment
        criterion_stage_enum stage
        criterion_check_status_enum status
        nullable_bool is_passed
        datetime created_at
    }
    
    criterion_check_status_enum {
        string SUFFICIENT
        string NEEDS_CODE
        string NEEDS_STUDENT
        string NEEDS_MANUAL
        string NOT_APPLICABLE
    }

    pipeline_tasks {
        integer id PK
        integer solution_id FK
        string step
        string status
        nullable_string error_text
        nullable_float duration
        datetime last_checked_at
        datetime ran_at
        datetime created_at
    }
    
    transactions {
        integer id PK
        integer user_id FK
        float amount
        string type
        jsonb metadata
        datetime created_at
    }

    custom_models {
        integer id PK
        integer workspace_id FK
        integer created_by FK
        string name
        string base_url
        string encrypted_api_key
        string model
        bool is_active
        datetime created_at
    }

    users ||--|{ workspace_members   : "is a part of"
    workspaces ||--|{ workspace_join_rules   : uses
    workspaces ||--|{ workspace_members   : contains
    workspace_members   ||..|| workspace_member_role_enum : has
    workspace_join_rules   ||..|| workspace_member_role_enum : has
    
    workspaces ||--|{ tasks : contains
    workspaces ||--|{ custom_models : contains
    workspaces ||--|{ criteria : has
    tasks ||--|| task_steps_models : "configured in"
    tasks ||--|{ criteria : has
    users ||--|{ tasks : creates
    users ||--|{ criteria : creates
    
    tasks ||--|{ task_criteria : "has"
    criteria ||--|{ task_criteria : "included in"
    criteria  ||..|| criterion_stage_enum : has
    
    task_criteria ||..|{ solution_criteria_checks : "verified by"
    solution_criteria_checks ||..|| criterion_check_status_enum : has
    solution_criteria_checks  ||..|| criterion_stage_enum : has
    solutions ||..|{ solution_criteria_checks : has
    
    users ||--|{ solutions : creates

    tasks ||--|{ solutions : "solved in"
    solutions ||..|| solution_format_enum : has
    solutions ||..|| solution_status_enum : has
    solutions ||--|{ pipeline_tasks : "processed by"
    
    users ||..|{ transactions : has
    users ||--|{ custom_models : creates
```
