from datetime import datetime

from dateutil.relativedelta import relativedelta

from yogsite.config import cfg
from yogsite import db
from yogsite.util import byondname_to_ckey

# If you have gotten this far you are already dead
def process_ipn_notification(ipn_args):
	valid = True
	notes = []

	amount = ipn_args.get("mc_gross", type=float)

	months = 0
	for tier in cfg.get("donation.tiers"):
		if amount >= tier["amount"]:
			if tier["months"] > months:
				months = tier["months"]
	
	donate_time = datetime.utcnow()
	expiration_time = donate_time + relativedelta(months=months) if months > 0 else None

	ckey = byondname_to_ckey(ipn_args.get("custom", type=str))

	transaction_id = ipn_args.get("txn_id", type=str)

	status = ipn_args.get("payment_status").lower()
	pending_reason = ipn_args.get("pending_reason")

	payer_email = ipn_args.get("payer_email")
	receiver_email = ipn_args.get("receiver_email")

	currency = ipn_args.get("mc_currency")

	sandbox = ipn_args.get("test_ipn")

	if sandbox:
		notes.append("sandbox transaction")
		valid = False
	
	if months == 0:
		notes.append("does not meet any donation tier")
		valid = False
	
	if currency != "USD":
		notes.append(f"bad currency: {currency}")
		valid = False
	
	if receiver_email != cfg.get("paypal.email"):
		notes.append(f"tampered email: {receiver_email}")
	
	if ckey == "":
		ckey = "Anonymous" # I hate this but it's how it was done in the php so I also have to do it like this
		notes.append("anonymous donation")
		valid = False # Anonymous people get no benefits
	
	if status == "pending":
		notes.append(f"pending because: \"{pending_reason}\"")
		valid = False
	
	if status == "denied":
		notes.append(f"denied because: \"{pending_reason}\"")
		valid = False

	existing_donation = db.game_db.query(db.Donation).filter(db.Donation.transaction_id == transaction_id).first()

	if existing_donation:
		existing_donation.status = status
		existing_donation.valid = int(valid)
		existing_donation.notes = ', '.join(notes)
		db.game_db.commit()

	else:
		donation = db.Donation(
			ckey = ckey,
			transaction_id = transaction_id,
			amount = amount,
			datetime = donate_time,
			expiration_time = expiration_time,
			payer_email = payer_email,
			status = status,
			valid = int(valid),
			notes = ', '.join(notes)
		)

		db.game_db.add(donation)
		db.game_db.commit()