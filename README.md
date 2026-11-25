# PM2.5 Explorer

ระบบสำรวจคุณภาพอากาศ PM2.5 ของประเทศไทย (รายวิชา 1145100 Data Science Toolbox)

## วิธีติดตั้ง
uv sync pyproject.toml

## วิธีดึงข้อมูล
```
uv run python src/fetch_air4thai.py
```
บันทึก JSON ดิบเป็น `data/raw/air4thai_YYYYMMDDTHHMMSS.json` และ log ที่ `data/raw/fetch.log` (โฟลเดอร์ `data/` ไม่ถูก commit)

## แหล่งข้อมูล
- **แหล่งที่มา:** Air4Thai กรมควบคุมมลพิษ (http://air4thai.pcd.go.th) endpoint `services/getNewAQI_JSON.php` ให้ค่าตรวจวัดล่าสุดของทุกสถานี
- **ผลตรวจ robots.txt (25 พ.ย. 2569):** `robots.txt` ของเว็บไซต์ตอบกลับ HTTP 404 (ไม่มีไฟล์) `RobotFileParser.can_fetch` จึงคืนค่า `True` คือไม่มีข้อห้ามสำหรับ endpoint นี้
- **เงื่อนไขการใช้ข้อมูล:** หน้าเว็บ Air4Thai ไม่มีหน้าข้อตกลงการใช้ข้อมูลแยกต่างหาก ระบุเพียง "Copyright © 2013-Present กรมควบคุมมลพิษ" และมีหน้า "ขั้นตอนการขอข้อมูลคุณภาพอากาศและเสียง" สำหรับขอข้อมูลอย่างเป็นทางการ โครงการนี้ใช้ข้อมูลเพื่อการศึกษาเท่านั้น ดึงไม่เกินชั่วโมงละ 1 ครั้ง และระบุตัวตนใน User-Agent
- **การอ้างอิง:** ข้อมูลคุณภาพอากาศจาก กรมควบคุมมลพิษ, Air4Thai (http://air4thai.pcd.go.th) เข้าถึงระหว่าง พ.ย. 2569

## ผู้จัดทำ
ธีรพล พูพวง 67114540277
