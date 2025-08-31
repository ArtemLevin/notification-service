from sqlalchemy import Text, String, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from admin_panel.models.base import Base
from admin_panel.admin.jinja_setup import validate_template_string


class MessageTemplate(Base):
    __tablename__ = "templates"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    # связь с кампаниями
    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="template")

    def __str__(self) -> str:
        return f"{self.name}"


@event.listens_for(MessageTemplate, "before_insert")
@event.listens_for(MessageTemplate, "before_update")
def validate_message_template(mapper, connection, target):
    validate_template_string(getattr(target, "body") or "")