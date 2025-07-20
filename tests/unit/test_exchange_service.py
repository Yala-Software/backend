import pytest
from unittest.mock import patch, MagicMock
from services.exchange_service import ExchangeService
from config import SUPPORTED_CURRENCIES

def test_exchange_service_singleton():
    # Verificar que ExchangeService es un singleton
    service1 = ExchangeService()
    service2 = ExchangeService()
    
    assert service1 is service2

@patch('core.exchange.api1_adapter.ExchangeRateAPI.get_exchange_rate')
@patch('core.exchange.api2_adapter.CurrencyConverterAPI.get_exchange_rate')
def test_get_exchange_rate_primary_api_success(mock_api2_get_rate, mock_api1_get_rate):
    # Probar obtención de tasa con API primaria exitosa
    mock_api1_get_rate.return_value = 3.5
    
    service = ExchangeService()
    rate = service.get_exchange_rate("USD", "PEN")
    
    assert rate == 3.5
    mock_api1_get_rate.assert_called_once_with("USD", "PEN")
    mock_api2_get_rate.assert_not_called()

@patch('core.exchange.api1_adapter.ExchangeRateAPI.get_exchange_rate')
@patch('core.exchange.api2_adapter.CurrencyConverterAPI.get_exchange_rate')
def test_get_exchange_rate_primary_api_failure(mock_api2_get_rate, mock_api1_get_rate):
    # Probar fallo de API primaria y uso de API secundaria
    mock_api1_get_rate.side_effect = Exception("Error API 1")
    mock_api2_get_rate.return_value = 3.6
    
    service = ExchangeService()
    rate = service.get_exchange_rate("USD", "PEN")
    
    assert rate == 3.6
    mock_api1_get_rate.assert_called_once_with("USD", "PEN")
    mock_api2_get_rate.assert_called_once_with("USD", "PEN")

@patch('core.exchange.api1_adapter.ExchangeRateAPI.get_exchange_rate')
@patch('core.exchange.api2_adapter.CurrencyConverterAPI.get_exchange_rate')
def test_get_exchange_rate_both_apis_failure(mock_api2_get_rate, mock_api1_get_rate):
    # Probar fallo de ambas APIs
    mock_api1_get_rate.side_effect = Exception("Error API 1")
    mock_api2_get_rate.side_effect = Exception("Error API 2")
    
    service = ExchangeService()
    
    with pytest.raises(ValueError) as excinfo:
        service.get_exchange_rate("USD", "PEN")
    
    assert "Could not get exchange rate" in str(excinfo.value)
    mock_api1_get_rate.assert_called_once_with("USD", "PEN")
    mock_api2_get_rate.assert_called_once_with("USD", "PEN")

def test_switch_api():
    # Probar cambio entre APIs primaria y secundaria
    service = ExchangeService()
    primary_api_name = service.get_api_name()
    
    service.switch_api()
    switched_api_name = service.get_api_name()
    
    assert primary_api_name != switched_api_name
    
    service.switch_api()
    back_to_primary = service.get_api_name()
    
    assert back_to_primary == primary_api_name

def test_get_supported_currencies():
    # Probar obtención de monedas soportadas
    service = ExchangeService()
    currencies = service.get_supported_currencies()
    
    # Verificar formato
    assert isinstance(currencies, dict)
    assert len(currencies) > 0
    assert "USD" in currencies
    assert "PEN" in currencies 