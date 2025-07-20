import time
from typing import Dict, Optional
from config import SUPPORTED_CURRENCIES

class ExchangeServiceMock:
    """Versión mockup del servicio de Exchange para pruebas de rendimiento"""
    _instance = None
    
    # Tasas de cambio fijas para las pruebas
    _exchange_rates = {
        "USD_PEN": 3.7,
        "PEN_USD": 0.27,
        "EUR_USD": 1.1,
        "USD_EUR": 0.91,
        "EUR_PEN": 4.07,
        "PEN_EUR": 0.245,
        "GBP_USD": 1.25,
        "USD_GBP": 0.8,
        "GBP_PEN": 4.63,
        "PEN_GBP": 0.216
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ExchangeServiceMock, cls).__new__(cls)
        return cls._instance
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """Obtener tipo de cambio con un delay simulado de 500ms"""
        # Simular delay de 500ms
        time.sleep(0.5)
        
        # Verificar si las monedas son iguales
        if from_currency == to_currency:
            return 1.0
        
        # Buscar la tasa de cambio directa
        key = f"{from_currency}_{to_currency}"
        if key in self._exchange_rates:
            return self._exchange_rates[key]
        
        # Si no existe directa, intentamos el reverso
        reverse_key = f"{to_currency}_{from_currency}"
        if reverse_key in self._exchange_rates:
            return 1 / self._exchange_rates[reverse_key]
        
        # Si ninguna está disponible, calculamos a través de USD
        try:
            from_to_usd = self.get_exchange_rate(from_currency, "USD")
            usd_to_target = self.get_exchange_rate("USD", to_currency)
            return from_to_usd * usd_to_target
        except:
            raise ValueError(f"No se pudo obtener el tipo de cambio de {from_currency} a {to_currency}")
    
    def get_supported_currencies(self) -> Dict[str, str]:
        """Obtener la lista de divisas soportadas"""
        return SUPPORTED_CURRENCIES 