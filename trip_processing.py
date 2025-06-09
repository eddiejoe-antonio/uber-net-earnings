import pandas as pd

# Load CSV
file_path = "driver_week_sample.csv"
df_all = pd.read_csv(file_path)

# Ensure column names are stripped of whitespace
df_all.columns = df_all.columns.str.strip()

# Normalize vehicle data (one row per vehicle per driver-week)
vehicle_cols = [
    ('vehicle_1_mmy', 'vehicle_1_mileage_share'),
    ('vehicle_2_mmy', 'vehicle_2_mileage_share'),
    ('vehicle_3_mmy', 'vehicle_3_mileage_share')
]

rows = []

for idx, row in df_all.iterrows():
    for mmy_col, share_col in vehicle_cols:
        vehicle_mmy = row.get(mmy_col)
        vehicle_share = row.get(share_col)

        if pd.notnull(vehicle_mmy):
            rows.append({
                'hashed_driver_uuid': row['hashed_driver_uuid'],
                'weekstr': row['weekstr'],
                'city_id': row['city_id'],
                'city_name': row['city_name'],
                'organic_earnings': row['organic_earnings'],
                'promos': row['promos'],
                'tip': row['tip'],
                'hours_open_trimmed': row['hours_open_trimmed'],
                'hours_active': row['hours_active'],
                'miles_open_trimmed': row['miles_open_trimmed'],
                'miles_active': row['miles_active'],
                'vehicle_mmy': vehicle_mmy.strip(),
                'vehicle_mileage_share': vehicle_share
            })

# Convert to DataFrame
df = pd.DataFrame(rows)

# Parse MMY fields
df[['make', 'model', 'year', 'engine', 'ownership']] = (
    df['vehicle_mmy'].str.split('|', expand=True).apply(lambda x: x.str.strip())
)
df['year'] = pd.to_numeric(df['year'], errors='coerce')

# Create total fields
df['total_earnings'] = df['organic_earnings'] + df['promos'] + df['tip']
df['total_miles'] = df['miles_open_trimmed'] + df['miles_active']
df['total_hours'] = df['hours_open_trimmed'] + df['hours_active']

# Group by city_name and calculate averages
columns_to_average = [
    "total_earnings", "organic_earnings", "promos", "tip",
    "total_miles", "miles_open_trimmed", "miles_active",
    "total_hours", "hours_open_trimmed", "hours_active"
]

avg_by_city = (
    df.groupby("city_name")[columns_to_average]
    .mean()
    .reset_index()
)

print("\n=== Averages by City ===")
print(avg_by_city.head())
avg_by_city.to_csv("averages_by_city.csv", index=False)

# Group by city_name and engine
avg_by_engine = (
    df.groupby(['city_name', 'engine'])[['total_earnings', 'total_miles', 'total_hours']]
    .mean()
    .reset_index()
    .sort_values(by=['city_name', 'engine'])
)

print("\n=== Averages by City and Engine ===")
print(avg_by_engine.head())
avg_by_engine.to_csv("averages_by_city_and_engine.csv", index=False)

# Group by city_name and ownership
avg_by_ownership = (
    df.groupby(['city_name', 'ownership'])[['total_earnings', 'total_miles', 'total_hours']]
    .mean()
    .reset_index()
    .sort_values(by=['city_name', 'ownership'])
)

print("\n=== Averages by City and Ownership ===")
print(avg_by_ownership.head())
avg_by_ownership.to_csv("averages_by_city_and_ownership.csv", index=False)

# Filter rows where total_hours > 30 and group by city_name
df_filtered = df[df['total_hours'] > 30]

avg_by_city_over_30hrs = (
    df_filtered.groupby("city_name")[['total_earnings', 'total_miles', 'total_hours']]
    .mean()
    .reset_index()
    .sort_values(by='city_name')
)

print("\n=== Averages by City (Only Total Hours > 30) ===")
print(avg_by_city_over_30hrs.head())
avg_by_city_over_30hrs.to_csv("averages_by_city_over_30_hours.csv", index=False)
