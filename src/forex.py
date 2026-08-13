import requests
import webbrowser
import time
import subprocess



def open_forex_charts():

    urls = [
        "https://www.tradingview.com/chart/?symbol=FX:EURUSD",
        "https://www.tradingview.com/chart/?symbol=TVC:GOLD"
    ]

    for url in urls:
        subprocess.Popen(
            ["C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
             "--new-window",
             url]
        )


def convert_aed_to_php(amount):

    url = "https://open.er-api.com/v6/latest/USD"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    aedphp_rate = (
        data["rates"]["PHP"] / data["rates"]["AED"]
    )

    converted_amount = round(amount * aedphp_rate, 2)

    return (
        f"{amount:g} UAE dirhams is approximately "
        f"{converted_amount:,.2f} Philippine pesos."
    )


def convert_php_to_aed(amount):
    """Convert Philippine pesos to UAE dirhams using the live USD cross-rate."""

    url = "https://open.er-api.com/v6/latest/USD"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    phpaed_rate = data["rates"]["AED"] / data["rates"]["PHP"]
    converted_amount = round(amount * phpaed_rate, 2)
    return (
        f"{amount:g} Philippine pesos is approximately "
        f"{converted_amount:,.2f} UAE dirhams."
    )




def get_forex():

    url = "https://open.er-api.com/v6/latest/USD"

    response = requests.get(url)

    data = response.json()

    eurusd = round(1 / data["rates"]["EUR"], 4)

    gbpusd = round(1 / data["rates"]["GBP"], 4)

    usdjpy = round(data["rates"]["JPY"], 2)

    aedphp = round(
        data["rates"]["PHP"] / data["rates"]["AED"],
        2
    )

    phpaed = round(
        data["rates"]["AED"] / data["rates"]["PHP"] * 100,
        2
    )

    return (
        f"Forex briefing. "
        f"Euro dollar is trading near {eurusd}. "
        f"Pound dollar is trading near {gbpusd}. "
        f"Dollar yen is trading near {usdjpy}. "
        f"One UAE dirham equals approximately {aedphp} Philippine pesos. "
      
    )


if __name__ == "__main__":
    open(get_forex())
