from passlib.hash import md5_crypt

password = "Dosen123!!"

# Generate hash dengan salt acak
hashed = md5_crypt.hash(password)

print(hashed)