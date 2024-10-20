pip install matplotlib requests
API_KEY = "your_openweathermap_api_key"
CITIES = ["Delhi", "Mumbai", "Chennai", "Bangalore", "Kolkata", "Hyderabad"]
INTERVAL = 300  # 5 minutes
TEMP_THRESHOLD = 35  # Celsius
ALERT_EMAIL = "your_alert_email@example.com"
DATABASE = "weather_data.db"
python weather_monitoring.py
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your_email@example.com', 'your_email_password')
if __name__ == "__main__":
    visualize_data()
    test_temperature_conversion()
    test_alert_threshold()
