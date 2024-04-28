from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://geek_test_owner:TfQWm9S7IXPk@ep-floral-credit-a2ev3h8l.eu-central-1.aws.neon.tech/geek_test?sslmode=require"

# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:123123Kal@127.0.0.1/geek_test"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()