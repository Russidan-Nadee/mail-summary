import time
import logging
from datetime import datetime
from scripts.auth import auth_google

REFRESH_INTERVAL = 30 * 60  # ทุก 30 นาที

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

if __name__ == "__main__":
    while True:
        try:
            creds = auth_google()  # refresh ถ้าจำเป็น
            logging.info(f"Token refreshed at {datetime.now()}")
        except Exception as e:
            logging.error(f"Refresh failed: {e}")
        time.sleep(REFRESH_INTERVAL)
