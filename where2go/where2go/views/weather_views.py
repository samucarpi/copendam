import requests
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
import json


def get_next_friday():
    """Calcola la data del prossimo venerdì"""
    today = datetime.now()
    days_until_friday = (4 - today.weekday()) % 7  # 4 = Friday (0=Monday)
    if days_until_friday == 0 and today.hour >= 23:  # Se è venerdì sera tardi, prendi il prossimo
        days_until_friday = 7
    if days_until_friday == 0:  # Se è venerdì ma ancora presto
        return today
    return today + timedelta(days=days_until_friday)


def get_weather_description(weather_code):
    """
    Converte i codici meteo di Open-Meteo in descrizioni italiane
    https://open-meteo.com/en/docs
    """
    weather_descriptions = {
        0: "Cielo sereno",
        1: "Prevalentemente sereno",
        2: "Parzialmente nuvoloso", 
        3: "Nuvoloso",
        45: "Nebbia",
        48: "Nebbia ghiacciata",
        51: "Pioviggine leggera",
        53: "Pioviggine moderata",
        55: "Pioviggine intensa",
        56: "Pioviggine ghiacciata leggera",
        57: "Pioviggine ghiacciata intensa",
        61: "Pioggia leggera",
        63: "Pioggia moderata",
        65: "Pioggia intensa",
        66: "Pioggia ghiacciata leggera",
        67: "Pioggia ghiacciata intensa",
        71: "Neve leggera",
        73: "Neve moderata",
        75: "Neve intensa",
        77: "Granuli di neve",
        80: "Rovesci leggeri",
        81: "Rovesci moderati",
        82: "Rovesci intensi",
        85: "Rovesci di neve leggeri",
        86: "Rovesci di neve intensi",
        95: "Temporale",
        96: "Temporale con grandine leggera",
        99: "Temporale con grandine intensa"
    }
    return weather_descriptions.get(weather_code, "Condizioni sconosciute")


def get_weather_icon(weather_code, is_day=True):
    """
    Converte i codici meteo di Open-Meteo in icone OpenWeatherMap compatibili
    """
    # Mappatura semplificata per icone meteo
    day_icons = {
        0: "01d",  # Sereno
        1: "02d",  # Prevalentemente sereno
        2: "03d",  # Parzialmente nuvoloso
        3: "04d",  # Nuvoloso
        45: "50d", # Nebbia
        48: "50d", # Nebbia ghiacciata
        51: "09d", # Pioviggine leggera
        53: "09d", # Pioviggine moderata
        55: "09d", # Pioviggine intensa
        61: "10d", # Pioggia leggera
        63: "10d", # Pioggia moderata
        65: "10d", # Pioggia intensa
        71: "13d", # Neve leggera
        73: "13d", # Neve moderata
        75: "13d", # Neve intensa
        80: "09d", # Rovesci
        81: "09d", # Rovesci moderati
        82: "09d", # Rovesci intensi
        95: "11d", # Temporale
    }
    
    night_icons = {
        0: "01n",  # Sereno
        1: "02n",  # Prevalentemente sereno
        2: "03n",  # Parzialmente nuvoloso
        3: "04n",  # Nuvoloso
        45: "50n", # Nebbia
        48: "50n", # Nebbia ghiacciata
        51: "09n", # Pioviggine leggera
        53: "09n", # Pioviggine moderata
        55: "09n", # Pioviggine intensa
        61: "10n", # Pioggia leggera
        63: "10n", # Pioggia moderata
        65: "10n", # Pioggia intensa
        71: "13n", # Neve leggera
        73: "13n", # Neve moderata
        75: "13n", # Neve intensa
        80: "09n", # Rovesci
        81: "09n", # Rovesci moderati
        82: "09n", # Rovesci intensi
        95: "11n", # Temporale
    }
    
    icons = day_icons if is_day else night_icons
    return icons.get(weather_code, "01d" if is_day else "01n")


@login_required
def get_weather_data(request):
    """
    Recupera i dati meteo per venerdì alle ore specificate (21:00, 22:00, 23:00)
    Utilizza Open-Meteo API per Reggio Emilia
    """
    if request.method == 'GET':
        try:
            # Coordinate di Reggio Emilia
            LAT = 44.6983
            LON = 10.6312
            
            # Calcola il prossimo venerdì
            next_friday = get_next_friday()
            friday_date = next_friday.strftime('%Y-%m-%d')
            
            # URL Open-Meteo API
            BASE_URL = "https://api.open-meteo.com/v1/forecast"
            
            # Parametri per la richiesta API
            params = {
                'latitude': LAT,
                'longitude': LON,
                'hourly': 'temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m,apparent_temperature',
                'start_date': friday_date,
                'end_date': friday_date,
                'timezone': 'Europe/Rome'
            }
            
            # Chiamata API
            response = requests.get(BASE_URL, params=params, timeout=10)
            
            if response.status_code != 200:
                return JsonResponse({
                    'success': False,
                    'error': f'API Error: {response.status_code}'
                })
            
            data = response.json()
            
            # Estrai i dati orari
            hourly_data = data.get('hourly', {})
            times = hourly_data.get('time', [])
            temperatures = hourly_data.get('temperature_2m', [])
            weather_codes = hourly_data.get('weather_code', [])
            humidities = hourly_data.get('relative_humidity_2m', [])
            wind_speeds = hourly_data.get('wind_speed_10m', [])
            apparent_temps = hourly_data.get('apparent_temperature', [])
            
            # Ore di interesse (21:00, 22:00, 23:00 del venerdì)
            target_hours = [21, 22, 23]
            
            forecasts = []
            daily_temps = temperatures  # Tutte le temperature del venerdì per min/max
            
            # Processa ogni ora del giorno
            for i, time_str in enumerate(times):
                dt = datetime.fromisoformat(time_str)
                hour = dt.hour
                
                # Controlla se è una delle ore di interesse
                if hour in target_hours:
                    # Determina se è giorno o notte per l'icona
                    is_day = 6 <= hour <= 18
                    
                    forecast_data = {
                        'datetime': time_str,
                        'hour': f"{hour:02d}:00",
                        'temperature': round(temperatures[i]) if i < len(temperatures) else 0,
                        'feels_like': round(apparent_temps[i]) if i < len(apparent_temps) else 0,
                        'description': get_weather_description(weather_codes[i] if i < len(weather_codes) else 0),
                        'icon': get_weather_icon(weather_codes[i] if i < len(weather_codes) else 0, is_day),
                        'humidity': round(humidities[i]) if i < len(humidities) else 0,
                        'wind_speed': round(wind_speeds[i], 1) if i < len(wind_speeds) else 0.0
                    }
                    forecasts.append(forecast_data)
            
            # Ordina per ora
            forecasts.sort(key=lambda x: x['hour'])
            
            # Calcola temperatura min/max del venerdì
            if daily_temps:
                min_temp = round(min(daily_temps))
                max_temp = round(max(daily_temps))
            else:
                min_temp = max_temp = None
            
            weather_data = {
                'success': True,
                'date': friday_date,
                'day_name': 'Venerdì',
                'min_temp': min_temp,
                'max_temp': max_temp,
                'forecasts': forecasts,
                'city': 'Reggio Emilia'
            }
            
            return JsonResponse(weather_data)
            
        except requests.exceptions.RequestException as e:
            return JsonResponse({
                'success': False,
                'error': f'Network error: {str(e)}'
            })
        except KeyError as e:
            return JsonResponse({
                'success': False,
                'error': f'Data parsing error: {str(e)}'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Metodo non consentito'})