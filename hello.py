import preswald as pw
from preswald import text, plotly, connect, get_df, checkbox, selectbox
import pandas as pd
import plotly.express as px

# -------------------------------------------
# Load data and prepare it
# -------------------------------------------
connect()
df = get_df('sample_csv')
df["Round"] = pd.to_numeric(df["Round"], errors="coerce")

# Get latest info per driver (in case of multiple rows)
latest_driver_info = df.sort_values(by=["DriverID", "Round"]).drop_duplicates(subset=["Code"], keep="last")

# Dynamically build driver metadata
driver_info = {}
for _, row in latest_driver_info.iterrows():
    code = row["Code"]
    driver_info[code] = {
        "name": f"{row['GivenName']} {row['FamilyName']}",
        "team": row["ConstructorName"],
        "img": f"driver_headshots/{code}.png"
    }

# -------------------------------------------
# Select driver and show info
# -------------------------------------------
text("# F1 2024 Driver's Standings)

selected_code = selectbox(
    label="Choose a Driver",
    options=list(driver_info.keys()),
    default="VER"
)

# Filter dataset for the selected driver
driver_df = df[df["Code"] == selected_code]

# Compute stats
total_points = driver_df["Points"].sum()
avg_position = driver_df["Position"].mean()
races = driver_df["Round"].nunique()
avg_grid = driver_df["Grid"].mean()
fastest_lap = driver_df["FastestLapTime"].min()

# Display headshot and stats
info = driver_info[selected_code]

text(f"""
## {info['name']}

**Team:** {info['team']}  
**Total Points:** {total_points:.0f}  
**Average Finish Position:** {avg_position:.2f}  
**Races Participated:** {races}  
**Average Starting Grid:** {avg_grid:.2f}  
**Best Fastest Lap Time:** {fastest_lap}
""")
# -------------------------------------------
# Driver's Championship Line Chart
# -------------------------------------------
text("# F1 2024 Driver's Championship")

df = df.sort_values(by=["DriverID", "Round"])
df["CumulativePoints"] = df.groupby("DriverID")["Points"].cumsum()

fig = px.line(
    df,
    x="Round",
    y="CumulativePoints",
    color="DriverID",
    markers=True,
    title="Cumulative Points Per Round",
    labels={"Round": "Race Round", "CumulativePoints": "Cumulative Points"}
)
plotly(fig)

# -------------------------------------------
# Constructor's Championship
# -------------------------------------------
text("# F1 2024 Constructor's Championship")

points_by_driver = df.groupby(["ConstructorName", "DriverID"])["Points"].sum().reset_index()

# Sort constructors by total points
total_points = points_by_driver.groupby("ConstructorName")["Points"].sum().reset_index()
total_points = total_points.sort_values("Points", ascending=True)

# Preserve sort order
points_by_driver["ConstructorName"] = pd.Categorical(
    points_by_driver["ConstructorName"],
    categories=total_points["ConstructorName"],
    ordered=True
)
points_by_driver = points_by_driver.sort_values("ConstructorName")

# Bar chart
fig = px.bar(
    points_by_driver,
    y="ConstructorName",
    x="Points",
    color="DriverID",
    orientation="h",
    title="Total Constructor Points (Stacked by Driver)",
    labels={"Points": "Total Points", "ConstructorName": "Constructor"}
)
fig.update_layout(
    barmode="stack",
    showlegend=False,
    yaxis_title="",
    xaxis_title="Points",
    plot_bgcolor="white"
)
plotly(fig)
