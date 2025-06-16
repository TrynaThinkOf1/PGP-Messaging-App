from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_rsa_keypair():
    # Generate a 4096-bit RSA private key with public exponent 65537
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096
    )
    # Serialize the private key to PEM (traditional PKCS#1) without encryption
    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    # Extract and serialize the public key to PEM (SubjectPublicKeyInfo)
    public_key = private_key.public_key()
    pub_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return priv_pem.decode('utf-8'), pub_pem.decode('utf-8')



def genkey():
    return generate_rsa_keypair()