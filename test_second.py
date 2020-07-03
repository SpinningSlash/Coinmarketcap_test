import requests
from datetime import datetime
from datetime import timedelta
from time import sleep, time
import sys
from multiprocessing import Pool
import numpy as np
import pytest


def max_volume_tickers(number_of_tickers):
    """Func collects data for `n` first tickers with max volume within 24h"""
    num_of_tries = 5
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': 1,
        'limit': number_of_tickers,
        'sort': 'market_cap'}

    headers = {
        'Accepts': 'application/json',
        'Accept - Encoding': 'deflate, gzip',
        'X-CMC_PRO_API_KEY': '5ad05081-2ce4-437d-b715-3db5681b6dd3',
    }
    for req in range(num_of_tries):
        try:
            response = requests.get(url, headers=headers, params=parameters, timeout=0.5)
            break
        except requests.exceptions.Timeout:
            print('Request timeout, retrying...')
            sleep(0.250)
            continue

    return response

def max_volume_tickers_test(test_number_of_tickers):
    response = max_volume_tickers(test_number_of_tickers)

    """Test response time"""
    response_time = response.elapsed.total_seconds() * 1000
    print('Response time is', round(response_time), 'ms')

    """Test size of package"""
    size_of_response = sys.getsizeof(response.content)
    # print('Size of package is', round(size_of_response / 1024, 2), 'bytes')

    """Test if data is up to date"""
    last_updated_list = []
    response_json = response.json()
    for record in response_json['data']:
        last_updated = datetime.strptime(record['last_updated'], '%Y-%m-%dT%H:%M:%S.%fZ')
        last_updated_list.append(last_updated)
    time_difference = (max(last_updated_list) - min(last_updated_list))
    # print('Time between oldest and newest price update for tickers is', time_differnce)

    assert response_time < 500
    assert size_of_response < 10240
    assert time_difference < timedelta(hours=24)
    return response_time

def parralel_max_volume_tickers_test(number_of_tests):
    """Test response time for parallel calls"""

    numbers_of_tickers = [10 for i in range(number_of_tests)]
    start_time = time()
    with Pool(number_of_tests) as p:
        list_response_times = p.map(max_volume_tickers_test, numbers_of_tickers)
    percentile_80 = np.percentile(list_response_times, 80)
    rps = number_of_tests/(time() - start_time)

    print('rps is', (round(rps, 2)))
    print('80 percentile of responses is', round(np.percentile(list_response_times, 80)))

    return percentile_80, rps

def test_main():
    """Main test"""
    if __name__ == '__main__':
        percentile_80, rps = parralel_max_volume_tickers_test(8)
        assert rps > 5
        assert percentile_80 < 450










