from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


def extract_pem_from_armored(armored_key):
    """
    Extract PEM key from PGP armored format.
    Args:
        armored_key (str): PGP armored key (public or private)
    Returns:
        str: PEM-encoded key (without armor headers/footers)
    """
    lines = armored_key.split('\n')
    pem_lines = []
    in_pem = False
    for line in lines:
        if "BEGIN PGP" in line:
            in_pem = True
            continue
        if "END PGP" in line:
            break
        if in_pem and line.strip():
            pem_lines.append(line)
    return '\n'.join(pem_lines)


def encrypt_plaintext(public_key_armored, plaintext):
    """
    Encrypt plaintext using a PGP public key (armored format).
    Args:
        public_key_armored (str): Public key in PGP armored format
        plaintext (str): Plaintext to encrypt
    Returns:
        bytes: Encrypted ciphertext
    """
    # Extract PEM from armored block
    public_key_pem = extract_pem_from_armored(public_key_armored)

    # Load public key
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode(),
        backend=default_backend()
    )

    # Encrypt with RSA-OAEP
    ciphertext = public_key.encrypt(
        plaintext.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext


def decrypt_plaintext(private_key_armored, ciphertext):
    """
    Decrypt ciphertext using a PGP private key (armored format).
    Args:
        private_key_armored (str): Private key in PGP armored format
        ciphertext (bytes): Encrypted ciphertext
    Returns:
        str: Decrypted plaintext
    """
    # Extract PEM from armored block
    private_key_pem = extract_pem_from_armored(private_key_armored)

    # Load private key (passphrase hardcoded to None)
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None,  # Force no passphrase
        backend=default_backend()
    )

    # Decrypt with RSA-OAEP
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext.decode()