# utils/charts.py
import matplotlib.pyplot as plt
import io

def generate_price_chart(prices: list, title: str) -> io.BytesIO:
    plt.figure(figsize=(10, 4))
    plt.plot(prices, color='green')
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Price")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf
