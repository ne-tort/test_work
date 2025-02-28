from locust import HttpUser, task, between
from threading import Lock
from logging import getLogger
import random
from multiprocessing import Value

class TestWallet(HttpUser):
    wait_time = between(0.1, 0.5)
    balance_lock = Lock()
    logger = getLogger(__name__)
    wallet_uuid = None
    balance = Value("d", 1000.0)

    def on_start(self):
        if TestWallet.wallet_uuid is None:
            self.create_wallet()

    def create_wallet(self):
        response = self.client.post(f"/api/v1/wallets/new_wallet/{round(TestWallet.balance.value, 2)}", catch_response=True)
        if response.status_code == 200:
            with TestWallet.balance_lock:
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
        amount = round(random.uniform(0.1, 100), 2)
        with self.client.post(f"/api/v1/wallets/{TestWallet.wallet_uuid}/operation", json={
            "operation": "WITHDRAW",
            "amount": amount
        }, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 400:
                response.success()
            else:
                response.failure(f"Unknown error: {response.status_code}")


    @task
    def deposit(self):
        amount = round(random.uniform(0.1, 100), 2)
        with self.client.post(f"/api/v1/wallets/{TestWallet.wallet_uuid}/operation", json={
            "operation": "DEPOSIT",
            "amount": amount
        }, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unknown error: {response.status_code}")