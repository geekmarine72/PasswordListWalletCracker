#!/usr/bin/env python
import base64, hashlib, hmac, json, sys, getpass
from Crypto.Cipher import AES
from Crypto.Hash import RIPEMD, SHA256

base58_chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'



def ReadWalletFile(walletfile):
	try:
		wfile = open(walletfile)
		wallet = wfile.readline()
		wfile.close
		return True, wallet
	except:
		print("Could not read wallet file: " + walletfile)
		return False, ""

def ReadPasswordList(passwordfile):
	try:
		pfile = open(passwordfile)
		passwords = pfile.readlines()
		pfile.close
		return True, passwords
	except:
		print("Could not read password file: " + passwordfile)
		return False, ""

def IsJson( text ):
    try:
        obj = json.loads(clear)
        return True
    except:
        return False 

def IsDoubleEncrypted(walletText):
	try:
		obj = json.loads(walletText)
		if (obj.has_key('double_encryption')):
			return True
		else:
			return False
	except:
		return False
            
def DecryptDoubleLayer(walletText, password):
    try:
		obj = json.loads(walletText)
		if (obj.has_key('double_encryption')):
		    for key in obj['keys']: key['priv'] = Decrypt(key['priv'], password)
		    for key in obj['keys']: key['priv_sipa'] = to_sipa(key['priv'])
		    print(json.dumps(obj, indent=4, sort_keys = True))
    except ValueError as err:
      	return False

def Decrypt(encrypted, password):
    encrypted = base64.b64decode(encrypted)
    iv, encrypted = encrypted[:16], encrypted[16:]
    aeshash = pbkdf2(password, iv, 10, 32)
    clearText =remove_iso10126_padding( AES.new(aeshash, AES.MODE_CBC, iv).decrypt(encrypted) )
    success = IsJson(clearText)
    return success, clearText

def remove_iso10126_padding(s):
    ba = bytearray(s)
    pad_len = ba[-1]
    return str(ba[:-pad_len])

def base58_decode(v):
  value = 0; ret = ''
  for c in v: value = value*58 + base58_chars.find(c)
  for i in range(32):
      ret = "%c"%(value%256) + ret; value /= 256
  return ret

def base58_encode(v):
    value = 0; ret = ''
    for c in v: value = value*256 + ord(c)
    while value > 0:
        ret = base58_chars[value%58] + ret; value /= 58
    return ret

def to_sipa(s):
    version = 128 # or 239 for testnet
    key = chr(version) + base58_decode(s)
    return base58_encode(key + SHA256.new(SHA256.new(key).digest()).digest()[:4])

# pbkdf2 from http://matt.ucc.asn.au/src/pbkdf2.py

from struct import pack

# this is what you want to call.
def pbkdf2( password, salt, itercount, keylen, hashfn = hashlib.sha1 ):
    digest_size = hashfn().digest_size

    # l - number of output blocks to produce
    l = keylen / digest_size
    if keylen % digest_size != 0:
        l += 1

    h = hmac.new( password, None, hashfn )

    T = ""
    for i in range(1, l+1):
        T += pbkdf2_F( h, salt, itercount, i )

    return T[0: keylen]

def xorstr( a, b ):
    if len(a) != len(b):
        raise "xorstr(): lengths differ"

    ret = ''
    for i in range(len(a)):
        ret += chr(ord(a[i]) ^ ord(b[i]))

    return ret

def prf( h, data ):
    hm = h.copy()
    hm.update( data )
    return hm.digest()

# Helper as per the spec. h is a hmac which has been created seeded with the
# password, it will be copy()ed and not modified.
def pbkdf2_F( h, salt, itercount, blocknum ):
    U = prf( h, salt + pack('>i',blocknum ) )
    T = U

    for i in range(2, itercount+1):
        U = prf( h, U )
        T = xorstr( T, U )

    return T

### ENTRY POINT ###

print("\nStarting wallet password cracker")

# Write error and exit if values aren't passwed at comand line:
if len(sys.argv) < 3:
    sys.stderr.write('Usage: sys.argv[0] [wallet.aes.json] [passwordfile]\n')
    sys.exit(1)
else:
	walletfile = sys.argv[1]
	passwordfile = sys.argv[2]

def tick():
	sys.stdout.write(".")
	sys.stdout.flush()

def bang():
	sys.stdout.write("!")
	sys.stdout.flush()

# Read File And Return Cipher Text

readwallet, ciphertext = ReadWalletFile(walletfile)
if(readwallet == False):
	print("Wallet read failed, exiting")
	sys.exit()

# Read Password List and Return Array

readpasswords, passwords = ReadPasswordList(passwordfile)
if(readpasswords == False):
	print("Passwords read failed, exiting")
	sys.exit()
else:
	print("Attempting " + str(len(passwords)) + " passwords")

#Check and retrieve first password if known
firstpassword = ""
cracked = False
#For each password, attempt first round of decipherment
print("Starting first phase password cracking")
for password in passwords:
	cracked, cleartext = Decrypt(ciphertext, password)
	if(cracked != True):
		tick()
	else:
		bang()
		firstpassword = password
		print("Found first password: " + firstpassword)
		break


#If first round is successful, write first password to file then parse for Encrypted body
if(cracked != True):
	print("\nFailed to find first round password, sorry! Quiting ...")
	sys.exit()

#If encrypted body found attempt second decipherment

if(IsDoubleEncrypted(cleartext) != True):
	print("Wallet is not double encrytped. We won!")
	sys.exit()

secondpassword = ""
for password in passwords:
	cracked, cleartext = DecryptDoubleLayer(clear, password)
	if(cracked != True):
		tick
	else:
		bang
		secondpassword = password
		print("Found second password: " + secondpassword)
		break
#If second round is successful, write second password to file, then write plain text to file
