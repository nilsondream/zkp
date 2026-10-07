"""
Prototipo Entrega 1 - Menu interactivo
Circuitos aritmeticos + prueba educativa de conocimiento cero
para validacion de boletos turisticos en Cusco.

Ejecucion:
    py -3 main.py
    python main.py
"""

from circuit import TicketPublic, TicketWitness, ticket_tag, validate_circuit
from zk_schnorr import public_key, prove, verify, simulate, verify_interactive


# ---------------------------------------------------------------------------
# Datos fijos de demostracion (los mismos del ejemplo_manual.md)
# ---------------------------------------------------------------------------
DEMO_SECRET = 73129
DEMO_TICKET_ID = 20260081
DEMO_ATTRACTION = 1
DEMO_ISSUE_DAY = 280
DEMO_VALIDITY = 10


def issue_demo_ticket():
    """Boleto valido de demostracion."""
    public = TicketPublic(
        ticket_id=DEMO_TICKET_ID,
        attraction_code=DEMO_ATTRACTION,
        issue_day=DEMO_ISSUE_DAY,
        validity_days=DEMO_VALIDITY,
        public_tag=ticket_tag(
            DEMO_SECRET, DEMO_TICKET_ID, DEMO_ATTRACTION,
            DEMO_ISSUE_DAY, DEMO_VALIDITY,
        ),
        public_key=public_key(DEMO_SECRET),
    )
    return public, TicketWitness(DEMO_SECRET)


def build_context(public):
    return (
        f"CUSCO|ticket={public.ticket_id}|"
        f"attraction={public.attraction_code}|day={public.issue_day}"
    )


def run_validation(public, witness, context, label="Caso"):
    """Ejecuta el flujo completo y muestra el resultado. Nunca imprime el secreto."""
    print(f"\n--- {label} ---")
    print(f"Ticket publico : {public.ticket_id}")
    print(f"Atractivo      : {public.attraction_code}")
    print(f"Dia emision    : {public.issue_day}")
    print(f"Vigencia       : {public.validity_days} dias")
    print(f"Tag publico    : {public.public_tag}")
    print(f"Clave publica  : {public.public_key}")
    print(f"Contexto       : {context}")

    circuit_ok = validate_circuit(public, witness)
    print(f"\n1. Circuito aritmetico valido: {circuit_ok}")

    proof_ok = False
    if circuit_ok:
        # Solo se genera prueba si el circuito pasa (flujo real de control).
        # Se usa el secreto del witness para probar conocimiento.
        proof = prove(witness.secret, public.public_key, context)
        proof_ok = verify(public.public_key, context, proof)
        print(f"2. Prueba Schnorr valida:      {proof_ok}")

        simulated = simulate(public.public_key, context)
        simulated_ok = verify_interactive(public.public_key, simulated)
        print(f"3. Transcript HVZK simulado:   {simulated_ok}")
    else:
        print("2. Prueba Schnorr:              (no generada, circuito invalido)")
        print("3. Transcript HVZK:             (omitido)")

    accepted = circuit_ok and proof_ok
    print(f"\nResultado: {'ACEPTAR' if accepted else 'RECHAZAR'}")
    return accepted


# ---------------------------------------------------------------------------
# Casos fijos
# ---------------------------------------------------------------------------
def caso_aceptar():
    public, witness = issue_demo_ticket()
    run_validation(public, witness, build_context(public),
                   label="CASO 1: boleto VALIDO -> debe ACEPTAR")


def caso_rechazo_secreto():
    """Witness con secret+1: el tag ya no coincide."""
    public, _ = issue_demo_ticket()
    bad_witness = TicketWitness(DEMO_SECRET + 1)
    run_validation(public, bad_witness, build_context(public),
                   label="CASO 2: secreto INCORRECTO (secret+1) -> debe RECHAZAR")


def caso_rechazo_vigencia():
    """Vigencia fuera de rango 1-10. Se recalcula el tag para aislar la causa:
    aunque el tag coincida, la restriccion de rango r3 debe rechazar."""
    secret = DEMO_SECRET
    public = TicketPublic(
        ticket_id=DEMO_TICKET_ID,
        attraction_code=DEMO_ATTRACTION,
        issue_day=DEMO_ISSUE_DAY,
        validity_days=11,  # fuera de rango
        public_tag=ticket_tag(secret, DEMO_TICKET_ID, DEMO_ATTRACTION,
                              DEMO_ISSUE_DAY, 11),
        public_key=public_key(secret),
    )
    run_validation(public, TicketWitness(secret), build_context(public),
                   label="CASO 3: vigencia FUERA DE RANGO (11 dias) -> debe RECHAZAR")


def caso_rechazo_prueba_alterada():
    """Prueba valida pero con response alterado (+1)."""
    public, witness = issue_demo_ticket()
    context = build_context(public)
    print("\n--- CASO 4: prueba ALTERADA (response+1) -> debe RECHAZAR ---")
    print(f"Ticket publico : {public.ticket_id}")

    circuit_ok = validate_circuit(public, witness)
    print(f"\n1. Circuito aritmetico valido: {circuit_ok}")

    proof = prove(witness.secret, public.public_key, context)
    tampered = type(proof)(proof.commitment, proof.challenge, proof.response + 1)
    proof_ok = verify(public.public_key, context, tampered)
    print(f"2. Prueba Schnorr valida (alterada): {proof_ok}")
    print(f"\nResultado: {'ACEPTAR' if (circuit_ok and proof_ok) else 'RECHAZAR'}")


def caso_rechazo_contexto():
    """Prueba valida para un contexto, verificada en otro contexto."""
    public, witness = issue_demo_ticket()
    context = build_context(public)
    other_context = context + "|day=999"
    print("\n--- CASO 5: contexto ALTERADO -> debe RECHAZAR ---")
    print(f"Contexto original : {context}")
    print(f"Contexto alterado : {other_context}")

    proof = prove(witness.secret, public.public_key, context)
    proof_ok = verify(public.public_key, other_context, proof)
    print(f"\n1. Circuito aritmetico valido: {validate_circuit(public, witness)}")
    print(f"2. Prueba Schnorr con otro contexto: {proof_ok}")
    print(f"\nResultado: {'ACEPTAR' if proof_ok else 'RECHAZAR'}")


# ---------------------------------------------------------------------------
# Modo interactivo con inputs
# ---------------------------------------------------------------------------
def pedir_entero(mensaje, minimo, maximo, defecto):
    while True:
        raw = input(f"{mensaje} [{defecto}]: ").strip()
        if raw == "":
            return defecto
        try:
            valor = int(raw)
        except ValueError:
            print("  Ingrese un numero entero.")
            continue
        if not (minimo <= valor <= maximo):
            print(f"  Debe estar entre {minimo} y {maximo}.")
            continue
        return valor


def modo_interactivo():
    print("\n=== MODO INTERACTIVO ===")
    print("Ingrese los datos del boleto (Enter = valor por defecto).")
    ticket_id = pedir_entero("ticket_id (1-99999999)", 1, 99999999, DEMO_TICKET_ID)
    attraction = pedir_entero("attraction_code (1-99)", 1, 99, DEMO_ATTRACTION)
    issue_day = pedir_entero("issue_day, dia del anio (1-365)", 1, 365, DEMO_ISSUE_DAY)
    validity = pedir_entero("validity_days (1-10)", 1, 10, DEMO_VALIDITY)
    secret = pedir_entero("secret del titular (1-2000000)", 1, 2000000, DEMO_SECRET)

    public = TicketPublic(
        ticket_id=ticket_id,
        attraction_code=attraction,
        issue_day=issue_day,
        validity_days=validity,
        public_tag=ticket_tag(secret, ticket_id, attraction, issue_day, validity),
        public_key=public_key(secret),
    )
    run_validation(public, TicketWitness(secret), build_context(public),
                   label="BOLETO INGRESADO POR USUARIO")


def menu():
    opciones = {
        "1": ("Boleto valido -> ACEPTAR (datos fijos)", caso_aceptar),
        "2": ("Secreto incorrecto -> RECHAZAR (datos fijos)", caso_rechazo_secreto),
        "3": ("Vigencia fuera de rango -> RECHAZAR (datos fijos)", caso_rechazo_vigencia),
        "4": ("Prueba alterada -> RECHAZAR (datos fijos)", caso_rechazo_prueba_alterada),
        "5": ("Contexto alterado -> RECHAZAR (datos fijos)", caso_rechazo_contexto),
        "6": ("Modo interactivo (ingresar datos por teclado)", modo_interactivo),
        "0": ("Salir", None),
    }
    while True:
        print("\n===============================================")
        print(" PROTOTIPO EDUCATIVO ZK - VALIDACION DE BOLETOS")
        print("===============================================")
        for key in ["1", "2", "3", "4", "5", "6", "0"]:
            print(f"  {key}. {opciones[key][0]}")
        try:
            eleccion = input("\nElija una opcion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo.")
            break
        if eleccion == "0":
            print("Saliendo.")
            break
        accion = opciones.get(eleccion)
        if accion is None:
            print("Opcion invalida. Intente de nuevo.")
            continue
        try:
            accion[1]()
        except (EOFError, KeyboardInterrupt):
            print("\nOperacion cancelada. Volviendo al menu.")
            continue
        input("\nPresione Enter para volver al menu...")


if __name__ == "__main__":
    menu()
