class PriceHistory(Base):
    __tablename__ = 'price_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(BigInteger)
    price = Column(Float)

    token_id = Column(Integer, ForeignKey('token.id'))
    token = relationship('Token', backref='price_history')
    __table_args__ = (UniqueConstraint('timestamp', 'token_id'),)

    def __init__(self, timestamp, price, contract_address=None, session=None):
        self.timestamp = timestamp
        self.price = price

        if session is not None:
            self.token = session.query(Token).filter_by(contract_address=contract_address).first()