#!/usr/bin/env python3
"""Mete los 25 correos de demo en el Gmail de demo (los envía desde esa misma cuenta a sí misma,
con el remitente ficticio en «Reply-To» y en el cuerpo). Lo ejecuta Alberto una vez.

Uso:
  GMAIL_DEMO=clinica.demo@gmail.com GMAIL_APP_PASSWORD=xxxx python3 enviar-correos-demo.py

La contraseña es una «contraseña de aplicación» de Google (Cuenta → Seguridad → Verificación en dos pasos →
Contraseñas de aplicaciones). Sin dependencias: solo la librería estándar de Python.
"""
import os, re, smtplib, ssl, sys, time, pathlib
from email.message import EmailMessage

usuario = os.environ.get("GMAIL_DEMO"); clave = os.environ.get("GMAIL_APP_PASSWORD")
if not usuario or not clave:
    sys.exit("Faltan GMAIL_DEMO y GMAIL_APP_PASSWORD en el entorno.")

tabla = (pathlib.Path(__file__).parent / "correos-demo.md").read_text(encoding="utf8")
filas = [l for l in tabla.splitlines() if re.match(r"^\| \d+ \|", l)]
correos = []
for l in filas:
    c = [x.strip() for x in l.strip("|").split("|")]
    n, de, asunto, cuerpo, tipo = c[0], c[1], c[2], c[3], c[4]
    m = re.match(r"(.*?)\s*<(.+?)>", de)
    nombre, direccion = (m.group(1).strip(), m.group(2).strip()) if m else (de, "demo@ejemplo.es")
    correos.append((int(n), nombre, direccion, asunto, cuerpo, tipo))

ctx = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as s:
    s.login(usuario, clave)
    for n, nombre, direccion, asunto, cuerpo, tipo in correos:
        msg = EmailMessage()
        msg["From"] = f"{nombre} <{usuario}>"   # Gmail obliga a que el From sea la propia cuenta
        msg["Reply-To"] = f"{nombre} <{direccion}>"
        msg["To"] = usuario
        msg["Subject"] = asunto
        msg.set_content(f"{cuerpo}\n\n--\n{nombre}\n{direccion}")
        s.send_message(msg)
        print(f"{n:02d} {tipo:12s} {asunto}")
        time.sleep(1.5)
print("Listo:", len(correos), "correos en", usuario)
