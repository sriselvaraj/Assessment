import io
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal, ROUND_DOWN
from app.main import app, get_db
from app.database import Base
from app.models import Claim

# ✅ Connect to PostgreSQL test DB
TEST_DATABASE_URL = "postgresql://postgres:password@localhost:5432/crud"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Override FastAPI DB dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# ✅ Setup/teardown for each test
@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    #Base.metadata.drop_all(bind=engine)

def test_create_item():
    input_json = {
      "service date": "2025-04-17T11:30:00",
      "Submitted Procedure": "D1110",
      "quadrant": "UR",
      "plan/Group #": "GRP-1000",
      "subscriber #": "3730189502",
      "provider Npi": 1234567890,
      "provider Fees": 120.50,
      "allowed Fees": 8.00,
      "member CoInsurance": 20.00,
      "member Copay": 10.00
    }
    print(input_json)
    res = client.post("/claim/add", json=input_json)
    assert res.status_code == 200
    assert res.json()["subscriber #"] == "3730189502"

def test_top_ten_provider_npis():
    input_json = {
      "service date": "2025-04-17T11:30:00",
      "Submitted Procedure": "D1110",
      "quadrant": "UR",
      "plan/Group #": "GRP-1000",
      "subscriber #": "3730189502",
      "provider Npi": 1234567890,
      "provider Fees": 100.00,
      "allowed Fees": 8.00,
      "member CoInsurance": 20.00,
      "member Copay": 10.00
    }
    fees = 100
    for i in range(20):
        input_json["provider Fees"] = fees
        res = client.post("/claim/add", json=input_json)
        assert res.status_code == 200
        decimal_fees = Decimal(str(fees))
        assert Decimal(res.json()["provider fees"]) == decimal_fees.quantize(Decimal('0.00'), rounding=ROUND_DOWN)
        fees = fees + 1
    get = client.get(f"/top10netfees")
    assert get.status_code == 200
    assert len(get.json()) == 10
    expected_value = 141
    for i in range(10):
        decimal_fees = Decimal(str(expected_value))
        assert Decimal(get.json()[i]["netfee"]) == decimal_fees.quantize(Decimal('0.00'), rounding=ROUND_DOWN)
        expected_value = expected_value - 1

def test_top_rate_limited_provider_npis():
    for i in range(20):
        get = client.get(f"/top10netfees")
        if i >= 9:
            assert get.status_code == 429
        else:
            assert get.status_code == 200
