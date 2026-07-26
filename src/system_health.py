import psutil


def get_system_health():

    cpu = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory().percent

    disk = psutil.disk_usage("/").percent

    return (
    f"CPU utilization is {cpu:.1f} percent. "
    f"Memory utilization is {memory:.1f} percent. "
    f"Disk utilization is {disk:.1f} percent."
    )


if __name__ == "__main__":
    print(get_system_health())