import psutil
import time
import os

def get_cpu_temp():
    try:
        temps = psutil.sensors_temperatures()

        for sensor_name, entries in temps.items():
            for entry in entries:
                if entry.current:
                    return entry.current

        return None

    except Exception:
        return None


while True:
    os.system("clear")

    cpu_usage = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()

    print("=" * 40)
    print("      Ubuntu System Monitor")
    print("=" * 40)
    print(f"CPU Usage : {cpu_usage:.1f}%")

    temp = get_cpu_temp()
    if temp is not None:
        print(f"CPU Temp  : {temp:.1f}°C")
    else:
        print("CPU Temp  : Not available")

    print(f"RAM Usage : {ram.percent:.1f}%")
    print(f"RAM Used  : {ram.used / (1024**3):.2f} GB")
    print(f"RAM Total : {ram.total / (1024**3):.2f} GB")
    print("=" * 40)

    time.sleep(1)