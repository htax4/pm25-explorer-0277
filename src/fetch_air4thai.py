"""ดึงข้อมูลคุณภาพอากาศล่าสุดจาก Air4Thai แล้วเก็บ JSON ดิบลง data/raw/

วิธีรัน (จากโฟลเดอร์ repo):  uv run python src/fetch_air4thai.py
exit code: 0 = สำเร็จ, 1 = ล้มเหลว
"""
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

try:
    import truststore

    truststore.inject_into_ssl()  # ใช้ใบรับรองของระบบปฏิบัติการ แก้ปัญหา chain ของ server ไม่ครบ
except ImportError:
    pass

URL = "http://air4thai.pcd.go.th/services/getNewAQI_JSON.php"
HEADERS = {
    # ต้องเป็น ASCII เท่านั้น (ห้ามมีภาษาไทยใน header)
    "User-Agent": "pm25-explorer-0277/0.1 (student project; teerapon.po.67@ubu.ac.th)"
}
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
TZ = ZoneInfo("Asia/Bangkok")
RETRIES, WAIT = 3, 5
RETRY_STATUS = {429, 500, 502, 503, 504}

# ต้องสร้างโฟลเดอร์ก่อนตั้ง logging เพราะ file handler จะเขียนลง RAW_DIR / "fetch.log"
RAW_DIR.mkdir(parents=True, exist_ok=True)
log = logging.getLogger("fetch_air4thai")
log.setLevel(logging.INFO)
_fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
for _h in (logging.StreamHandler(), logging.FileHandler(RAW_DIR / "fetch.log", encoding="utf-8")):
    _h.setFormatter(_fmt)
    log.addHandler(_h)


def fetch(url: str) -> requests.Response:
    """GET พร้อม retry เฉพาะปัญหาชั่วคราว (เชื่อมต่อไม่ได้, timeout, 429, 5xx)"""
    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=(10, 60))  # (connect, read) วินาที
        except (requests.ConnectionError, requests.Timeout) as e:
            log.warning("attempt %d/%d: %s", attempt, RETRIES, type(e).__name__)
        else:
            if r.status_code in RETRY_STATUS:
                log.warning("attempt %d/%d: HTTP %d", attempt, RETRIES, r.status_code)
            else:
                r.raise_for_status()  # 4xx อื่น เช่น 404 = เรียกผิด ลองซ้ำก็ไม่หาย จึง raise ทันที
                return r
        if attempt < RETRIES:
            time.sleep(WAIT * attempt)  # รอนานขึ้นทุกรอบ: 5, 10 วินาที
    raise RuntimeError(f"fetch failed after {RETRIES} attempts")


def validate(r: requests.Response) -> int:
    """ตรวจว่า body เป็น JSON ที่มี key 'stations' เป็น list ไม่ว่าง แล้วคืนจำนวนสถานี"""
    data = r.json()  # ถ้า server ส่ง HTML มาจะเกิด ValueError ตรงนี้
    stations = data.get("stations") if isinstance(data, dict) else None
    if not isinstance(stations, list) or not stations:
        raise ValueError("response has no non-empty 'stations' list")
    return len(stations)


def main() -> int:
    fetched_at = datetime.now(TZ)  # เวลาที่ดึง (ไม่ใช่เวลาที่วัดค่า ซึ่งอยู่ใน AQILast.date/time)
    try:
        r = fetch(URL)
        n = validate(r)
    except Exception as e:
        log.error("%s: %s", type(e).__name__, e)
        return 1
    out = RAW_DIR / f"air4thai_{fetched_at:%Y%m%dT%H%M%S}.json"
    out.write_bytes(r.content)  # เก็บ byte ดิบตามที่ server ส่งมา ไม่ผ่านการ decode/แปลง
    log.info("saved %s (%d stations, %d bytes)", out.name, n, len(r.content))
    return 0


if __name__ == "__main__":
    sys.exit(main())
