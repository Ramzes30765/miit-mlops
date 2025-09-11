import requests
import matplotlib.pyplot as plt
import pandas as pd

url = "https://api.open-meteo.com/v1/forecast"
params = {"latitude": 55.75, "longitude": 37.61, "hourly": "temperature_2m"}

response = requests.get(url, params=params)
data = response.json()

hours = data["hourly"]["time"][:24]
temps = data["hourly"]["temperature_2m"][:24]

df = pd.DataFrame({"time": pd.to_datetime(hours), "temperature_c": temps})
df = df.sort_values("time").reset_index(drop=True)
df.to_csv("temperature_24h.csv", index=False)
print("Сохранено в temperature_24h.csv")

plt.plot(hours, temps, marker="o")
plt.xticks(rotation=45)
plt.title("Температура в Москве (24 часа)")
plt.xlabel("Время")
plt.ylabel("°C")
plt.tight_layout()
plt.show()
