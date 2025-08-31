from admin_panel.generator.recipients import init_recipients
from admin_panel.generator.templates import init_templates

async def init_all():
    await init_templates()
    await init_recipients()

__all__ = ['init_recipients', 'init_templates', 'init_all']