"""
Circuitos aritméticos educativos para validación de boletos turísticos.

Este prototipo NO es un sistema criptográfico de producción.
Modela un circuito sobre un campo finito y una relación R1CS sencilla.
"""

from dataclasses import dataclass

FIELD = 2_147_483_647  # primo de Mersenne, suficiente para el prototipo educativo


def mod(x: int) -> int:
    return x % FIELD


@dataclass(frozen=True)
class TicketPublic:
    ticket_id: int
    attraction_code: int
    issue_day: int
    validity_days: int
    public_tag: int
    public_key: int


@dataclass(frozen=True)
class TicketWitness:
    secret: int


def ticket_tag(secret: int, ticket_id: int, attraction_code: int,
               issue_day: int, validity_days: int) -> int:
    """
    Etiqueta algebraica educativa:
    tag = secret + 7*ticket_id + 11*attraction + 13*issue_day + 17*validity
    """
    return mod(
        secret
        + 7 * ticket_id
        + 11 * attraction_code
        + 13 * issue_day
        + 17 * validity_days
    )


def validate_circuit(public: TicketPublic, witness: TicketWitness) -> bool:
    """
    Evalúa el circuito aritmético del boleto.

    Restricciones educativas:
      1) secret * 1 = secret
      2) tag(public data, secret) = public_tag
      3) 1 <= validity_days <= 10
    """
    s = mod(witness.secret)

    # Gate de identidad del witness.
    r1 = mod(s * 1 - s) == 0

    # Gate principal: relación algebraica pública/privada.
    expected = ticket_tag(
        s,
        public.ticket_id,
        public.attraction_code,
        public.issue_day,
        public.validity_days,
    )
    r2 = expected == mod(public.public_tag)

    # Restricción de rango del prototipo (el BTC real tiene reglas por modalidad).
    r3 = 1 <= public.validity_days <= 10

    return r1 and r2 and r3


def build_r1cs(public: TicketPublic):
    """
    Representación simbólica mínima de las restricciones.

    Cada fila sigue la convención A*B-C=0.
    No pretende ser un compilador Circom/R1CS completo.
    """
    return [
        {
            "name": "witness_identity",
            "A": {"secret": 1},
            "B": {"one": 1},
            "C": {"secret": 1},
        },
        {
            "name": "ticket_tag",
            "A": {"one": 1},
            "B": {
                "secret": 1,
                "ticket_id": 7,
                "attraction_code": 11,
                "issue_day": 13,
                "validity_days": 17,
            },
            "C": {"public_tag": 1},
        },
    ]
