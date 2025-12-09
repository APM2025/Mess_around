
import sys
import os
sys.path.append(os.getcwd())
from src.database import get_session
from src.models import Vaccine

session = get_session()
vaccines = session.query(Vaccine).all()
print("Vaccines in DB:")
for v in vaccines:
    print(f"'{v.vaccine_code}'")
