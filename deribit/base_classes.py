from dataclasses import dataclass
from pydantic import BaseModel


@dataclass
class RobotSettings(BaseModel):
    gap: float
    gap_ignore: float


@dataclass(frozen=True)
class Credentials(BaseModel):
    client_id: str
    client_secret: str
    client_url: str


@dataclass
class MysqlDB:
    db_user: str
    db_password: str
    db_name: str
    db_table: str
    db_host: str
    db_port: int


@dataclass(frozen=True)
class Settings(BaseModel):
    robot: RobotSettings
    credentials: Credentials
    db: MysqlDB


@dataclass
class Order:
    id: str
    type: str
    run: bool
    price: float
    amount: float
