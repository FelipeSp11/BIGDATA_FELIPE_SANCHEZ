import requests
import sqlite3
import os

class Ingestion:
    def __init__(self):
        self.db_path = "src/static/db/database.sqlite"
        self._asegurar_directorio()
        self._crear_tabla()
    
    def _asegurar_directorio(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _crear_tabla(self):
        conexion = sqlite3.connect(self.db_path)
        cursor = conexion.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS datos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                moneda TEXT,
                metodo TEXT,
                high REAL,
                low REAL,
                vol REAL,
                last REAL,
                buy REAL,
                sell REAL,
                open REAL,
                date INTEGER,
                pair TEXT
            )
        ''')
        conexion.commit()
        conexion.close()
    
    def obtener_datos_api(self, url=""):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            print(error)
            return {}
    
    def guardar_db(self, datos=[]):
        if not isinstance(datos, list) or len(datos) == 0:
            print("Datos inválidos o vacíos")
            return
        
        conexion = sqlite3.connect(self.db_path)
        cursor = conexion.cursor()
        
        for ticker in datos:
            cursor.execute("""
                INSERT INTO datos (moneda, metodo, high, low, vol, last, buy, sell, open, date, pair) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticker.get("moneda", ""), ticker.get("metodo", ""),
                float(ticker.get("high", 0)), float(ticker.get("low", 0)), float(ticker.get("vol", 0)),
                float(ticker.get("last", 0)), float(ticker.get("buy", 0)), float(ticker.get("sell", 0)),
                float(ticker.get("open", 0)), int(ticker.get("date", 0)), ticker.get("pair", "")
            ))
        
        conexion.commit()
        conexion.close()
        print("Datos guardados en la base de datos con éxito")


ingestion = Ingestion()
url = "https://api.coinlore.net/api/tickers/"
datos = ingestion.obtener_datos_api(url=url)

if "data" in datos:
    registros = [
        {
            "moneda": item.get("symbol", ""),
            "metodo": "ticker",
            "high": item.get("high", 0),
            "low": item.get("low", 0),
            "vol": item.get("volume24", 0),
            "last": item.get("price_usd", 0),
            "buy": item.get("price_btc", 0),
            "sell": item.get("price_btc", 0),
            "open": item.get("price_usd", 0),
            "date": item.get("ts", 0),
            "pair": f"USD{item.get('symbol', '')}"
        }
        for item in datos["data"]
    ]
    
    ingestion.guardar_db(datos=registros)
else:
    print("No se obtuvo la consulta")