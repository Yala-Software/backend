from typing import Dict, Optional
from core.exchange.interface import ExchangeAPIInterface
from core.exchange.api1_adapter import ExchangeRateAPI
from core.exchange.api2_adapter import CurrencyConverterAPI

class ExchangeService:
    """Singleton service for currency exchange rates"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ExchangeService, cls).__new__(cls)
            cls._instance._primary_api = ExchangeRateAPI()
            cls._instance._fallback_api = CurrencyConverterAPI()
            cls._instance._current_api = cls._instance._primary_api
        return cls._instance
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """Get exchange rate using the current API with fallback"""
        try:
            return self._current_api.get_exchange_rate(from_currency, to_currency)
        except Exception:
            old_api = self._current_api
            self._current_api = self._fallback_api if self._current_api == self._primary_api else self._primary_api
            try:
                return self._current_api.get_exchange_rate(from_currency, to_currency)
            except Exception:
                self._current_api = old_api
                raise ValueError(f"Could not get exchange rate from {from_currency} to {to_currency} from any API")
    
    def switch_api(self) -> None:
        """Switch between primary and fallback API"""
        self._current_api = self._fallback_api if self._current_api == self._primary_api else self._primary_api
    
    def get_api_name(self) -> str:
        """Get the name of the current API being used"""
        return self._current_api.__class__.__name__
    
    def get_supported_currencies(self) -> Dict[str, str]:
        """Get list of supported currencies"""
        return self._current_api.get_supported_currencies()
