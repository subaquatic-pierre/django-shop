
import json

with open('/home/ubuntu/etc/config.json') as f:
	config = json.load(f)

class Config():

	SECRET_KEY = config.get("SECRET_KEY")
	DB_NAME = "DB_NAME"
	DB_USER = "your-db-user-name"
	DB_PASSWORD = "DB_PASSWORD"
	DB_HOST = "DB_HOST"
	STRIPE_LIVE_PUBLIC_KEY = "STRIPE_LIVE_PUBLIC_KEY"
	STRIPE_LIVE_SECRET_KEY = "STRIPE_LIVE_SECRET_KEY"
	EMAIL_HOST_USER = "subaquatic.pierre@gmail.com"
	EMAIL_HOST_PASSWORD = "somesupersecretpassword"

