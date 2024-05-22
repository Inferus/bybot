def calculate_pump_percent(ticker_before, ticker_now):
    return (float(ticker_now["openInterest"]) / float(ticker_before["openInterest"]) * 100) - 100

