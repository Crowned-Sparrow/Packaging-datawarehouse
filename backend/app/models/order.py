# app/models/order.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
#from app.models.customer import Customer
from app.core.database import Base


class Order(Base):
    __tablename__ = "fact_orders"

    order_id        = Column(Integer, primary_key=True, autoincrement=True)
    pds             = Column(String(20), unique=True, nullable=True)
    customer_id     = Column(Integer, ForeignKey("dim_customers.customer_id"), nullable=False)
    order_date      = Column(Date, nullable=False)
    delivery_date   = Column(Date, nullable=True)
    quantity        = Column(Integer, nullable=False)
    order_note      = Column(String, nullable=True)
    order_status    = Column(
        String(20),
        nullable=False,
        default="pending",
    )

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_quantity_positive"),
        CheckConstraint(
            "order_status IN ('pending', 'in_progress', 'delivered', 'cancelled')",
            name="ck_order_status_valid",
        ),
    )

    customer = relationship("Customer", back_populates="orders")

    def __repr__(self):
        return f"<Order id={self.order_id} pds={self.pds!r} status={self.order_status!r}>"