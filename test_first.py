import requests
from datetime import datetime
from datetime import timedelta
from time import sleep
import sys
import pytest

def max_volume_tickers(number_of_tickers):
    """Func collects data for `n` first tickers with max volume within 24h"""

    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    num_of_tries = 5
    parameters = {
        'start': 1,
        'limit': number_of_tickers,
        'sort': 'market_cap'
    }
    headers = {
        'Accepts': 'application/json',
        'Accept - Encoding': 'deflate, gzip',
        'X-CMC_PRO_API_KEY': '5ad05081-2ce4-437d-b715-3db5681b6dd3'
    }

    """Work around server lags"""
    for req in range(num_of_tries):
        try:
            response = requests.get(url, headers=headers, params=parameters, timeout=0.5)
            break
        except requests.exceptions.Timeout:
            print('Request timeout, retrying...')
            sleep(0.250)
            continue
    return response


def test_max_volume_tickers():
    response = max_volume_tickers(5)

    """Test response time"""
    response_time = response.elapsed.total_seconds() * 1000
    print('Response time is', round(response_time), 'ms')

    """Test size of package"""
    size_of_response = sys.getsizeof(response.content)
    print('Size of package is', round(size_of_response / 1024, 2), 'bytes')

    """Test if data is up to date"""
    last_updated_list = []
    for record in response.json()['data']:
        last_updated = datetime.strptime(record['last_updated'], '%Y-%m-%dT%H:%M:%S.%fZ')
        last_updated_list.append(last_updated)
    time_differnce = (max(last_updated_list) - min(last_updated_list))
    print('Time between oldest and newest price update for tickers is', time_differnce)

    assert response_time < 500
    assert size_of_response < 10240
    assert time_differnce < timedelta(hours=24)
