from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption
from datetime import datetime, UTC


def generate_pgp_key_pair(name, email, comment=None, key_size=4096, passphrase=None):
    """
    Generate PGP public/private key pair.

    Args:
        name (str): Name of key owner
        email (str): Email of key owner
        comment (str, optional): Comment for key
        key_size (int, optional): RSA key size (default: 4096)
        passphrase (str, optional): Passphrase to encrypt private key

    Returns:
        tuple: (public_key_bytes, private_key_bytes)
    """
    # Create user ID string (RFC 4880 format)
    user_id = f"{name} <{email}>"
    if comment:
        user_id = f"{name} ({comment}) <{email}>"

    # Generate RSA key pair
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # Serialize private key
    encryption_algorithm = NoEncryption()
    if passphrase:
        encryption_algorithm = serialization.BestAvailableEncryption(passphrase.encode())

    private_bytes = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm
    )

    # Serialize public key
    public_bytes = public_key.public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo
    )

    # Create PGP-style armored output
    def create_pgp_armor(data, key_type):
        now = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
        header = f"-----BEGIN PGP {key_type} KEY BLOCK-----\n"
        header += f"Version: Python Cryptography\n"
        header += f"Comment: {user_id}\n"
        header += f"Created: {now}\n\n"
        footer = f"\n-----END PGP {key_type} KEY BLOCK-----"
        return header + data.decode('ascii') + footer

    armored_public = create_pgp_armor(public_bytes, "PUBLIC")
    armored_private = create_pgp_armor(private_bytes, "PRIVATE")

    return armored_public, armored_private



def genkey(name):
    return generate_pgp_key_pair(
        name=name,
        email=""
    )