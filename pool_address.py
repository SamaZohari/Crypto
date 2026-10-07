from .base import Base, Column, String, Integer, ForeignKey
from .token import Token
from sqlalchemy.orm import Session, relationship

class PoolAddress(Base):
    __tablename__ = 'pool_address'

    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String, unique=True, nullable=False)
    token_id = Column(Integer, ForeignKey('token.id'))
    token = relationship('Token', backref='pool_address')

    def __init__(self, address, contract_address, session: Session):
        self.address = address
        self.token = session.query(Token).filter_by(contract_address=contract_address).first()
