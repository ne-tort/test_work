# test_work
Здравствуйте, проект включает в себя:
 - FastAPI+Sqlalchemy, PostgreSQL, LiquiBase, PgBouncer

>>Тесты реализованы pytest, нагрузочное тестирование проводилось с помощью locust
>> - stress-test-locust.py

>> Для удобства тестирования добавлен api для создания тестового счета:
>> - http://localhost:8000/api/v1/wallets/new_wallet/{balance}
