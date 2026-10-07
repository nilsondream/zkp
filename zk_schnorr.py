"""
Protocolo Schnorr educativo para demostrar conocimiento de un secreto.

La construcción sigue el esquema:
  u = g^r
  c = challenge
  z = r + c*x
  verificar: g^z = u * h^c

Se usa un grupo multiplicativo pequeño solo con fines didácticos.
NO usar estos parámetros para seguridad real.
"""

from dataclasses import dataclass
import hashlib
import secrets

# Parámetros pequeños y deliberadamente educativos.
P = 2_147_483_647
Q = P - 1
G = 5


@dataclass(frozen=True)
class SchnorrProof:
    commitment: int
    challenge: int
    response: int


def public_key(secret: int) -> int:
    return pow(G, secret, P)


def challenge(commitment: int, public: int, context: str) -> int:
    msg = f"{commitment}|{public}|{context}".encode()
    return int.from_bytes(hashlib.sha256(msg).digest(), "big") % Q


def prove(secret: int, public: int, context: str) -> SchnorrProof:
    r = secrets.randbelow(Q)
    u = pow(G, r, P)
    c = challenge(u, public, context)
    z = (r + c * secret) % Q
    return SchnorrProof(u, c, z)


def verify(public: int, context: str, proof: SchnorrProof) -> bool:
    c2 = challenge(proof.commitment, public, context)
    if c2 != proof.challenge:
        return False
    left = pow(G, proof.response, P)
    right = (proof.commitment * pow(public, proof.challenge, P)) % P
    return left == right


def verify_interactive(public: int, proof: SchnorrProof) -> bool:
    """Verificación del transcript interactivo con challenge ya fijado."""
    left = pow(G, proof.response, P)
    right = (proof.commitment * pow(public, proof.challenge, P)) % P
    return left == right


def simulate(public: int, context: str = "") -> SchnorrProof:
    """
    Simulador HVZK educativo del protocolo interactivo.
    Aquí el challenge NO se deriva de Fiat-Shamir: se eligen c,z y
    se reconstruye u para que g^z = u*h^c.
    """
    c = secrets.randbelow(Q)
    z = secrets.randbelow(Q)
    h_c = pow(public, c, P)
    inv_h_c = pow(h_c, P - 2, P)
    u = (pow(G, z, P) * inv_h_c) % P
    return SchnorrProof(u, c, z)
