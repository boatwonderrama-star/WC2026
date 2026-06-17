# World Cup 2026 — ตารางคะแนน 7 ทีมเลือก (อัปเดตอัตโนมัติทุกวัน)

เว็บไซต์เล็กๆ ที่แสดงตารางคะแนนบอลโลก 2026 เฉพาะ 7 ทีม:
ฝรั่งเศส 🇫🇷 เยอรมัน 🇩🇪 ญี่ปุ่น 🇯🇵 สเปน 🇪🇸 อาร์เจนติน่า 🇦🇷 เนเธอร์แลนด์ 🇳🇱 โปรตุเกส 🇵🇹

ข้อมูลดึงจาก [openfootball/worldcup.json](https://github.com/openfootball/worldcup.json)
(public domain ไม่ต้องใช้ API key) แล้ว build เป็นหน้า HTML ใหม่ทุกวันอัตโนมัติ
ผ่าน GitHub Actions + โฮสต์ฟรีบน GitHub Pages

---

## วิธี deploy (ทำครั้งเดียว ใช้เวลา ~10 นาที)

### 1. สร้าง repository ใหม่บน GitHub
- ไปที่ https://github.com/new
- ตั้งชื่อ repo เช่น `wc2026-tracker`
- เลือก **Public** (จำเป็น ถ้าอยากใช้ GitHub Pages ฟรี)
- กด **Create repository**

### 2. อัปโหลดไฟล์ทั้งหมดในโฟลเดอร์นี้ขึ้น repo
มีไฟล์ดังนี้:
```
.github/workflows/update.yml   <- ตัวจัดการรันอัตโนมัติทุกวัน
scripts/build.py               <- สคริปต์ดึงข้อมูล + สร้างหน้าเว็บ
docs/index.html                <- หน้าเว็บ (จะถูกเขียนทับอัตโนมัติ ไม่ต้องแก้)
README.md                      <- ไฟล์นี้
```

วิธีอัปโหลดง่ายที่สุด (ไม่ต้องใช้ command line):
- เปิดหน้า repo ที่สร้างไว้ → กด **uploading an existing file**
- ลากไฟล์ทั้งหมด (รวมโฟลเดอร์ `.github` และ `scripts` และ `docs`) ลงไป
- กด **Commit changes**

> ถ้าใช้ git บนคอมพิวเตอร์ตัวเอง ก็ใช้คำสั่งปกติ:
> ```
> git init
> git add .
> git commit -m "initial commit"
> git remote add origin https://github.com/<username>/wc2026-tracker.git
> git push -u origin main
> ```

### 3. เปิดใช้งาน GitHub Pages
- ไปที่ repo → **Settings** → **Pages** (เมนูด้านซ้าย)
- ตรง **Source** เลือก **GitHub Actions**
- กด Save (ถ้ามี)

### 4. รัน workflow ครั้งแรกด้วยตัวเอง
- ไปที่แท็บ **Actions** ของ repo
- เลือก workflow ชื่อ **Update World Cup 2026 standings**
- กด **Run workflow** (ปุ่มสีเขียวด้านขวา) → กด **Run workflow** อีกครั้งเพื่อยืนยัน
- รอประมาณ 30-60 วินาที จนเห็นเครื่องหมายถูกสีเขียว ✅

### 5. เอาลิงก์ไปแชร์ให้เพื่อน
ลิงก์จะอยู่ที่:
```
https://<username>.github.io/wc2026-tracker/
```
(เช็คลิงก์ที่แน่นอนได้จาก Settings → Pages หลัง deploy เสร็จ)

---

## มันอัปเดตยังไง

GitHub Actions จะรันสคริปต์ `scripts/build.py` ให้เองทุกวัน เวลา 00:00 UTC (07:00 เวลาไทย)
ตามที่ตั้งไว้ใน `.github/workflows/update.yml`:
```yaml
schedule:
  - cron: "0 0 * * *"
```
ถ้าอยากเปลี่ยนเวลา หรืออยากให้อัปเดตบ่อยกว่านี้ (เช่นทุก 6 ชั่วโมง) แก้บรรทัด cron ได้เลย
เช่น `"0 */6 * * *"` คือทุก 6 ชั่วโมง

อยากอัปเดตทันทีไม่ต้องรอ ก็กด **Run workflow** ที่แท็บ Actions ได้ตลอดเวลา

## หมายเหตุ

- ข้อมูลจาก openfootball เป็นข้อมูลที่อัปเดตโดยอาสาสมัครประมาณวันละครั้ง ไม่ใช่ real-time วินาทีต่อวินาที
- ถ้าทีมที่เลือกยังไม่ได้ลงเล่น จะแสดงคะแนน 0 และไม่มีกลุ่มแสดง (เป็นปกติ)
- ถ้าอยากเปลี่ยนทีมที่ติดตาม แก้ตัวแปร `TEAMS` ใน `scripts/build.py` ได้เลย
