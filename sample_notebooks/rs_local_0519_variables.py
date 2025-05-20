# %%
from resinkit.resinkit import Resinkit
rs = Resinkit(
    sql_gateway_url="http://localhost:8083",
)

rs.show_vars_ui(base_url="http://localhost:8602")

# %%
