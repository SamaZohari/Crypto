from .base import Base
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import Session
from models import PriceHistory, Transaction  
import requests
from datetime import datetime

class Token(Base):
    __tablename__ = 'token'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_address = Column(String, unique=True, nullable=False)
    symbol = Column(String)
    name = Column(String)
    decimals = Column(Integer)
    api_called = Column(Boolean, default=False)  

    def __init__(self, contract_address, symbol=None, name=None, decimals=None):
        self.contract_address = contract_address
        if symbol is not None:
            self.symbol = symbol
        if name is not None:
            self.name = name
        if decimals is not None:
            self.decimals = decimals

    def get_price(self, session: Session):

        price_history = session.query(PriceHistory).filter_by(token_id=self.id).all()
        if price_history:
            print(f"Price history found for {self.symbol} in the database.")
            return price_history

        print(f"Fetching price history for {self.symbol} from the API.")
        price_data = self.fetch_price_from_api()

        if price_data:
            for entry in price_data:
                price_record = PriceHistory(
                    timestamp=entry['timestamp'],
                    price=entry['price'],
                    token_id=self.id
                )
                session.add(price_record)
            session.commit()

        return session.query(PriceHistory).filter_by(token_id=self.id).all()

    def fetch_price_from_api(self):

        api_url = f"https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses={self.contract_address}&vs_currencies=usd"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()

            return data
        else:
            print(f"Failed to fetch prices for {self.symbol}. Error: {response.status_code}")
            return []

    def get_token_transactions(self, session: Session):

        if self.api_called:
            
            print(f"Fetching transactions for {self.symbol} from the database.")
            transactions = session.query(Transaction).filter_by(token_id=self.id).all()
            return [txn for txn in transactions if txn.transaction_type in ['buy', 'sell']]

        print(f"Fetching transactions for {self.symbol} from the API.")
        transactions_data = self.fetch_transactions_from_api()

        if transactions_data:
            for txn_data in transactions_data:
                transaction = Transaction(
                    hash=txn_data['hash'],
                    timestamp=txn_data['timestamp'],
                    from_address=txn_data['from_address'],
                    to_address=txn_data['to_address'],
                    value_in_token=txn_data['value_in_token'],
                    transaction_type=txn_data['transaction_type'],
                    token_id=self.id
                )
                session.add(transaction)

            self.api_called = True  
            session.commit()

        return [txn for txn in transactions_data if txn['transaction_type'] in ['buy', 'sell']] 

    def fetch_transactions_from_api(self):

        api_url = f"https://api.etherscan.io/api?module=account&action=tokentx&contractaddress={self.contract_address}&page=1&offset=100&sort=asc&apikey=<YOUR_API_KEY>"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed to fetch transactions for {self.symbol}. Error: {response.status_code}")
            return []

