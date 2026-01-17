from datetime import datetime
from zoneinfo import ZoneInfo
import os

print("Current System Time (What scraper currently uses):")
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

print("\nPeru Time (Goal):")
print(datetime.now(ZoneInfo("America/Lima")).strftime("%Y-%m-%d %H:%M:%S"))
