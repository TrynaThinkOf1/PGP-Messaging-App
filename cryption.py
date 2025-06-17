from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64


def encrypt_plaintext(message, public_key_pem):
    """
    Encrypt a message using PGP-style hybrid encryption:
    1. Generate a random AES key
    2. Encrypt the message with AES
    3. Encrypt the AES key with RSA public key
    4. Return both encrypted components
    """
    # Convert message to bytes if it's a string
    if isinstance(message, str):
        message = message.encode('utf-8')

    # Load the public key
    public_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))

    # Generate a random 256-bit AES key
    aes_key = os.urandom(32)  # 256 bits

    # Generate a random IV for AES
    iv = os.urandom(16)  # 128 bits for AES

    # Encrypt the message with AES in CBC mode
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    encryptor = cipher.encryptor()

    # Pad the message to be a multiple of 16 bytes (PKCS7 padding)
    padding_length = 16 - (len(message) % 16)
    padded_message = message + bytes([padding_length] * padding_length)

    encrypted_message = encryptor.update(padded_message) + encryptor.finalize()

    # Encrypt the AES key with RSA public key
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Combine encrypted AES key, IV, and encrypted message
    # Format: [encrypted_aes_key_length][encrypted_aes_key][iv][encrypted_message]
    result = (
            len(encrypted_aes_key).to_bytes(4, 'big') +
            encrypted_aes_key +
            iv +
            encrypted_message
    )

    # Return base64 encoded result for easy handling
    return base64.b64encode(result).decode('utf-8')


def decrypt_plaintext(encrypted_data, private_key_pem):
    """
    Decrypt a message using PGP-style hybrid decryption:
    1. Extract the encrypted AES key and decrypt it with RSA private key
    2. Extract the IV and encrypted message
    3. Decrypt the message with AES
    """
    # Decode from base64
    encrypted_data = base64.b64decode(encrypted_data.encode('utf-8'))

    # Load the private key
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None
    )

    # Extract components
    # First 4 bytes: length of encrypted AES key
    aes_key_length = int.from_bytes(encrypted_data[:4], 'big')

    # Next aes_key_length bytes: encrypted AES key
    encrypted_aes_key = encrypted_data[4:4 + aes_key_length]

    # Next 16 bytes: IV
    iv = encrypted_data[4 + aes_key_length:4 + aes_key_length + 16]

    # Remaining bytes: encrypted message
    encrypted_message = encrypted_data[4 + aes_key_length + 16:]

    # Decrypt the AES key with RSA private key
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Decrypt the message with AES
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    decryptor = cipher.decryptor()

    padded_message = decryptor.update(encrypted_message) + decryptor.finalize()

    # Remove PKCS7 padding
    padding_length = padded_message[-1]
    message = padded_message[:-padding_length]

    # Return as string if it's valid UTF-8, otherwise return bytes
    try:
        return message.decode('utf-8')
    except UnicodeDecodeError:
        return message


# Example usage and testing
if __name__ == "__main__":
    # Generate keypair
    private_key_pem, public_key_pem = genkey()

    # Test message
    test_message = "Hello, this is a secret message encrypted using PGP-style hybrid cryptography!"

    print("Original message:", test_message)
    print("\n" + "=" * 50)

    # Encrypt the message
    encrypted = encrypt_message(test_message, public_key_pem)
    print("Encrypted (base64):", encrypted[:100] + "..." if len(encrypted) > 100 else encrypted)

    # Decrypt the message
    decrypted = decrypt_message(encrypted, private_key_pem)
    print("Decrypted message:", decrypted)

    # Verify they match
    print("\nEncryption/Decryption successful:", test_message == decrypted)