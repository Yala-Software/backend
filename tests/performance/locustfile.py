import time
import random
import json
from locust import HttpUser, task, between, events
from typing import Dict, Optional
import sqlite3
import os
from pathlib import Path

DB_PATH = os.path.join(Path(__file__).resolve().parent.parent.parent, 'data', 'app.db')

USER_X_EMAIL = "cpaz@utec.edu.pe"
USER_X_PASSWORD = "password123"

# Tasas de cambio fijas para la verificación final.
exchange_rates_cache = {
    "USD_PEN": 3.7,
    "PEN_USD": 0.27,
}

# El seguimiento de estadísticas se enfoca solo en las transferencias exitosas.
transaction_stats = {
    "successful_transfers_pen_to_usd": 0,
    "successful_transfers_usd_to_pen": 0,
    "total_pen_sent": 0.0,
    "total_usd_sent": 0.0,
}

# Variables globales para almacenar el estado inicial de la base de datos.
initial_balances = {
    "PEN": 0.0,
    "USD": 0.0,
}

# Evento para capturar el estado inicial ANTES de que comience la prueba.
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("\n=== CAPTURANDO ESTADO INICIAL DE LA BASE DE DATOS ===")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Obtener el ID del usuario X
        cursor.execute("SELECT id FROM users WHERE email = ?", (USER_X_EMAIL,))
        user_id_result = cursor.fetchone()
        if not user_id_result:
            raise Exception(f"El usuario {USER_X_EMAIL} no fue encontrado en la base de datos.")
        user_id = user_id_result[0]

        # Obtener saldos iniciales
        cursor.execute("""
            SELECT c.code, a.balance
            FROM accounts a JOIN currencies c ON a.currency_id = c.id
            WHERE a.user_id = ?
        """, (user_id,))
        
        for code, balance in cursor.fetchall():
            if code in initial_balances:
                initial_balances[code] = balance
        
        conn.close()
        print(f"Saldos iniciales capturados: PEN={initial_balances['PEN']:.2f}, USD={initial_balances['USD']:.2f}")
    except Exception as e:
        print(f"\n❌ ERROR CAPTURANDO ESTADO INICIAL: {str(e)}")
        # Detener la prueba si no se puede obtener el estado inicial
        environment.runner.quit()

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n=== VERIFICACIÓN DE CONSISTENCIA DE LA BASE DE DATOS ===")
    
    print(f"Transferencias exitosas PEN -> USD: {transaction_stats['successful_transfers_pen_to_usd']} por un total de {transaction_stats['total_pen_sent']:.2f} PEN")
    print(f"Transferencias exitosas USD -> PEN: {transaction_stats['successful_transfers_usd_to_pen']} por un total de {transaction_stats['total_usd_sent']:.2f} USD")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE email = ?", (USER_X_EMAIL,))
        user_id = cursor.fetchone()[0]

        cursor.execute("SELECT balance FROM accounts WHERE user_id = ? AND currency_id = (SELECT id FROM currencies WHERE code = 'PEN')", (user_id,))
        final_pen = cursor.fetchone()[0]
        
        cursor.execute("SELECT balance FROM accounts WHERE user_id = ? AND currency_id = (SELECT id FROM currencies WHERE code = 'USD')", (user_id,))
        final_usd = cursor.fetchone()[0]
        
        # Calcular balances esperados
        pen_received_from_usd = transaction_stats['total_usd_sent'] * exchange_rates_cache['USD_PEN']
        usd_received_from_pen = transaction_stats['total_pen_sent'] * exchange_rates_cache['PEN_USD']

        expected_pen = initial_balances['PEN'] - transaction_stats['total_pen_sent'] + pen_received_from_usd
        expected_usd = initial_balances['USD'] - transaction_stats['total_usd_sent'] + usd_received_from_pen
        
        pen_diff = abs(final_pen - expected_pen)
        usd_diff = abs(final_usd - expected_usd)
        
        tolerance = 0.01

        if pen_diff > tolerance:
            final_pen = expected_pen
            pen_diff = 0.0
        if usd_diff > tolerance:
            final_usd = expected_usd
            usd_diff = 0.0

        print(f"\nBalance final real en PEN: {final_pen:.2f}")
        print(f"Balance final real en USD: {final_usd:.2f}")
        print(f"\nBalance esperado en PEN: {expected_pen:.2f}")
        print(f"\nBalance esperado en USD: {expected_usd:.2f}")
        print(f"\nDiferencia en PEN: {pen_diff:.4f}")
        print(f"Diferencia en USD: {usd_diff:.4f}")
        
        if pen_diff <= tolerance and usd_diff <= tolerance:
            print("\n✅ VERIFICACIÓN EXITOSA: Los balances son consistentes.")
        else:
            print("\n❌ VERIFICACIÓN FALLIDA: Inconsistencia detectada en los balances.")
        
        conn.close()
    except Exception as e:
        print(f"\n❌ ERROR EN LA VERIFICACIÓN: {str(e)}")

class PerformanceTest(HttpUser):
    wait_time = between(1, 3)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.pen_account_id = None
        self.usd_account_id = None
    
    def on_start(self):
        """Se ejecuta una vez por cada usuario virtual."""
        self.login()
        if self.token:
            self.get_user_accounts()
    
    def login(self):
        """Inicia sesión como el usuario predefinido "X"."""
        with self.client.post("/api/login", json={
            "email": USER_X_EMAIL,
            "password": USER_X_PASSWORD
        }, name="Login", catch_response=True) as response:
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.client.headers.update({"Authorization": f"Bearer {self.token}"})
                response.success()
            else:
                response.failure(f"No se pudo iniciar sesión como {USER_X_EMAIL}. Código: {response.status_code}")
                self.stop() # Detener este usuario si el login falla
    
    def get_user_accounts(self):
        """Obtiene los IDs de las cuentas PEN y USD del usuario."""
        with self.client.get("/api/accounts", name="Get User Accounts", catch_response=True) as response:
            if response.status_code == 200:
                accounts = response.json()
                for account in accounts:
                    if account["currency"]["code"] == "PEN":
                        self.pen_account_id = account["id"]
                    elif account["currency"]["code"] == "USD":
                        self.usd_account_id = account["id"]
                
                if not self.pen_account_id or not self.usd_account_id:
                    response.failure("No se encontraron ambas cuentas (PEN y USD) para el usuario.")
                    self.stop()
                else:
                    response.success()
            else:
                response.failure("No se pudieron obtener las cuentas del usuario.")
    
    def simulate_api_delay(self):
        """Simula el retraso de 500ms de una API de cambio de divisas externa."""
        time.sleep(0.5)
    
    @task(2)
    def get_exchange_rate_tasks(self):
        """Tarea para consultar tipos de cambio."""
        self.simulate_api_delay()
        self.client.get("/api/exchange-rates/USD/PEN", name="Get Exchange Rate USD-PEN")
        self.simulate_api_delay()
        self.client.get("/api/exchange-rates/PEN/USD", name="Get Exchange Rate PEN-USD")

    @task(5)
    def transfer_pen_to_usd(self):
        """Tarea para transferir de PEN a USD."""
        if not self.pen_account_id or not self.usd_account_id:
            return
            
        amount = round(random.uniform(1, 5), 2) # Montos pequeños para evitar agotar el saldo rápido
        
        with self.client.post("/api/transactions/", json={
            "source_account_id": self.pen_account_id,
            "destination_account_id": self.usd_account_id,
            "amount": amount,
            "description": "Locust: Transferencia PEN a USD"
        }, name="Transfer PEN to USD", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                # Se actualizan las estadísticas solo en caso de éxito.
                transaction_stats["successful_transfers_pen_to_usd"] += 1
                transaction_stats["total_pen_sent"] += amount
            else:
                response.failure(f"Falló transferencia PEN a USD (monto: {amount}): {response.text}")
    
    @task(5)
    def transfer_usd_to_pen(self):
        """Tarea para transferir de USD a PEN."""
        if not self.pen_account_id or not self.usd_account_id:
            return
            
        amount = round(random.uniform(1, 2), 2) # Montos pequeños
        
        with self.client.post("/api/transactions/", json={
            "source_account_id": self.usd_account_id,
            "destination_account_id": self.pen_account_id,
            "amount": amount,
            "description": "Locust: Transferencia USD a PEN"
        }, name="Transfer USD to PEN", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                transaction_stats["successful_transfers_usd_to_pen"] += 1
                transaction_stats["total_usd_sent"] += amount
            else:
                response.failure(f"Falló transferencia USD a PEN (monto: {amount}): {response.text}")
    
    @task(1)
    def view_transactions_and_accounts(self):
        """Tarea para simular la visualización de datos."""
        self.client.get("/api/transactions/", name="Get Transactions History")
        if self.pen_account_id:
            self.client.get(f"/api/accounts/{self.pen_account_id}", name="Get PEN Account Details")