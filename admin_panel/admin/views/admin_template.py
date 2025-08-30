from markupsafe import Markup
from sqladmin import ModelView

from admin_panel.models import MessageTemplate


class MessageTemplateAdmin(ModelView, model=MessageTemplate):
    name = "Template"
    name_plural = "Templates"
    icon = "fa-solid fa-file-alt"
    column_list = [MessageTemplate.id, MessageTemplate.name, "preview_link", MessageTemplate.created_at]
    column_searchable_list = [MessageTemplate.name]
    column_sortable_list = [MessageTemplate.name, MessageTemplate.created_at, MessageTemplate.created_at]
    form_excluded_columns = [MessageTemplate.created_at, MessageTemplate.updated_at, MessageTemplate.campaigns]

    # Кастомный рендер колонки
    column_formatters = {
        "preview_link": lambda m, _: Markup(
            f'<a href="/templates/{m.id}/raw" target="_blank">👀 Preview</a>'
        )
    }

    column_export_list = [
        MessageTemplate.id, 
        MessageTemplate.name, 
        MessageTemplate.body, 
        MessageTemplate.created_at, 
        MessageTemplate.updated_at
    ]

    def date_format(value):
        return value.strftime("%d.%m.%Y")
    