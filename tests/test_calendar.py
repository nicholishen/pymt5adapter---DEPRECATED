from .context import pymt5adapter as mt5
from pymt5adapter.calendar import calendar_events, Importance, Currency
import pymt5adapter.calendar as cal
from datetime import datetime, timedelta
import pytest


def test_calendar_events():
    from time import perf_counter
    f = datetime.now()
    t = f + timedelta(days=30)
    t1 = perf_counter()
    events = calendar_events(time_from=f, time_to=t, importance=Importance.HIGH)
    t1 = perf_counter() - t1
    t2 = perf_counter()
    events = calendar_events(time_from=f, time_to=t, importance=Importance.HIGH)
    t2 = perf_counter() - t2
    assert t2 * 1000 < t1 # verify cache speed
    assert type(events) is list
    assert len(events) > 0
    for e in events:
        etime = e['release_date']
        assert f <= etime <= t
        assert e['importance'].upper() not in ['MEDIUM', 'LOW', 'HOLIDAY']


def test_construct_args():
    test_args = dict(time_to=timedelta(days=-30), round_minutes=15)
    res_args = cal._construct_args(**test_args)
    assert isinstance(res_args['datetime_to'], datetime)
    assert isinstance(res_args['datetime_from'], datetime)
    assert isinstance(res_args['importance'], int)
    assert isinstance(res_args['currencies'], int)
    t = test_args['time_to'] = datetime(2020, 1, 1)
    test_args['time_from'] = t + timedelta(weeks=1)
    res_args = cal._construct_args(**test_args)
    assert res_args['datetime_from'] < res_args['datetime_to']


def test_camel_to_snake():
    controls = {
        'Url'         : 'url',
        'EventName'   : 'event_name',
        'CamelCaseKey': 'camel_case_key',
        'ok_id'       : 'ok_id',
        'NItems'      : 'n_items'
    }
    for k, v in controls.items():
        assert cal._camel_to_snake(k) == v


def test_normalize_time():
    control_minutes = 15
    control_time = datetime(2020, 1, 1, 1, control_minutes)
    delta = timedelta(minutes=7)
    test_time = control_time - delta
    result = cal._time_ceil(test_time, minutes=control_minutes)
    assert result == control_time
    test_time = control_time + delta
    result = cal._time_floor(test_time, minutes=control_minutes)
    assert result == control_time


def test_split_pairs():
    control = set('EUR USD AUD'.split())

    def clean(res):
        return set(map(str.upper, res))

    result = clean(cal._split_pairs(['eurusd', 'audusd', 'eur', 'aud', 'usd']))
    assert result == control


def test_make_flags():
    control_currency = Currency.USD | Currency.EUR | Currency.AUD
    control_importance = Importance.HOLIDAY | Importance.LOW
    test_currency = cal._make_flag(Currency, control_currency)
    assert test_currency == control_currency
    test_currency = cal._make_flag(Currency, 'eur aud usd')
    assert test_currency == control_currency
    test_currency = cal._make_flag(Currency, 'eur, aud, usd')
    assert test_currency == control_currency
    test_currency = cal._make_flag(Currency, ('eurusd', 'audusd'))
    assert test_currency == control_currency
    test_currency = cal._make_flag(Currency, ('eur', 'usd', 'aud'))
    assert test_currency == control_currency
    test_currency = cal._make_flag(Currency, 'eurusd, audusd, usdjpy')
    assert test_currency != control_currency
    test_importance = cal._make_flag(Importance, 'low, holiday')
    assert test_importance == control_importance


if __name__ == '__main__':
    pass
