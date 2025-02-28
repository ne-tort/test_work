from pydantic import BaseModel, condecimal
from typing import Literal
from uuid import UUID

class WalletPostRequest(BaseModel):
    operation: Literal["DEPOSIT", "WITHDRAW"]
    amount: condecimal(gt=0, decimal_places=2)

class WalletPostResponse(BaseModel):
    wallet_uuid: UUID
    operation: Literal["DEPOSIT", "WITHDRAW"]
    amount: condecimal(gt=0, decimal_places=2)

class WalletGetResponse(BaseModel):
    wallet_uuid: UUID
    balance: condecimal(gt=0, decimal_places=2)