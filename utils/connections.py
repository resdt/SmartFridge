import re
import psycopg2
from psycopg2.extras import DictCursor


DB_LINK = "postgresql://smartfridgedb_owner:kRe0Hf1josyS@ep-young-dust-a5pvzx3t.us-east-2.aws.neon.tech/smartfridgedb?sslmode=require"
PARAMETER_LIST = re.split(r"[:/\@\?]+", DB_LINK)
DB_PARAMS = {"user": PARAMETER_LIST[1],
             "password": PARAMETER_LIST[2],
             "host": PARAMETER_LIST[3],
             "database": PARAMETER_LIST[4],
             "port": "5432"}


def execute_query(query, *parameters):
    try:
        connection = psycopg2.connect(**DB_PARAMS)
        cursor = connection.cursor(cursor_factory=DictCursor)
        cursor.execute(query, parameters)

        if query.strip().lower().startswith("select"):
            results = cursor.fetchall()
            return [dict(row) for row in results]
        else:
            connection.commit()
            return None
    except Exception as e:
        print(e)
        return None
    finally:
        if "connection" in locals() and connection:
            connection.close()
