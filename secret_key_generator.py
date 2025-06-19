import os

secret_key = os.urandom(32)
print(secret_key.hex())