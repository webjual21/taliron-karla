#!/usr/bin/env python3
"""Genera los datos ficticios del kit de demo de Karla:
   - 20 facturas PDF de proveedores (gestoría) + 6 facturas de proveedores (restaurante)
   - fotos realistas con Gemini (Nano Banana) para Instagram / piso / carta
Se ejecuta desde el Mac de Alberto (usa Chrome headless y la clave google-ai-api-key del llavero).
Karla NO necesita ejecutarlo: los archivos ya vienen generados en el repo."""
import os, random, subprocess, json, base64, sys, urllib.request, datetime, pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
random.seed(2026)

def html_a_pdf(html, destino):
    tmp = destino.with_suffix(".html")
    tmp.write_text(html, encoding="utf8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={destino}", f"file://{tmp}"], capture_output=True)
    tmp.unlink(missing_ok=True)

def factura_html(emisor, cif, direccion, cliente, cliente_cif, cliente_dir, numero, fecha, lineas, iva=21):
    base = sum(c * p for _, c, p in lineas)
    cuota = round(base * iva / 100, 2)
    filas = "".join(f"<tr><td>{d}</td><td style='text-align:right'>{c}</td><td style='text-align:right'>{p:,.2f} €</td><td style='text-align:right'>{c*p:,.2f} €</td></tr>" for d, c, p in lineas)
    return f"""<html><head><meta charset='utf-8'><style>
    body{{font-family:Helvetica,Arial;color:#222;margin:40px;font-size:13px}} h1{{font-size:26px;margin:0 0 4px;letter-spacing:1px}}
    .cab{{display:flex;justify-content:space-between;border-bottom:2px solid #333;padding-bottom:14px;margin-bottom:18px}}
    table{{width:100%;border-collapse:collapse;margin-top:18px}} th{{text-align:left;background:#f0f0f0;padding:8px;font-size:12px}} td{{padding:8px;border-bottom:1px solid #ddd}}
    .tot{{margin-top:18px;margin-left:auto;width:260px}} .tot div{{display:flex;justify-content:space-between;padding:4px 0}} .tot .g{{font-weight:bold;font-size:16px;border-top:2px solid #333;padding-top:8px}}
    .peq{{color:#666;font-size:11px;margin-top:30px}}</style></head><body>
    <div class='cab'><div><h1>{emisor}</h1><div>{direccion}</div><div>CIF {cif}</div></div>
    <div style='text-align:right'><div style='font-size:20px;font-weight:bold'>FACTURA {numero}</div><div>Fecha: {fecha}</div><div>Vencimiento: 30 días</div></div></div>
    <div><b>Cliente:</b> {cliente}<br>{cliente_dir}<br>CIF {cliente_cif}</div>
    <table><tr><th>Concepto</th><th style='text-align:right'>Cant.</th><th style='text-align:right'>Precio</th><th style='text-align:right'>Importe</th></tr>{filas}</table>
    <div class='tot'><div><span>Base imponible</span><span>{base:,.2f} €</span></div><div><span>IVA {iva} %</span><span>{cuota:,.2f} €</span></div><div class='g'><span>TOTAL</span><span>{base+cuota:,.2f} €</span></div></div>
    <div class='peq'>Forma de pago: transferencia a ES12 0049 0001 5000 0000 {random.randint(1000,9999)}. Documento de ejemplo para demostraciones. Datos ficticios.</div>
    </body></html>"""

PROVEEDORES_TALLER = [
    ("Recambios Levante SL", "B46781234", "Pol. Ind. Fuente del Jarro, nave 12, 46988 Paterna (Valencia)", [("Pastillas de freno delanteras", 8, 34.50), ("Filtro de aceite", 20, 6.90), ("Aceite motor 5W30 5 L", 12, 38.00)]),
    ("Neumáticos Turia SA", "A46009876", "Av. del Puerto 145, 46023 Valencia", [("Neumático 205/55 R16", 8, 72.00), ("Montaje y equilibrado", 8, 12.00)]),
    ("Iberdrola Clientes SAU", "A95758389", "Plaza Euskadi 5, 48009 Bilbao", [("Suministro eléctrico", 1, 412.37)]),
    ("Telefónica de España SAU", "A82018474", "Gran Vía 28, 28013 Madrid", [("Fibra + móvil empresa", 1, 64.90)]),
    ("Pinturas Mediterráneo SL", "B96123456", "C/ Industria 8, 46540 El Puig", [("Pintura bicapa 1 L", 6, 41.20), ("Masilla poliéster 2 kg", 4, 18.75), ("Lija grano 400 (50 uds)", 2, 22.00)]),
    ("Herramientas Profesionales Vidal SL", "B46445566", "C/ Alboraya 22, 46010 Valencia", [("Llave dinamométrica 1/2", 1, 89.00), ("Juego de vasos 94 pzs", 1, 129.90)]),
    ("Limpiezas Sol y Mar SL", "B46778899", "C/ Colón 60, 46004 Valencia", [("Limpieza mensual nave", 1, 380.00)]),
    ("Gasóleos Express SL", "B46990011", "Ctra. Barcelona km 7, 46130 Massamagrell", [("Gasóleo A (litros)", 600, 1.42)]),
    ("Seguros Mapfre SA", "A28141935", "Ctra. Pozuelo 52, 28222 Majadahonda", [("Seguro responsabilidad civil taller (trimestre)", 1, 295.00)]),
    ("Amazon Business EU SARL", "W0184081H", "38 Av. John F. Kennedy, L-1855 Luxemburgo", [("Compresor de aire 50 L", 1, 219.00), ("Foco LED taller", 4, 27.50)]),
]
PROVEEDORES_RESTAURANTE = [
    ("Pescados Guadalquivir SL", "B41123456", "Mercado de Abastos puesto 14, 41001 Sevilla", [("Lubina salvaje (kg)", 12, 21.50), ("Gamba blanca Huelva (kg)", 6, 38.00)]),
    ("Carnes de Sierra Morena SA", "A41009988", "Pol. Store nave 7, 41008 Sevilla", [("Presa ibérica (kg)", 15, 19.80), ("Secreto ibérico (kg)", 10, 16.40)]),
    ("Frutas y Verduras Triana SL", "B41556677", "Mercado de Triana puesto 3, 41010 Sevilla", [("Tomate rosa (kg)", 30, 3.20), ("Patata (kg)", 60, 0.95), ("Pimiento (kg)", 20, 2.40)]),
    ("Bodegas del Sur Distribución SL", "B41778899", "C/ Betis 40, 41010 Sevilla", [("Vino tinto crianza (caja 6)", 10, 54.00), ("Cerveza barril 30 L", 6, 78.00)]),
    ("Endesa Energía SAU", "A81948077", "C/ Ribera del Loira 60, 28042 Madrid", [("Suministro eléctrico", 1, 687.15)]),
    ("Lavandería Industrial Hispalis SL", "B41334455", "C/ Torneo 88, 41002 Sevilla", [("Lavado mantelería (semana)", 4, 62.00)]),
]

def facturas(carpeta, cliente, cliente_cif, cliente_dir, proveedores, n, prefijo):
    carpeta.mkdir(parents=True, exist_ok=True)
    inicio = datetime.date(2026, 7, 1)
    for i in range(n):
        emisor, cif, dire, lineas = proveedores[i % len(proveedores)]
        fecha = inicio + datetime.timedelta(days=random.randint(0, 85))
        numero = f"{prefijo}-{fecha.year}-{random.randint(100, 999)}"
        lineas_v = [(d, max(1, int(c * random.uniform(0.6, 1.4))) if c > 1 else c, round(p * random.uniform(0.95, 1.05), 2)) for d, c, p in lineas]
        nombre = f"{i+1:02d}-{emisor.split()[0].lower()}-{fecha.strftime('%Y-%m-%d')}.pdf"
        html_a_pdf(factura_html(emisor, cif, dire, cliente, cliente_cif, cliente_dir, numero, fecha.strftime('%d/%m/%Y'), lineas_v), carpeta / nombre)
    print("facturas", carpeta, n)

def imagen_gemini(prompt, destino):
    try:
        key = subprocess.run(["security", "find-generic-password", "-s", "google-ai-api-key", "-w"], capture_output=True, text=True).stdout.strip()
        if not key: raise RuntimeError("sin clave google-ai-api-key")
        cuerpo = json.dumps({"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseModalities": ["IMAGE"]}}).encode()
        req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={key}", data=cuerpo, headers={"Content-Type": "application/json"})
        r = json.load(urllib.request.urlopen(req, timeout=120))
        for p in r["candidates"][0]["content"]["parts"]:
            if "inlineData" in p:
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_bytes(base64.b64decode(p["inlineData"]["data"]))
                print("foto", destino.name); return True
        print("sin imagen en la respuesta", destino.name); return False
    except Exception as e:
        print("foto FALLO", destino.name, str(e)[:200]); return False

FOTOS = {
    "clinica-dental/fotos/recepcion.jpg": "Photorealistic photo of the reception of a modern small dental clinic in Madrid, Spain: white counter, soft warm lighting, a green plant, clean minimal design, morning light through the window, no people. Photographic realism, no text.",
    "clinica-dental/fotos/gabinete.jpg": "Photorealistic photo of a bright modern dental treatment room: dental chair, overhead lamp, white and light wood finishes, instruments neatly arranged, no people. Photographic realism, no text.",
    "clinica-dental/fotos/paciente-sonrisa.jpg": "Photorealistic candid photo of a Spanish woman in her 30s smiling naturally after a dental cleaning, sitting in a dental chair, dentist in blue scrubs blurred in the background, natural light. Photographic realism, no text.",
    "clinica-dental/fotos/equipo.jpg": "Photorealistic photo of a small dental team of three (two women, one man, Spanish, 30-45 years old) in light blue scrubs standing in a modern clinic corridor, friendly natural smiles. Photographic realism, no text.",
    "restaurante/fotos/presa-iberica.jpg": "Photorealistic food photo: grilled Iberian pork presa sliced, pink center, with roasted potatoes and rosemary, on a dark ceramic plate, rustic wooden table, warm restaurant light. Photographic realism, no text.",
    "restaurante/fotos/sala.jpg": "Photorealistic photo of a cozy Andalusian grill restaurant dining room in Seville at dusk: exposed brick, wooden tables set with wine glasses, warm pendant lights, empty, inviting. Photographic realism, no text.",
    "restaurante/fotos/terraza.jpg": "Photorealistic photo of a small restaurant terrace on a narrow street in Seville, Spain, orange trees, tables with checkered napkins, golden hour, no people. Photographic realism, no text.",
    "inmobiliaria/piso-calle-mayor/fotos/salon.jpg": "Photorealistic real estate photo of a renovated apartment living room in central Madrid: 85 square meters flat, tall windows with wooden shutters, herringbone parquet, white walls, grey sofa, daylight. Photographic realism, no text.",
    "inmobiliaria/piso-calle-mayor/fotos/cocina.jpg": "Photorealistic real estate photo of a modern white kitchen with island in a renovated Madrid apartment, quartz countertop, integrated appliances, window with street view. Photographic realism, no text.",
    "inmobiliaria/piso-calle-mayor/fotos/dormitorio.jpg": "Photorealistic real estate photo of a bright double bedroom in a renovated Madrid apartment, wooden floor, built-in wardrobe, balcony door with light curtains. Photographic realism, no text.",
    "gimnasio/fotos/sala.jpg": "Photorealistic photo of a mid-size neighbourhood gym in Spain: rows of dumbbells, rubber floor, large mirrors, morning light, no people. Photographic realism, no text.",
    "peluqueria/fotos/salon.jpg": "Photorealistic photo of a small stylish hair salon in Spain: two styling chairs, round mirrors with warm bulbs, plants, pastel tones, no people. Photographic realism, no text.",
}

if __name__ == "__main__":
    demo = RAIZ / "demo"
    if "sin-facturas" not in sys.argv:
        facturas(demo / "gestoria" / "facturas-talleres-vidal", "Talleres Mecánicos Vidal SL", "B46112233", "C/ Mislata 14, 46014 Valencia", PROVEEDORES_TALLER, 20, "F")
        facturas(demo / "restaurante" / "facturas-proveedores", "La Brasa de Ana SL", "B41667788", "C/ Pureza 22, 41010 Sevilla", PROVEEDORES_RESTAURANTE, 6, "R")
    if "sin-fotos" not in sys.argv:
        for rel, prompt in FOTOS.items():
            destino = demo / rel
            if not destino.exists(): imagen_gemini(prompt, destino)
