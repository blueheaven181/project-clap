import psutil


def get_system_health():

    cpu = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory().percent

    disk = psutil.disk_usage("/").percent

    
    report = (
        f"Regarding system health. "
        f"CPU utilization is {cpu:.1f} percent. "
        f"Memory utilization is {memory:.1f} percent. "
        f"Disk utilization is {disk:.1f} percent. "
    )

    if cpu > 90:
        report += " Warning. CPU utilization is high."

    if memory > 90:
        report += " Warning. Memory utilization is high."

    if disk > 90:
        report += " Warning. Disk utilization is high."

    return report



if __name__ == "__main__":
    print(get_system_health())