from sqlalchemy import Column, Integer, String, DateTime, func, BigInteger, Numeric
from app.database import Base

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)  #  **claim_process** generates a unique id per claim.
    serviceDate = Column(DateTime(timezone=True), server_default=func.now())
    submittedprocedure = Column(String)
    quadrant = Column(String)
    plangroup = Column(String)
    subscriber = Column(String)
    providernpi = Column(BigInteger)
    providerfees = Column(Numeric(10, 2))
    allowedfees = Column(Numeric(10, 2))
    membercoinsurance = Column(Numeric(10, 2))
    membercopay = Column(Numeric(10, 2))
    netfee = Column(Numeric(10, 2), index=True) # Indexing will help to sort the table based on netfee
