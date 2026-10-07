```markdown
# Ethereum Token ETL & Relational Data Models

A lightweight, modular data persistence layer built with Python and SQLAlchemy to model, track, and persist on-chain Ethereum activity and token market pricing.

---

## Architecture Overview

This module acts as the relational schema and ingestion layer for Ethereum on-chain events and market pricing feeds. It maps smart contract metadata, transaction events, decentralized liquidity pools, and historical pricing snapshots into normalized tables enforced by relational constraints.

```text
├── models/
│   ├── __init__.py           # Package exports and module registration
│   ├── base.py               # Shared declarative base and common SQLAlchemy types
│   ├── token.py              # Core token entity (contract address, symbol, decimals)
│   ├── transaction.py        # On-chain transfer events, block numbers, and addresses
│   ├── price_history.py      # Historical token pricing and timestamp-based queries
│   └── pool_address.py       # Liquidity pool registry and contract mappings

```

---

## Schema & Entity Relationship

```text
               +-------------------+
               |       Token       |
               +-------------------+
               | id (PK)           |
               | contract_address  | <---+ (Unique)
               | symbol, name      |     |
               | decimals          |     |
               +---------+---------+     |
                         |               |
         +---------------+---------------+
         | (1:N)         | (1:N)         | (1:N)
         v               v               v
+-----------------+ +-------------+ +--------------------+
|  PriceHistory   | | PoolAddress | |    Transaction     |
+-----------------+ +-------------+ +--------------------+
| id (PK)         | | id (PK)     | | id (PK)            |
| token_id (FK)   | | token_id(FK)| | token_id (FK)      |
| timestamp       | | address     | | hash, block_number |
| price           | +-------------+ | from/to_address    |
+-----------------+                 | value, timestamp   |
(Unique: token_id                   +--------------------+
 + timestamp)

```

---

## Module Breakdown

### 1. `base.py`

* Initializes `Base = declarative_base()`.
* Exports centralized SQLAlchemy types and ORM helper functions across models.

### 2. `token.py`

* Represents tracked ERC-20 / Ethereum tokens.
* Fields: `contract_address` (unique constraint), `symbol`, `name`, `decimals`, and status flags.
* Establishes foreign-key anchor points for transactions, liquidity pools, and price feeds.

### 3. `transaction.py`

* Persists on-chain transaction logs and transfer events.
* Fields: `hash`, `block_number`, `timestamp`, `block_hash`, `from_address`, `to_address`, and token transfer amounts.
* Implements relationships linking individual transactions back to parent tokens.

### 4. `price_history.py`

* Captures historical token prices over discrete timestamps.
* Enforces a composite constraint `UniqueConstraint('timestamp', 'token_id')` to prevent duplicate price snapshots.
* Provides helper ingestion routines to resolve or cache token records dynamically.

### 5. `pool_address.py`

* Tracks decentralized exchange (DEX) liquidity pool addresses mapped to specific tokens.
* Enforces unique pool address constraints to avoid duplicate registry entries.

---

## Setup & Usage

### Installation

```bash
pip install sqlalchemy requests

```

### Initializing the Database & Creating Tables

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Token, PriceHistory, Transaction, PoolAddress

# Create engine (SQLite or PostgreSQL)
DATABASE_URL = "sqlite:///crypto_data.db"
engine = create_engine(DATABASE_URL, echo=False)

# Create all schema tables
Base.metadata.create_all(engine)

# Bind session
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

```

### Basic Insert & Query Example

```python
from models import Token, PriceHistory

# 1. Register a Token
token = Token(
    contract_address="0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
    symbol="UNI",
    name="Uniswap",
    decimals=18
)
session.add(token)
session.commit()

# 2. Record Historical Price
price_entry = PriceHistory(
    timestamp=1696118400,
    price=5.42,
    contract_address=token.contract_address,
    session=session
)
session.add(price_entry)
session.commit()

# 3. Query Token with Relationships
queried_token = session.query(Token).filter_by(symbol="UNI").first()
for record in queried_token.price_history:
    print(f"Timestamp: {record.timestamp} | Price: ${record.price}")

```

---

## Key Features & Design Choices

* **Relational Integrity:** Foreign keys tie all child records (`Transaction`, `PriceHistory`, `PoolAddress`) directly to the canonical `Token` entity.
* **Deduplication:** Composite constraints on `(token_id, timestamp)` guarantee idempotent price ingestion cycles.
* **Separation of Concerns:** Each blockchain primitive is decoupled into its own file, facilitating pipeline extensions such as event listeners, Celery tasks, or analytics scripts.

```

```
