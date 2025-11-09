def calc_stop_loss(entry_price: float, atr: float, direction: str):
    if atr is None:
        return None
    if direction == 'BUY':
        return float(entry_price - 2*atr)
    elif direction == 'SELL':
        return float(entry_price + 2*atr)
    return None

def calc_take_profit(entry_price: float, wave1_size: float, direction: str):
    mult = 1.618
    if wave1_size is None:
        wave1_size = 0.0
    if direction == 'BUY':
        return float(entry_price + mult * wave1_size)
    elif direction == 'SELL':
        return float(entry_price - mult * wave1_size)
    return None
