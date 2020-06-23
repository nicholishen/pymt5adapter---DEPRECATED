from . import const
from .context import _ContextAwareBase
from .core import copy_rates_from_pos
from .core import symbol_info
from .core import symbol_info_tick
from .core import symbol_select
from .types import SymbolInfo
from .types import Union


class Symbol(_ContextAwareBase):
    def __init__(self, symbol: Union[str, SymbolInfo]):
        super().__init__()
        self.name = symbol

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, symbol):
        try:
            self._name = symbol.name
            self._info = symbol
        except AttributeError:
            self._name = symbol
            self._info = None
        self._refresh()

    @property
    def select(self):
        return self._select

    @select.setter
    def select(self, enable: bool):
        x = symbol_select(self._name, enable)
        self._select = enable if x else not enable

    @property
    def tick(self):
        return self._tick

    @property
    def spread(self):
        return int(round(self.spread_float / self.trade_tick_size))

    @property
    def bid(self):
        return self.tick.bid

    @property
    def ask(self):
        return self.tick.ask

    @property
    def volume(self):
        return self.tick.volume

    def _daily(self, key):
        rate = copy_rates_from_pos(self.name, const.TIMEFRAME.D1, 0, 1)
        try:
            return rate[0][key]
        except:
            return 0

    @property
    def day_real_volume(self):
        return self._daily('real_volume')

    @property
    def day_volume(self):
        return self._daily('volume')

    @property
    def volume_real(self):
        return self.tick.volume_real

    def normalize_price(self, price: float):
        ts = self.trade_tick_size
        if ts != 0.0:
            return round(round(price / ts) * ts, self.digits)

    def tick_calc(self, price: float, num_ticks: int):
        """Calculate a new price by number of ticks from the price param. The result is normalized to the
        tick-size of the instrument.

        :param price: The price to add or subtract ticks from.
        :param num_ticks: number of ticks. If subtracting ticks then this should be a negative number.
        :return: A new price adjusted by the number of ticks and normalized to tick-size.
        """
        return self.normalize_price(price + num_ticks * self.trade_tick_size)

    def refresh_rates(self):
        self._tick = symbol_info_tick(self.name)
        return self

    def _refresh(self):
        info = self._info or symbol_info(self._name)
        self.refresh_rates()
        self._select = info.select
        # self.spread = info.spread
        # self.volume_real = info.volume_real
        self.custom = info.custom
        self.chart_mode = info.chart_mode
        self.visible = info.visible
        self.session_deals = info.session_deals
        self.session_buy_orders = info.session_buy_orders
        self.session_sell_orders = info.session_sell_orders
        # self.volume = info.volume
        self.volumehigh = info.volumehigh
        self.volumelow = info.volumelow
        self.digits = info.digits
        self.spread_float = info.spread_float
        self.ticks_bookdepth = info.ticks_bookdepth
        self.trade_calc_mode = info.trade_calc_mode
        self.trade_mode = info.trade_mode
        self.start_time = info.start_time
        self.expiration_time = info.expiration_time
        self.trade_stops_level = info.trade_stops_level
        self.trade_freeze_level = info.trade_freeze_level
        self.trade_exemode = info.trade_exemode
        self.swap_mode = info.swap_mode
        self.swap_rollover3days = info.swap_rollover3days
        self.margin_hedged_use_leg = info.margin_hedged_use_leg
        self.expiration_mode = info.expiration_mode
        self.filling_mode = info.filling_mode
        self.order_mode = info.order_mode
        self.order_gtc_mode = info.order_gtc_mode
        self.option_mode = info.option_mode
        self.option_right = info.option_right
        self.bidhigh = info.bidhigh
        self.bidlow = info.bidlow
        self.askhigh = info.askhigh
        self.asklow = info.asklow
        self.lasthigh = info.lasthigh
        self.lastlow = info.lastlow
        self.volumehigh_real = info.volumehigh_real
        self.volumelow_real = info.volumelow_real
        self.option_strike = info.option_strike
        self.point = info.point
        self.trade_tick_value = info.trade_tick_value
        self.trade_tick_value_profit = info.trade_tick_value_profit
        self.trade_tick_value_loss = info.trade_tick_value_loss
        self.trade_tick_size = info.trade_tick_size
        self.trade_contract_size = info.trade_contract_size
        self.trade_accrued_interest = info.trade_accrued_interest
        self.trade_face_value = info.trade_face_value
        self.trade_liquidity_rate = info.trade_liquidity_rate
        self.volume_min = info.volume_min
        self.volume_max = info.volume_max
        self.volume_step = info.volume_step
        self.volume_limit = info.volume_limit
        self.swap_long = info.swap_long
        self.swap_short = info.swap_short
        self.margin_initial = info.margin_initial
        self.margin_maintenance = info.margin_maintenance
        self.session_volume = info.session_volume
        self.session_turnover = info.session_turnover
        self.session_interest = info.session_interest
        self.session_buy_orders_volume = info.session_buy_orders_volume
        self.session_sell_orders_volume = info.session_sell_orders_volume
        self.session_open = info.session_open
        self.session_close = info.session_close
        self.session_aw = info.session_aw
        self.session_price_settlement = info.session_price_settlement
        self.session_price_limit_min = info.session_price_limit_min
        self.session_price_limit_max = info.session_price_limit_max
        self.margin_hedged = info.margin_hedged
        self.price_change = info.price_change
        self.price_volatility = info.price_volatility
        self.price_theoretical = info.price_theoretical
        self.price_greeks_delta = info.price_greeks_delta
        self.price_greeks_theta = info.price_greeks_theta
        self.price_greeks_gamma = info.price_greeks_gamma
        self.price_greeks_vega = info.price_greeks_vega
        self.price_greeks_rho = info.price_greeks_rho
        self.price_greeks_omega = info.price_greeks_omega
        self.price_sensitivity = info.price_sensitivity
        self.basis = info.basis
        self.category = info.category
        self.currency_base = info.currency_base
        self.currency_profit = info.currency_profit
        self.currency_margin = info.currency_margin
        self.bank = info.bank
        self.description = info.description
        self.exchange = info.exchange
        self.formula = info.formula
        self.isin = info.isin
        self.page = info.page
        self.path = info.path
        return self
