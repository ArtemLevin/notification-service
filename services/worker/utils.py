from typing import Dict, Any

from jinja2 import Environment, BaseLoader, StrictUndefined


_j2 = Environment(loader=BaseLoader(), undefined=StrictUndefined, autoescape=False)


async def render_template(body: str, context: Dict[str, Any]) -> str:
    tmpl = _j2.from_string(body)
    return tmpl.render(**context)
