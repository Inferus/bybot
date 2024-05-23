def calculate_pump_percent(ticker_before, ticker_now):
    if ticker_before["openInterest"] == 0:
        ticker_before["openInterest"] = 0.00000001
    return (float(ticker_now["openInterest"]) / float(ticker_before["openInterest"]) * 100) - 100

