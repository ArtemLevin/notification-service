from sqladmin import ModelView

from admin_panel.models import Recipient


class RecipientAdmin(ModelView, model=Recipient):
    name = "Recipient"
    name_plural = "Recipients"
    icon = "fa-solid fa-user"

    column_list = [Recipient.email]
    column_searchable_list = [Recipient.email]
    form_excluded_columns = [Recipient.created_at, Recipient.updated_at, Recipient.campaigns]