#dtype 변환
def change_datatype(df):
  df["ts"] = pd.to_datetime(df["ts"], utc=True)
  df["status"] = df["status"].astype(int)
  df["time"] = df["time"].astype(int)

# Action 분리
def classify_action(uri):
    if uri.startswith("/api/notices"):
        return "Notice"
    if uri.startswith("/api/short-notices"):
        return "ShortNotice"
    if uri.startswith("/api/booth"):
        return "Booth"
    if uri.startswith("/api/food-truck"):
        return "FoodTruck"
    if uri.startswith("/api/stamp"):
        return "Stamp"
    if uri.startswith("/api/auth"):
        return "Auth"
    if uri == "/":
        return "Home"
    return "Other"
