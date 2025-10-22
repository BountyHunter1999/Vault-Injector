from pydantic import BaseModel, Field


class DBData(BaseModel):
    username: str = Field(..., description="The username")
    password: str = Field(..., description="The password")
    host: str = Field(..., description="The host")
    port: int = Field(..., description="The port")
    database: str = Field(..., description="The database")
    sslmode: str = Field(..., description="The SSL mode")

class DBTypeSecret(BaseModel):
    secret_path: str = Field(..., description="The path to the secret")
    db_engine: str = Field(..., description="The database engine")
    secret_data: DBData = Field(..., description="The data of the secret")
