# %%
import nest_asyncio
from resinkit.resinkit import Resinkit
import logging

from flink_gateway_api.api.default import (
    get_info,
)
from flink_gateway_api.models import (
    GetInfoResponseBody,
)

# Configure the root logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
nest_asyncio.apply()  # Allow nested event loops
# https://resink.ai/resinkit/03055414_T6nlGb6sDWQ/flinkui/#/overview
RESINKIT_SESSION = "eyJhbGciOiJSUzI1NiIsImtpZCI6InJQV1pUZyJ9.eyJpc3MiOiJodHRwczovL3Nlc3Npb24uZmlyZWJhc2UuZ29vZ2xlLmNvbS9yZXNpbmstYWkiLCJuYW1lIjoiU2hpamluZyBMdSIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NJU2diWGpJZGNITjltNHVuRGV6UUEtU1p5SWMyQTZIU0pGZm9HdkdkX3ZNMUdpUGN0NVx1MDAzZHM5Ni1jIiwiYXVkIjoicmVzaW5rLWFpIiwiYXV0aF90aW1lIjoxNzQ2MTYzMjcxLCJ1c2VyX2lkIjoiRkpGZVFyQzJod1V4ZmZ6eTRRY2drZEtlTkg0MyIsInN1YiI6IkZKRmVRckMyaHdVeGZmenk0UWNna2RLZU5INDMiLCJpYXQiOjE3NDYyNTY1NTksImV4cCI6MTc0NzQ2NjE1OSwiZW1haWwiOiJzaGlqaW5nLmx2QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7Imdvb2dsZS5jb20iOlsiMTAyMjExMzM2NjA3ODM1MTQxMDM1Il0sImVtYWlsIjpbInNoaWppbmcubHZAZ21haWwuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoiZ29vZ2xlLmNvbSJ9fQ.l7kxocrVJVxQ2QHyVVnppHZ6EMkK3XfaCmN2jMfaPWqCLzoF7kQ9Eiimz_o42MHGwsNY4jHV2xf7JZGIaiEKixw9VIvdIzz92bpC1QsSrAjkcV-PxGMUunma7Oi_4yOVt0SOMWj1QfYQbZv0OHSEgHDjOVZ3-YOpWv_c83nShtxzXj6RMgopRVZX1I1oSt8AJMcssyHYp4svcb6_s85dTe1DDwQJA6lYfODSL5yiCRGSD4q607WfglYtRWirIadKzq62p4pNg_ZANTTYrxf3XXf2-PVQ6WKA3bytZ6UIKKPYk8kNd2S9LyzsRdLN-qPGMbwRECwRckZ7Ghs6J3PCZw"
rk = Resinkit(
    url="https://resink.ai/resinkit/03055414_T6nlGb6sDWQ/api/flink_sql_gateway",
    resinkit_session=RESINKIT_SESSION,
    personal_access_token="pat_cnk8_",
)

info: GetInfoResponseBody = get_info.sync(client=rk.flink_gateway_client)
print(info)
# %%
# sql_t0 = """
# SELECT * FROM (
#     VALUES
#         (23, 'Alice Liddell', CAST('2024-12-29 10:30:00' AS TIMESTAMP)),
#         (19, 'Bob Smith', CAST('2024-12-28 11:45:00' AS TIMESTAMP)),
#         (27, 'Charlie Brown', CAST('2024-12-27 14:15:00' AS TIMESTAMP)),
#         (31, 'David Jones', CAST('2024-12-26 16:20:00' AS TIMESTAMP))
# ) AS t(age, name, created_at);
# """
# # %%
# with rk.create_session("test_session") as session:
#     with session.execute(sql_t0).sync() as operation:
#         df = operation.fetch().sync()

# # %%
# with rk.create_session("test_session") as session:
#     with session.execute("SET;").sync() as operation:
#         df_vars = operation.fetch().sync()
