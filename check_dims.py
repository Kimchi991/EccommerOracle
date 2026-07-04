import os
from PIL import Image

files = [
    "login_page.png", "dashboard_page.png", "customers_page.png", "products_page.png",
    "orders_page.png", "order_details_page.png", "payments_page.png", "logs_page.png"
]

for f in files:
    if os.path.exists(f):
        img = Image.open(f)
        print(f"{f}: {img.size}")
    else:
        print(f"{f} does not exist")
