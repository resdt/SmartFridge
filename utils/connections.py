import re
import asyncpg
import asyncio


DB_LINK = "postgresql://smartfridgedb_owner:kRe0Hf1josyS@ep-young-dust-a5pvzx3t.us-east-2.aws.neon.tech/smartfridgedb?sslmode=require"
PARAMETER_LIST = re.split(r"[:/\@\?]+", DB_LINK)
DB_PARAMS = {"user": PARAMETER_LIST[1],
             "password": PARAMETER_LIST[2],
             "host": PARAMETER_LIST[3],
             "database": PARAMETER_LIST[4],
             "port": "5432"}


async def async_execute_query(query, *parameters):
    connection = await asyncpg.connect(**DB_PARAMS)
    try:
        results = await connection.fetch(query, *parameters)
        return [dict(row) for row in results]
    except Exception as e:
        print(e)
        return None
    finally:
        await connection.close()


def execute_query(query, *parameters):
    result = asyncio.run(async_execute_query(query, *parameters))
    return result
