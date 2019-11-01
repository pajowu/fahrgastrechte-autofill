import functions, json
args = functions.parse_args()
with open(args.auftragsnummer + ".pkpass", "wb") as f:
	f.write(functions.download_passbook(args.auftragsnummer, args.nachname))
print("Wrote passbook to {}.pkpass".format(args.auftragsnummer))
