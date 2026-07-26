import pygetwindow as gw
import time


def arrange_workspace():

    
    eurusd_windows = gw.getWindowsWithTitle("EURUSD")

  
    gold_windows = gw.getWindowsWithTitle("GOLD")

   
   

    if not eurusd_windows:
        print("EURUSD window not found")
        return

    if not gold_windows:
        print("GOLD window not found")
        return

    eurusd = eurusd_windows[0]
    gold = gold_windows[0]

    eurusd.restore()
    gold.restore()

    time.sleep(1)

    eurusd.moveTo(-2560, 0)
    eurusd.resizeTo(2560, 1440)

    gold.moveTo(0, 0)
    gold.resizeTo(2560, 1440)


if __name__ == "__main__":
    arrange_workspace()