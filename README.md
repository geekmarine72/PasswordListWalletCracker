# SmartWalletCracker.py

A rewrite of the passwordlistwalletcracker. This version provides better feedback on run execution with intelligent support for double encrypted wallets.  Attempts to decipher both primary and secondary cycle passwords from a list of passwords.

Usage:  python smartWalletCracker.py [walletfile] [passwordlistfile] 

# PasswordListWalletCracker - DEPRECATED
Attempts to decipher a given wallet.aes.json using a password list

Note, when you need to get the pycrypto library to run. (easy_install pycrypto). 

I am not sure this even works.  It's a fork of code that claims to be able to decipher a wallet.aes.json blockchain wallet backup.  I intend to create a new wallet with a new password to confirm. 

Requires the wallest.aes.json file and a text file list of passwords (one per line) 

Created in an effort to recover the password from a 4+ year old bitcoin wallet (with .55 BTC in it). 

Usage:  python PasswordListWalletCracker [walletfile] [passwordlistfile] 

If your wallet backup is named "wallet.aes.json", as most are, and you've created a list of passwords called "passwords.txt", then the command would be

python PasswordListWalletCracker wallet.aes.json passwords.txt

Let me know if it works for you.  Will be posting once I confirm it works
