from fastapi import FastAPI, Depends, Request, File, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import SessionLocal, engine, Base
from starlette.middleware.base import BaseHTTPMiddleware
import json
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

Base.metadata.create_all(bind=engine)


class LowercaseJSONMiddleware(BaseHTTPMiddleware):
    """ Note that the names are not consistent in capitalization. Converting all the names to lower case"""
    async def dispatch(self, request: Request, call_next):
        # Read the incoming request body
        body = await request.body()

        try:
            # Convert the body to a dictionary if it's a valid JSON
            json_data = json.loads(body)
            # Convert all keys to lowercase
            lowercase_data = {key.lower(): value for key, value in json_data.items()}
            # Re-encode the modified data into JSON format
            body = json.dumps(lowercase_data).encode('utf-8')
            print(body)
        except json.JSONDecodeError:
            # If body is not a valid JSON, skip modification
            pass

        # Create a new Request object with the modified body
        request._body = body

        # Continue the request-response cycle
        response = await call_next(request)
        return response
app = FastAPI()
app.add_middleware(LowercaseJSONMiddleware)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/claim/add", response_model=schemas.Claim)
def create_claim(claim: schemas.ClaimCreate, db: Session = Depends(get_db)):
    """**claim_process** transforms a JSON payload representing a single claim input with multiple lines and stores it into a RDB."""
    print(claim)
    return crud.create_claim(db=db, claim=claim)

@app.get("/top10netfees/", response_model=list[schemas.Claim])
@limiter.limit("10/minute")
def get_top_10_provider_npis(request: Request, db: Session = Depends(get_db)):
    """Implement an endpoint that returns the top 10 provider_npis by net fees generated."""
    """It would be good to have a rate limiter to this api probably 10 req/min."""
    return crud.get_provider_npis_sorted_by_netfees(db)
