from sqladmin import ModelView

from admin_panel.models import Campaign


class CampaignAdmin(ModelView, model=Campaign):
    name = "Campaign"
    name_plural = "Campaigns"
    icon = "fa-solid fa-paper-plane"

    column_list = [Campaign.name, Campaign.created_at]
    column_searchable_list = [Campaign.name]
    column_sortable_list = [Campaign.name]
    form_excluded_columns = [Campaign.created_at, Campaign.updated_at, Campaign.deliveries]