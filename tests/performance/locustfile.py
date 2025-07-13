import time
import random
import json
from locust import HttpUser, task, between, events
from typing import Dict, Optional
import sqlite3
import os
from pathlib import Path

# Conexión a la base de datos para verificar la consistencia al final
TEST_DB_PATH = os.path.join(Path(__file__).resolve().parent.parent.parent, 'data', 'test_app.db')

# Datos para los tests
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "password123"
TEST_USER_FULLNAME = "Test User"
TEST_USER_USERNAME = "testuser"

# Cache para simular el comportamiento de la API de exchange (con delay de 500ms)
exchange_rates_cache = {
    "USD_PEN": 3.7,
    "PEN_USD": 0.27,
    "EUR_USD": 1.1,
    "USD_EUR": 0.91
}

# Variable global para almacenar el token de autenticación
auth_token = None

# Variable para realizar seguimiento de las operaciones para la verificación final
transaction_stats = {
    "deposits_pen": 0,
    "deposits_usd": 0,
    "transfers_pen_to_usd": 0,
    "transfers_usd_to_pen": 0,
    "deposit_amount_pen": 0,
    "deposit_amount_usd": 0,
    "transfer_amount_pen_to_usd": 0,
    "transfer_amount_usd_to_pen": 0
}

# Evento para verificar la consistencia al final de la prueba
@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n=== VERIFICACIÓN DE CONSISTENCIA DE LA BASE DE DATOS ===")
    
    # Mostrar estadísticas de transacciones
    print(f"Depósitos en PEN: {transaction_stats['deposits_pen']} por un total de {transaction_stats['deposit_amount_pen']}")
    print(f"Depósitos en USD: {transaction_stats['deposits_usd']} por un total de {transaction_stats['deposit_amount_usd']}")
    print(f"Transferencias de PEN a USD: {transaction_stats['transfers_pen_to_usd']} por un total de {transaction_stats['transfer_amount_pen_to_usd']}")
    print(f"Transferencias de USD a PEN: {transaction_stats['transfers_usd_to_pen']} por un total de {transaction_stats['transfer_amount_usd_to_pen']}")

    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()
        
        # Obtener el balance total en PEN y USD
        cursor.execute("SELECT SUM(balance) FROM accounts JOIN currencies ON accounts.currency_id = currencies.id WHERE currencies.code = 'PEN'")
        total_pen = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(balance) FROM accounts JOIN currencies ON accounts.currency_id = currencies.id WHERE currencies.code = 'USD'")
        total_usd = cursor.fetchone()[0]
        
        print(f"\nBalance total en PEN: {total_pen}")
        print(f"Balance total en USD: {total_usd}")
        
        # Verificar consistencia
        expected_pen = transaction_stats['deposit_amount_pen'] - transaction_stats['transfer_amount_pen_to_usd'] + transaction_stats['transfer_amount_usd_to_pen'] * exchange_rates_cache['USD_PEN']
        expected_usd = transaction_stats['deposit_amount_usd'] - transaction_stats['transfer_amount_usd_to_pen'] + transaction_stats['transfer_amount_pen_to_usd'] * exchange_rates_cache['PEN_USD']
        
        print(f"\nBalance esperado en PEN: {expected_pen}")
        print(f"Balance esperado en USD: {expected_usd}")
        
        pen_diff = abs(total_pen - expected_pen)
        usd_diff = abs(total_usd - expected_usd)
        
        print(f"\nDiferencia en PEN: {pen_diff}")
        print(f"Diferencia en USD: {usd_diff}")
        
        # Tolerancia debido a redondeos
        tolerance = 0.01
        if pen_diff <= tolerance and usd_diff <= tolerance:
            print("\n✅ VERIFICACIÓN EXITOSA: Los balances son consistentes")
        else:
            print("\n❌ VERIFICACIÓN FALLIDA: Los balances no son consistentes")
        
        conn.close()
    except Exception as e:
        print(f"\n❌ ERROR EN LA VERIFICACIÓN: {str(e)}")

class PerformanceTest(HttpUser):
    wait_time = between(1, 3)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.user_id = None
        self.pen_account_id = None
        self.usd_account_id = None
    
    def on_start(self):
        # Registrar un usuario o iniciar sesión
        self.register_or_login()
        
        # Obtener las cuentas del usuario
        self.get_user_accounts()
    
    def register_or_login(self):
        # Intentar iniciar sesión
        response = self.client.post("/api/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }, name="Login")
        
        if response.status_code != 200:
            # Si no se puede iniciar sesión, intentar registrar
            response = self.client.post("/api/register", json={
                "username": TEST_USER_USERNAME,
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_FULLNAME
            }, name="Register")
        
        # Guardar el token
        data = response.json()
        self.token = data["access_token"]
        
        # Configurar el token en los headers
        self.client.headers.update({"Authorization": f"Bearer {self.token}"})
        
        # Obtener el ID del usuario
        user_response = self.client.get("/api/users/me", name="Get User Profile")
        self.user_id = user_response.json()["id"]
    
    def get_user_accounts(self):
        # Obtener las cuentas del usuario
        response = self.client.get("/api/accounts", name="Get User Accounts")
        accounts = response.json()
        
        for account in accounts:
            if account["currency"]["code"] == "PEN":
                self.pen_account_id = account["id"]
            elif account["currency"]["code"] == "USD":
                self.usd_account_id = account["id"]
    
    def simulate_api_delay(self):
        # Simular el retraso de la API (500ms)
        time.sleep(0.5)
    
    @task(2)
    def get_exchange_rate_usd_pen(self):
        # Consultar tipo de cambio USD a PEN
        self.simulate_api_delay()
        with self.client.get("/api/exchange-rates/USD/PEN", name="Get Exchange Rate USD-PEN", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get exchange rate: {response.text}")
    
    @task(2)
    def get_exchange_rate_pen_usd(self):
        # Consultar tipo de cambio PEN a USD
        self.simulate_api_delay()
        with self.client.get("/api/exchange-rates/PEN/USD", name="Get Exchange Rate PEN-USD", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get exchange rate: {response.text}")
    
    @task(1)
    def get_supported_currencies(self):
        # Obtener monedas soportadas
        with self.client.get("/api/supported-currencies", name="Get Supported Currencies", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get currencies: {response.text}")
    
    @task(3)
    def make_deposit_pen(self):
        # Realizar un depósito en PEN (simulado como transferencia desde otra cuenta)
        if not self.pen_account_id:
            return
            
        amount = round(random.uniform(10, 100), 2)
        transaction_stats["deposits_pen"] += 1
        transaction_stats["deposit_amount_pen"] += amount
        
    
    @task(3)
    def make_deposit_usd(self):
        # Realizar un depósito en USD (simulado)
        if not self.usd_account_id:
            return
            
        amount = round(random.uniform(5, 50), 2)
        transaction_stats["deposits_usd"] += 1
        transaction_stats["deposit_amount_usd"] += amount
        
        # Simulación similar al depósito en PEN
    
    @task(5)
    def transfer_pen_to_usd(self):
        # Transferir de PEN a USD
        if not self.pen_account_id or not self.usd_account_id:
            return
            
        amount = round(random.uniform(5, 20), 2)
        
        # Verificamos que podemos hacer la transferencia (simplificado)
        if transaction_stats["deposit_amount_pen"] - transaction_stats["transfer_amount_pen_to_usd"] < amount:
            return
            
        transaction_stats["transfers_pen_to_usd"] += 1
        transaction_stats["transfer_amount_pen_to_usd"] += amount
        
        with self.client.post("/api/transactions/", json={
            "source_account_id": self.pen_account_id,
            "destination_account_id": self.usd_account_id,
            "amount": amount,
            "description": "Transferencia PEN a USD (test)"
        }, name="Transfer PEN to USD", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to transfer: {response.text}")
                transaction_stats["transfers_pen_to_usd"] -= 1
                transaction_stats["transfer_amount_pen_to_usd"] -= amount
    
    @task(5)
    def transfer_usd_to_pen(self):
        # Transferir de USD a PEN
        if not self.pen_account_id or not self.usd_account_id:
            return
            
        amount = round(random.uniform(2, 10), 2)
        
        # Verificamos que podemos hacer la transferencia (simplificado)
        if transaction_stats["deposit_amount_usd"] - transaction_stats["transfer_amount_usd_to_pen"] < amount:
            return
            
        transaction_stats["transfers_usd_to_pen"] += 1
        transaction_stats["transfer_amount_usd_to_pen"] += amount
        
        with self.client.post("/api/transactions/", json={
            "source_account_id": self.usd_account_id,
            "destination_account_id": self.pen_account_id,
            "amount": amount,
            "description": "Transferencia USD a PEN (test)"
        }, name="Transfer USD to PEN", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to transfer: {response.text}")
                transaction_stats["transfers_usd_to_pen"] -= 1
                transaction_stats["transfer_amount_usd_to_pen"] -= amount
    
    @task(1)
    def view_transactions(self):
        # Ver historial de transacciones
        with self.client.get("/api/transactions/", name="Get Transactions", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get transactions: {response.text}")
    
    @task(1)
    def view_account_details(self):
        # Ver detalles de cuenta
        if not self.pen_account_id:
            return
            
        with self.client.get(f"/api/accounts/{self.pen_account_id}", name="Get Account Details", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get account details: {response.text}") 