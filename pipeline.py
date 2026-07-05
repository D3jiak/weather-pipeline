import requests
import pandas as pd
from sqlalchemy import create_engine
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def fetch_weather(latitude, longitude):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,rain,wind_speed_10m"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        logging.info("Weather data fetched successfully")
        return response.json()
    except Exception as e:
        logging.error(f"Failed to fetch weather data: {e}")
        return None

def structure_data(data):
    try:
        row = {
            'time': data['current']['time'],
            'temperature_c': data['current']['temperature_2m'],
            'rain_mm': data['current']['rain'],
            'wind_kmh': data['current']['wind_speed_10m'],
            'location': 'Manchester'
        }
        logging.info("Data structured successfully")
        return pd.DataFrame([row])
    except Exception as e:
        logging.error(f"Failed to structure data: {e}")
        return None

def store_data(df, connection_string):
    try:
        engine = create_engine(connection_string)
        df.to_sql(
            name='weather_data',
            con=engine,
            if_exists='append',
            index=False
        )
        logging.info(f"Data stored successfully - {len(df)} row(s) written")
        return True
    except Exception as e:
        logging.error(f"Failed to store data: {e}")
        return False

def run_pipeline():
    logging.info("Pipeline started")
    
    connection_string = os.environ.get('DATABASE_URL')
    if not connection_string:
        logging.error("DATABASE_URL environment variable not set")
        return
    
    data = fetch_weather(53.4808, -2.2426)
    if data is None:
        logging.error("Pipeline failed at fetch stage")
        return
    
    df = structure_data(data)
    if df is None:
        logging.error("Pipeline failed at structure stage")
        return
    
    success = store_data(df, connection_string)
    if success:
        logging.info("Pipeline completed successfully")
    else:
        logging.error("Pipeline failed at store stage")

if __name__ == "__main__":
    run_pipeline()
