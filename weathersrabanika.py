import requests
import smtplib
import sqlite3
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import matplotlib.pyplot as plt

# Configuration
API_KEY = "d5ca0ed8e5dd2f8f84410b0eef3f0837"
CITIES = ["Delhi", "Mumbai", "Chennai", "Bangalore", "Kolkata", "Hyderabad"]
INTERVAL = 300  # seconds (5 minutes)
TEMP_THRESHOLD = 35  # Celsius
ALERT_EMAIL = "dassrabanika@gmail.com"
DATABASE = "weather_data.db"

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('weather_data.db')
cursor = conn.cursor()

# # Create a table for weather data
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS weather (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     date TEXT NOT NULL,
#     temperature REAL,
#     humidity REAL,
#     wind_speed REAL,
#     conditions TEXT
# )
# ''')
cursor.execute("""
CREATE TABLE IF NOT EXISTS Weather (
    city TEXT,
    temp REAL,
    feels_like REAL,
    condition TEXT,
    timestamp INTEGER
)""")


# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and table created successfully!")

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()


def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "city": city,
            "temp": data["main"]["temp"] - 273.15,  # Convert Kelvin to Celsius
            "feels_like": data["main"]["feels_like"] - 273.15,
            "condition": data["weather"][0]["main"],
            "timestamp": data["dt"]
        }
    else:
        print(f"Failed to get data for {city}")
        return None


def fetch_data_for_all_cities():
    weather_data = []
    for city in CITIES:
        data = get_weather_data(city)
        if data:
            weather_data.append(data)
    return weather_data


def store_data(data):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Weather (
        city TEXT,
        temp REAL,
        feels_like REAL,
        condition TEXT,
        timestamp INTEGER
    )""")
    for entry in data:
        cursor.execute("""
        INSERT INTO Weather (city, temp, feels_like, condition, timestamp)
        VALUES (?, ?, ?, ?, ?)""",
                       (entry["city"], entry["temp"], entry["feels_like"], entry["condition"], entry["timestamp"]))
    conn.commit()


def calculate_daily_summary():
    cursor.execute("""
    SELECT city, 
           AVG(temp) as avg_temp, 
           MAX(temp) as max_temp, 
           MIN(temp) as min_temp, 
           condition 
    FROM Weather 
    WHERE DATE(timestamp, 'unixepoch') = DATE('now')
    GROUP BY city
    """)
    summary = cursor.fetchall()
    for row in summary:
        print(f"City: {row[0]}, Avg Temp: {row[1]}, Max Temp: {row[2]}, Min Temp: {row[3]}, Condition: {row[4]}")
    return summary


def check_thresholds(data):
    alerts = []
    for entry in data:
        if entry["temp"] > TEMP_THRESHOLD:
            alerts.append(entry)
    if alerts:
        trigger_alert(alerts)


def trigger_alert(alerts):
    print("Alert! Temperature Threshold Breached")
    send_email(alerts)


def send_email(alerts):
    # Simple Email Alert (replace with your SMTP server details)
    msg = MIMEMultipart()
    msg['From'] = 'weather-alert@example.com'
    msg['To'] = ALERT_EMAIL
    msg['Subject'] = 'Weather Alert'
    body = "The following cities have breached the temperature threshold:\n"
    for alert in alerts:
        body += f"{alert['city']} - {alert['temp']}C\n"
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('dassrabanika@gmail.com', 'jLvKHQ82d_q.cwQ')
    text = msg.as_string()
    server.sendmail('weather-alert@gmail.com', ALERT_EMAIL, text)
    server.quit()


def run_weather_monitoring():
    weather_data = fetch_data_for_all_cities()
    if weather_data:
        store_data(weather_data)
        calculate_daily_summary()
        check_thresholds(weather_data)


def visualize_data():

    # def run_weather_monitoring():
    #     while True:
    #         weather_data = fetch_data_for_all_cities()
    #         if weather_data:
    #             store_data(weather_data)
    #             calculate_daily_summary()
    #             check_thresholds(weather_data)
    #         time.sleep(INTERVAL)

    run_weather_monitoring()

    cursor.execute("""
    SELECT city, AVG(temp) as avg_temp FROM Weather 
    WHERE DATE(timestamp, 'unixepoch') = DATE('now') 
    GROUP BY city
    """)
    data = cursor.fetchall()
    cities = [x[0] for x in data]
    temps = [x[1] for x in data]

    plt.bar(cities, temps)
    plt.xlabel('Cities')
    plt.ylabel('Average Temperature (C)')
    plt.title('Daily Average Temperature')
    plt.show()


def test_temperature_conversion():
    kelvin = 300
    celsius = kelvin - 273.15
    assert round(celsius, 2) == 26.85, "Conversion Error"


def test_alert_threshold():
    sample_data = [
        {"city": "Delhi", "temp": 36, "feels_like": 38, "condition": "Clear", "timestamp": int(time.time())}
    ]
    check_thresholds(sample_data)
    # Expect alert to be triggered.


if __name__ == "__main__":
    visualize_data()
    test_temperature_conversion()
    test_alert_threshold()