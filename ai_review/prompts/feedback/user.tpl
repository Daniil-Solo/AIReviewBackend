# Информация о проекте

## Критерии
{% for criterion in criteria %}
### {{ criterion.description }}
Комментарий: {{ criterion.comment }}
Критерий пройден: {{ criterion.is_passed }}
{% endfor %}
