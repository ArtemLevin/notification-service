from jinja2 import StrictUndefined, BaseLoader, meta
from jinja2.sandbox import SandboxedEnvironment
from jinja2.exceptions import TemplateSyntaxError
import re

# Инициализация окружения Jinja2
jinja_env = SandboxedEnvironment(
    loader=BaseLoader(),
    undefined=StrictUndefined,
    autoescape=True, 
)

# Разрешённые переменные
ALLOWED_TOP_LEVEL_VARS = {
    "user", "extra", "current_date"
}

# Запрещённые теги
FORBIDDEN_TAGS_RE = re.compile(
    r'{%\s*(extends|include|import|from|call|macro)\b',
    re.IGNORECASE
)

# Добавляем безопасные фильтры
def format_date(value, fmt="%d %B %Y"):
    if hasattr(value, "strftime"):
        return value.strftime(fmt)
    return str(value)

jinja_env.filters.clear()
jinja_env.filters.update({
    "format_date": format_date,
    "upper": lambda s: str(s).upper(),
    "lower": lambda s: str(s).lower(),
    "join": lambda seq, sep=', ': sep.join(map(str, seq)),
})


def validate_template_string(template_str: str) -> None:
    """Валидация шаблона"""
    if not template_str:
        return

    if len(template_str) > 100_000:
        raise ValueError("Шаблон слишком большой")

    if FORBIDDEN_TAGS_RE.search(template_str):
        raise ValueError("Использование extends/include/import/macro/call запрещено")

    try:
        ast = jinja_env.parse(template_str)
    except TemplateSyntaxError as e:
        raise ValueError(f"Ошибка синтаксиса: {e.message} (строка {e.lineno})")

    used = meta.find_undeclared_variables(ast)
    invalid = set(used) - ALLOWED_TOP_LEVEL_VARS
    if invalid:
        raise ValueError(f"Недопустимые переменные: {', '.join(invalid)}")

