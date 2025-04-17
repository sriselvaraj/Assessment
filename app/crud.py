from sqlalchemy.orm import Session
from app import models, schemas
from fastapi import FastAPI, Request, HTTPException
from sqlalchemy import text

def create_claim(db: Session, claim: schemas.ClaimCreate) -> models.Claim:
    """ When this API is invoked, the net fees can be calculated and can be
        passed to payments service. if the kafka send succeeds, then commit the
        changes, else do not commit the changes. This way the data will be revoked
        or error message added in the table for this claim.
        If kafka send succeeds, the changes will be committed.

        pseudocode:
        step 1: calculate net fees
        step 2: create kafka payload with id (unique identifier), netfee and any other required parameters.
        step 3: publish the data to a topic which payments service will be subscribed to (claim_input).
        step 4: if the kafka send succeeds, the changes will be committed.
        step 5: If the kafka send failed or any other error, error can be returned and data not written into database.

        payments service:
        step 1: Subscribe to the topic claim_input with kafka.
        step 2: When the data is received, process the payload.
        step 3: if there are any errors, error code can be written into the database for the appropriate claim.
    """
    db_claim = models.Claim(**claim.dict())
    """ Please add data validation for *“submitted procedure”* and *“Provider NPI”* columns. *“Submitted procedure”* always begins with the letter ‘D’ and *“Provider NPI”* is always a 10 digit number. """
    if not db_claim.submittedprocedure.startswith("D"):
        raise HTTPException(status_code=400, detail="Invalid submitted procedure")
    if len(str(db_claim.providernpi)) != 10:
        raise HTTPException(status_code=400, detail="Invalid provider NPI")
    """**claim_process** computes the *“net fee”* as a result per the formula"""
    db_claim.netfee = db_claim.providerfees + db_claim.membercoinsurance + db_claim.membercopay - db_claim.allowedfees
    if db_claim.netfee < 0:
        raise HTTPException(status_code=400, detail="Calculated net fee is negative")
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)
    return db_claim

def get_provider_npis_sorted_by_netfees(db: Session):
    """ The endpoint should be optimized for performance """
    # The claims table is indexed with netfee column so order by netfee will not have performance impact
    return db.query(models.Claim) \
             .order_by(models.Claim.netfee.desc()) \
             .limit(10) \
             .all()

