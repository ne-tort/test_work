from locust import FastHttpUser, task, constant, events
from threading import Lock
from logging import getLogger
import random
from decimal import Decimal

class TestWallet(FastHttpUser):
    wait_time = constant(0)
    balance_lock = Lock()
    logger = getLogger(__name__)
    wallet_uuid = None

    def on_start(self):
        with TestWallet.balance_lock:
            if TestWallet.wallet_uuid is None:
                self.create_wallet('100.00')

    def create_wallet(self, amount):
        response = self.client.post(f"/api/v1/wallets/new_wallet/{amount}")
        if response.status_code == 200:
            TestWallet.wallet_uuid = response.json().get("wallet_uuid")
            TestWallet.logger.info(f"Wallet created, uuid: {TestWallet.wallet_uuid}")
        else:
            raise Exception(f"Failed to create wallet: {response.status_code}")

    @task
    def check_balance(self):
        with self.client.get(f"/api/v1/wallets/{TestWallet.wallet_uuid}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get balance: {response.status_code}")

    @task
    def withdraw(self):
        amount = Decimal(random.uniform(0.1, 100)).quantize(Decimal('0.01'))
        with self.client.post(f"/api/v1/wallets/{TestWallet.wallet_uuid}/operation", json={
            "operation": "WITHDRAW",
            "amount": str(amount)
        }, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 400:
                response.success()
            else:
                response.failure(f"Unknown error: {response.status_code}")


    @task
    def deposit(self):
        amount = Decimal(random.uniform(0.1, 100)).quantize(Decimal('0.01'))
        with self.client.post(f"/api/v1/wallets/{TestWallet.wallet_uuid}/operation", json={
            "operation": "DEPOSIT",
            "amount": str(amount)
        }, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unknown error: {response.status_code}")

@events.test_stop.add_listener
def clear(environment, **kwargs):
    TestWallet.wallet_uuid = None
    environment.stats.reset_all()
    environment.runner.stats.total.reset()
    environment.runner.stats.clear_all()