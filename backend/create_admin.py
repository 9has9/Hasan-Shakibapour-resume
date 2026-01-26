from sqlalchemy.orm import Session
from database import SessionLocal
import models
from passlib.context import CryptContext

# تنظیم هش پسورد
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# اتصال به دیتابیس
db: Session = SessionLocal()

# مشخصات ادمین
username = "admin"
password = "admin123"  # میتونی تغییرش بدی
hashed_password = pwd_context.hash(password)

# چک کردن وجود ادمین
existing_admin = db.query(models.Admin).filter_by(username=username).first()

if existing_admin:
    print("Admin already exists.")
else:
    admin = models.Admin(username=username, hashed_password=hashed_password)
    db.add(admin)
    db.commit()
    print("Admin created successfully.")

db.close()
