# Prototipo — Circuitos aritméticos y pruebas educativas de conocimiento cero

## Propósito
Prototipo inicial para la Entrega 1 del proyecto semestral de Algoritmos Avanzados.

## Estructura
- `main.py`: demostración de extremo a extremo.
- `circuit.py`: modelo de circuito aritmético y restricciones educativas.
- `zk_schnorr.py`: prueba de conocimiento tipo Schnorr.
- `tests/test_prototype.py`: pruebas automatizadas.
- `requirements.txt`: dependencias.

## Requisitos
Python 3.10+ recomendado. No requiere paquetes externos.

## Ejecutar
```bash
python main.py
python -m unittest discover -s tests -v
```

## Alcance y advertencia
Es un prototipo académico. Los parámetros criptográficos son deliberadamente pequeños y la
etiqueta algebraica no es un hash criptográfico. No debe usarse para boletos reales ni para
proteger información real.

La arquitectura separa:
1. validación algebraica de la instancia;
2. prueba de conocimiento del secreto;
3. verificación pública sin imprimir el secreto.

Una evolución posterior puede reemplazar este protocolo educativo por un circuito R1CS real
compilado con Circom y un sistema zk-SNARK, manteniendo la misma lógica funcional.
