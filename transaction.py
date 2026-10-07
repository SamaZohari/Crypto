from .base import Base, Column, String, Integer, Float, ForeignKey, UniqueConstraint
from .token import Token
from sqlalchemy.orm import relationship

class Transaction(Base):
    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hash = Column(String, nullable=False)
    block_number = Column(Integer)
    timestamp = Column(Integer, nullable=False)
    block_hash = Column(String)
    from_address = Column(String, nullable=False)
    to_address = Column(String, nullable=False)
    value_in_token = Column(Float, nullable=False)
    value_in_usd = Column(Float)
    transaction_type = Column(String)
    __table_args__ = (UniqueConstraint('hash', 'transaction_type'),)

    token_id = Column(Integer, ForeignKey('token.id'))
    token = relationship('Token', backref='transaction')

    def __init__(self, hash, timestamp, from_address, to_address,
                 value_in_token, contract_address=None, session=None, block_number=None, block_hash=None, value_in_usd=None, transaction_type=None):
        self.hash = hash
        self.timestamp = timestamp
        self.from_address = from_address
        self.to_address = to_address
        self.value_in_token = value_in_token
        if session is not None and contract_address is not None:
            self.token = session.query(Token).filter_by(contract_address=contract_address).first()
        if block_number is not None:
            self.block_number = block_number
        if block_hash is not None:
            self.block_hash = block_hash
        if value_in_usd is not None:
            self.value_in_usd = value_in_usd
        if transaction_type is not None:
            self.transaction_type = transaction_type

    def get_transaction_type(self, pool_addresses):
        lowercase_contract_address = self.token.contract_address.lower()
        for pool_address in pool_addresses:
            lowercase_pool_address = pool_address.address.lower()
            if self.to_address.lower() == lowercase_contract_address:
                return 'tax'
            elif (
                self.from_address.lower() == lowercase_contract_address
                and lowercase_pool_address == self.to_address.lower()
            ):
                return 'pool_fill'
            elif (
                lowercase_pool_address == self.from_address.lower()
                and self.token.contract_address.lower() == lowercase_contract_address
            ):
                return 'buy'
            elif (
                lowercase_pool_address == self.to_address.lower()
                and self.token.contract_address.lower() == lowercase_contract_address
            ):
                return 'sell'
        return 'transfer'
