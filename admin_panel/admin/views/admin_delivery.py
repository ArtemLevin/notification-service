from sqladmin import ModelView

from admin_panel.models import DeliveryHistory


class DeliveryHistoryAdmin(ModelView, model=DeliveryHistory):
    name = "Delivery"
    name_plural = "Deliveries"
    icon = "fa-solid fa-clock-rotate-left"

    column_list = [DeliveryHistory.status]
    column_searchable_list = [DeliveryHistory.status]
    form_excluded_columns = [DeliveryHistory.created_at, DeliveryHistory.updated_at]