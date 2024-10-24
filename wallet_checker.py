import requests
import json
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes, Bip39MnemonicGenerator
from eth_utils import to_checksum_address

# Load API keys from config file
def load_api_keys():
    with open("config.json", "r") as file:
        config = json.load(file)
    return config

# Generate a random seed phrase
def generate_seed():
    mnemonic = Bip39MnemonicGenerator().FromWordsNumber(12)  # 12-word seed phrase
    return mnemonic

# Derive Bitcoin address from seed phrase
def get_btc_address(seed_phrase, index=0):
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
    bip44_addr_ctx = bip44_acc_ctx.AddressIndex(index)  # Use address index
    return bip44_addr_ctx.PublicKey().ToAddress()

# Derive Ethereum address from seed phrase
def get_eth_address(seed_phrase, index=0):
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
    bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
    bip44_addr_ctx = bip44_acc_ctx.AddressIndex(index)
    eth_address = bip44_addr_ctx.PublicKey().ToAddress()
    return to_checksum_address(eth_address)

# Derive Litecoin address from seed phrase
def get_ltc_address(seed_phrase, index=0):
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.LITECOIN)
    bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
    bip44_addr_ctx = bip44_acc_ctx.AddressIndex(index)
    return bip44_addr_ctx.PublicKey().ToAddress()

# Check Bitcoin balance using Blockchain.info API
def check_btc_balance(address):
    try:
        url = f"https://blockchain.info/q/addressbalance/{address}?confirmations=6"
        response = requests.get(url)
        if response.status_code == 200:
            balance = int(response.text) / 1e8  # Bitcoin balance in BTC
            return balance
        else:
            print(f"Error fetching BTC balance for {address}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching BTC balance for {address}: {e}")
        return None

# Check Ethereum balance using Etherscan API
def check_eth_balance(address, api_key):
    try:
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            balance_wei = int(response.json()["result"])
            balance_eth = balance_wei / 1e18  # Convert Wei to Ether
            return balance_eth
        else:
            print(f"Error fetching ETH balance for {address}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching ETH balance for {address}: {e}")
        return None

# Check Litecoin balance using Chain.so API
def check_ltc_balance(address):
    try:
        url = f"https://chain.so/api/v2/get_address_balance/LTC/{address}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            balance = float(data["data"]["confirmed_balance"])
            return balance
        else:
            print(f"Error fetching LTC balance for {address}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching LTC balance for {address}: {e}")
        return None

# Main script to generate seed, derive addresses, and check balances
if __name__ == "__main__":
    api_keys = load_api_keys()
    
    # Generate a seed phrase
    seed_phrase = generate_seed()
    print(f"Generated Seed Phrase: {seed_phrase}")
    
    # Loop through multiple address indices (e.g., first 5 addresses)
    for index in range(5):
        # Bitcoin
        btc_address = get_btc_address(seed_phrase, index)
        print(f"Checking BTC Address (index {index}): {btc_address}")
        btc_balance = check_btc_balance(btc_address)
        print(f"Balance for {btc_address}: {btc_balance} BTC" if btc_balance is not None else "Could not retrieve BTC balance")
        
        # Ethereum
        eth_address = get_eth_address(seed_phrase, index)
        print(f"Checking ETH Address (index {index}): {eth_address}")
        eth_balance = check_eth_balance(eth_address, api_keys['etherscan_api_key'])
        print(f"Balance for {eth_address}: {eth_balance} ETH" if eth_balance is not None else "Could not retrieve ETH balance")
        
        # Litecoin
        ltc_address = get_ltc_address(seed_phrase, index)
        print(f"Checking LTC Address (index {index}): {ltc_address}")
        ltc_balance = check_ltc_balance(ltc_address)
        print(f"Balance for {ltc_address}: {ltc_balance} LTC" if ltc_balance is not None else "Could not retrieve LTC balance")
    
    # Log balances if any wallet has a positive balance
    with open("valid_wallets.txt", "a") as file:
        if btc_balance and btc_balance > 0:
            file.write(f"Seed: {seed_phrase} | BTC Address (index {index}): {btc_address} | Balance: {btc_balance} BTC\n")
        if eth_balance and eth_balance > 0:
            file.write(f"Seed: {seed_phrase} | ETH Address (index {index}): {eth_address} | Balance: {eth_balance} ETH\n")
        if ltc_balance and ltc_balance > 0:
            file.write(f"Seed: {seed_phrase} | LTC Address (index {index}): {ltc_address} | Balance: {ltc_balance} LTC\n")
