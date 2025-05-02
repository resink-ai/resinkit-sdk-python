
#%%
import nest_asyncio
from flink_gateway_api import Client
import logging

from resinkit.flink_session import FlinkSession

# Configure the root logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logging.getLogger("httpcore.http11").setLevel(logging.INFO)
logging.getLogger('httpcore.connection').setLevel(logging.INFO)

nest_asyncio.apply()  # Allow nested event loops
fg_client = Client(base_url="http://localhost:8083", raise_on_unexpected_status=True)

sql_t0 = '''
SELECT * FROM (
    VALUES
        (23, 'Alice Liddell', CAST('2024-12-29 10:30:00' AS TIMESTAMP)),
        (19, 'Bob Smith', CAST('2024-12-28 11:45:00' AS TIMESTAMP)),
        (27, 'Charlie Brown', CAST('2024-12-27 14:15:00' AS TIMESTAMP)),
        (31, 'David Jones', CAST('2024-12-26 16:20:00' AS TIMESTAMP))
) AS t(age, name, created_at);
'''
#%%
with FlinkSession(fg_client) as session:
    with session.execute(sql_t0).sync() as operation:
        df = operation.fetch().sync()

#%% 
with FlinkSession(fg_client) as session:
    with session.execute('SET;').sync() as operation:
        df_vars = operation.fetch().sync()
