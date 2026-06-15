from utilities.utils import get_hashed_password

# Konversi password ke hash
password = "Dik123!!"
hashed_password = get_hashed_password(password)
print(hashed_password)
# Output: $1$xxxxxx$xxxxxxxxxxxxx (format MD5 Crypt)