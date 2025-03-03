import redis
from decimal import Decimal

class RedisClient:
    def __init__(self, host="localhost", port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def new_wallet(self, wallet_uuid: str, amount: str):
        existing_balance = self.client.get(f"wallet:{wallet_uuid}")
        if existing_balance:
            raise ValueError(f"Wallet {wallet_uuid} already exists.")
        self.client.set(f"wallet:{wallet_uuid}", int(Decimal(amount) * 100))

    def change_balance(self, wallet_uuid: str, amount: Decimal):
        amount_in_cents = int(amount * 100)
        self.client.incrby(f"wallet:{wallet_uuid}", amount_in_cents)

    def get_balance(self, wallet_uuid: str):
        balance = self.client.get(f"wallet:{wallet_uuid}")
        if balance:
            return Decimal(int(balance)) / 100
        else:
            return Decimal("0.00")
