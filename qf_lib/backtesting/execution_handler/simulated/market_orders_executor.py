import math
from typing import Dict, List, Sequence

from qf_lib.backtesting.contract_to_ticker_conversion.base import ContractTickerMapper
from qf_lib.backtesting.data_handler.data_handler import DataHandler
from qf_lib.backtesting.execution_handler.simulated.commission_models.commission_model import CommissionModel
from qf_lib.backtesting.execution_handler.simulated.simulated_executor import SimulatedExecutor
from qf_lib.backtesting.execution_handler.simulated.slippage.base import Slippage
from qf_lib.backtesting.monitoring.abstract_monitor import AbstractMonitor
from qf_lib.backtesting.order.order import Order
from qf_lib.backtesting.portfolio.portfolio import Portfolio
from qf_lib.common.utils.dateutils.timer import Timer


class MarketOrdersExecutor(SimulatedExecutor):
    def __init__(self, contracts_to_tickers_mapper: ContractTickerMapper, data_handler: DataHandler,
                 monitor: AbstractMonitor, portfolio: Portfolio, timer: Timer, order_id_generator,
                 commission_model: CommissionModel, slippage_model: Slippage):

        super().__init__(contracts_to_tickers_mapper, data_handler, monitor, portfolio, timer,
                         order_id_generator, commission_model, slippage_model)

    def accept_orders(self, orders: Sequence[Order]) -> List[int]:
        order_id_list = []
        for order in orders:
            order.id = next(self._order_id_generator)

            order_id_list.append(order.id)
            self._awaiting_orders[order.id] = order

        return order_id_list

    def _get_orders_with_fill_prices_without_slippage(self, market_orders_list, tickers):
        unique_tickers = list(set(tickers))
        current_prices_series = self._data_handler.get_current_price(unique_tickers)

        unexecuted_orders_dict = {}  # type: Dict[int, Order]
        to_be_executed_orders = []
        no_slippage_prices = []

        for order, ticker in zip(market_orders_list, tickers):
            security_price = current_prices_series[ticker]

            if security_price is None or math.isnan(security_price):
                unexecuted_orders_dict[order.id] = order
            else:
                to_be_executed_orders.append(order)
                no_slippage_prices.append(security_price)

        return no_slippage_prices, to_be_executed_orders, unexecuted_orders_dict

