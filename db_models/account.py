from sqlalchemy import Column, String, Integer
from db_models.base import Base


class AccountTransactionTemplate(Base):
    """Модель таблицы accounts_transaction_template"""
    __tablename__ = 'accounts_transaction_template'

    user = Column(String, primary_key=True)
    balance = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Account(user='{self.user}', balance={self.balance})>"