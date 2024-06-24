import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def import_data():
    engine = create_engine(DATABASE_URL)
    df = pd.read_csv('students.csv')
    df.to_sql("students", con=engine, if_exists="replace",index=False)

if __name__ == "__main__":
    import_data()
