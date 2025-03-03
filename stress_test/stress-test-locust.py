import time
from locust import FastHttpUser, task, constant, events
from logging import getLogger
import random
from decimal import Decimal
from threading import Lock
import requests
from redis_client import RedisClient


class TestWallet(FastHttpUser):
    wait_time = constant(0)
    lock = Lock()
    logger = getLogger(__name__)
    wallet_uuid = None
    check_final_balance = False
    redis_client = RedisClient(host='localhost', port=6379, db=0)

    def on_start(self):
        with TestWallet.lock:
            if TestWallet.wallet_uuid is None:
                self.create_wallet("100.00")

    def create_wallet(self, amount):
        response = self.client.post(f"/api/v1/wallets/new_wallet/{amount}")
        if response.status_code == 200:
            TestWallet.wallet_uuid = response.json().get("wallet_uuid")
            TestWallet.logger.info(f"Wallet created, uuid: {TestWallet.wallet_uuid}")
            if TestWallet.check_final_balance:
                TestWallet.redis_client.new_wallet(TestWallet.wallet_uuid, amount)
        else:
            raise Exception(f"Failed to create wallet: {response.status_code} - {response.text}")


    @task
    def withdraw(self):
        amount = Decimal(random.uniform(0.1, 100)).quantize(Decimal('0.01'))
        with self.client.post(f"/api/v1/wallets/{TestWallet.wallet_uuid}/operation", json={
            "operation": "WITHDRAW",
            "amount": str(amount)
        }, catch_response=True) as response:
            if response.status_code == 200:
                if TestWallet.check_final_balance:
                    TestWallet.redis_client.change_balance(TestWallet.wallet_uuid, -amount)
                response.success()
            elif response.status_code == 400:
                response.success()
            else:
                response.failure(f"Unknown error: {response.status_code} - {response.text}")


    @task
    def deposit(self):
        amount = Decimal(random.uniform(0.1, 100)).quantize(Decimal('0.01'))
        with self.client.post(f"/api/v1/wallets/{TestWallet.wallet_uuid}/operation", json={
            "operation": "DEPOSIT",
            "amount": str(amount)
        }, catch_response=True) as response:
            if response.status_code == 200:
                if TestWallet.check_final_balance:
                    TestWallet.redis_client.change_balance(TestWallet.wallet_uuid, amount)
                response.success()
            else:
                response.failure(f"Unknown error: {response.status_code} - {response.text}")


def get_balance():
    url = f"http://localhost:8000/api/v1/wallets/{TestWallet.wallet_uuid}"
    response = requests.get(url)
    if response.status_code == 200:
        return Decimal(response.json()["balance"])
    else:
        print(f"Failed to get balance: {response.status_code} - {response.text}")
        return None

@events.test_stop.add_listener
def final_check_balance(environment, **kwargs):
    if TestWallet.check_final_balance:
        time.sleep(5)
        actual_balance = get_balance()
        expected_balance = TestWallet.redis_client.get_balance(TestWallet.wallet_uuid)
        if actual_balance is not None:
            if actual_balance == expected_balance:
                print(f"Balance confirmed! Balance: {actual_balance}")
            else:
                print(f"Balance not confirmed! Expected: {expected_balance}, Actual balance: {actual_balance}")

@events.test_stop.add_listener
def clear(environment, **kwargs):
    TestWallet.wallet_uuid = None
    environment.stats.reset_all()
    environment.runner.stats.total.reset()
    environment.runner.stats.clear_all()


