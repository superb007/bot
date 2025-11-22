import random
import string

def g_code():
    characters = string.ascii_letters + string.digits  # Letters and digits
    return ''.join(random.sample(characters, 6))