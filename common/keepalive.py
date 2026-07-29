import threading
import time
import logging

logger = logging.getLogger(__name__)

def start_db_keepalive():
    def ping():
        time.sleep(15)
        while True:
            try:
                import psycopg2
                from decouple import config
                conn = psycopg2.connect(config('DATABASE_URL'))
                cur = conn.cursor()
                cur.execute("SELECT 1")
                cur.close()
                conn.close()
                logger.debug("DB keep-alive ping sent")
            except Exception as e:
                logger.warning(f"DB keep-alive failed: {e}")
            time.sleep(240)

    thread = threading.Thread(target=ping, daemon=True)
    thread.start()