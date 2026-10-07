import unittest
from circuit import TicketPublic, TicketWitness, ticket_tag, validate_circuit
from zk_schnorr import public_key, prove, verify, simulate, verify_interactive


class TestPrototype(unittest.TestCase):
    def setUp(self):
        self.secret = 73129
        self.public = TicketPublic(
            ticket_id=20260081,
            attraction_code=1,
            issue_day=280,
            validity_days=10,
            public_tag=ticket_tag(self.secret, 20260081, 1, 280, 10),
            public_key=public_key(self.secret),
        )

    def test_valid_circuit(self):
        self.assertTrue(validate_circuit(self.public, TicketWitness(self.secret)))

    def test_wrong_secret_rejected(self):
        self.assertFalse(validate_circuit(self.public, TicketWitness(self.secret + 1)))

    def test_invalidity_rejected(self):
        invalid = TicketPublic(
            **{**self.public.__dict__, "validity_days": 11}
        )
        self.assertFalse(validate_circuit(invalid, TicketWitness(self.secret)))

    def test_schnorr_proof(self):
        context = f"ticket={self.public.ticket_id}|attraction={self.public.attraction_code}"
        proof = prove(self.secret, self.public.public_key, context)
        self.assertTrue(verify(self.public.public_key, context, proof))

    def test_tampered_proof_rejected(self):
        context = f"ticket={self.public.ticket_id}|attraction={self.public.attraction_code}"
        proof = prove(self.secret, self.public.public_key, context)
        tampered = type(proof)(proof.commitment, proof.challenge, proof.response + 1)
        self.assertFalse(verify(self.public.public_key, context, tampered))

    def test_simulator_transcript(self):
        context = f"ticket={self.public.ticket_id}|attraction={self.public.attraction_code}"
        simulated = simulate(self.public.public_key, context)
        # En el protocolo real, el challenge debe estar ligado a u mediante Fiat-Shamir.
        # El simulador aquí se presenta solo como evidencia pedagógica del transcript HVZK.
        self.assertTrue(verify_interactive(self.public.public_key, simulated))


if __name__ == "__main__":
    unittest.main()
