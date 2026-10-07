# Ejemplo manual

Se usa:
- ticket_id = 20260081
- attraction_code = 1
- issue_day = 280
- validity_days = 10
- secret = 73129

La etiqueta pública se calcula como:

tag = secret + 7*ticket_id + 11*attraction_code + 13*issue_day + 17*validity_days (mod p)

El verificador conoce `ticket_id`, `attraction_code`, `issue_day`, `validity_days`,
`tag` y la clave pública `h = g^secret mod p`, pero no recibe `secret`.

La prueba Schnorr demuestra conocimiento del secreto asociado a `h`.
