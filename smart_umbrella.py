# smart_umbrella.py
# Ask for a city or coordinates, fetch weather from OpenWeatherMap, and suggest umbrella.

import os
import sys
import requests

# ✅ FIXED: API key must be a string in quotes
API_KEY = "4ff1a925851f81de5952735418dc7997"
API_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_api_key():
    key = (API_KEY or os.getenv("OPENWEATHER_API_KEY", "")).strip()
    if not key:
        print("⚠️ Missing API key. Set API_KEY or env var OPENWEATHER_API_KEY.")
        sys.exit(1)
    return key

def call_api(params, api_key):
    try:
        r = requests.get(API_URL, params={**params, "appid": api_key, "units": "metric"}, timeout=10)
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {e}"}
    try:
        data = r.json()
    except ValueError:
        return {"error": "Invalid response from server (not JSON)."}
    if r.status_code != 200:
        msg = data.get("message", "Unknown error").capitalize()
        if r.status_code == 401:
            return {"error": f"Invalid API key (401): {msg}"}
        if r.status_code == 404:
            return {"error": f"Not found (404): {msg}"}
        return {"error": f"API error ({r.status_code}): {msg}"}
    return {"data": data}

def fetch_by_city(city, api_key):
    return call_api({"q": city}, api_key)

def fetch_by_coords(lat, lon, api_key):
    return call_api({"lat": lat, "lon": lon}, api_key)

def suggestion(condition):
    return "🌂 Carry an umbrella today!" if condition in {"Rain", "Drizzle", "Thunderstorm"} else "☀️ No umbrella needed — enjoy your day!"

def show_result(d):
    name = d.get("name", "Unknown")
    main = d.get("main", {})
    w0 = (d.get("weather") or [{}])[0]
    temp = main.get("temp")
    cond = w0.get("main", "N/A")
    desc = w0.get("description", "").capitalize()
    t_str = f"{temp:.1f}°C" if isinstance(temp, (int, float)) else "N/A"
    print("\n✅ Weather fetched successfully!\n")
    print(f"🏙️ City: {name}")
    print(f"🌡️ Temperature: {t_str}")
    print(f"☁️ Condition: {cond} ({desc})")
    print(f"\n💡 Suggestion: {suggestion(cond)}")

def parse_input(s):
    if "," in s:
        try:
            lat_s, lon_s = [x.strip() for x in s.split(",", 1)]
            return ("coords", float(lat_s), float(lon_s))
        except Exception:
            return ("error", "Invalid coordinates. Use format: lat,lon (e.g., 40.71,-74.01).")
    return ("city", s)

def main():
    print("=== Smart Umbrella Reminder ===")
    user_in = input("Enter your city name (or lat,lon): ").strip()
    if not user_in:
        print("⚠️ Input cannot be empty.")
        return
    mode = parse_input(user_in)
    if mode[0] == "error":
        print(f"❌ {mode[1]}")
        return
    api_key = get_api_key()
    result = fetch_by_coords(mode[1], mode[2], api_key) if mode[0] == "coords" else fetch_by_city(mode[1], api_key)
    if "error" in result:
        print(f"❌ {result['error']}")
        return
    show_result(result["data"])

if __name__ == "__main__":
    main()
