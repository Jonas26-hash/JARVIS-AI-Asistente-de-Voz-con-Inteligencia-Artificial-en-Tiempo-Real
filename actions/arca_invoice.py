"""arca_invoice.py — Generate Argentine electronic invoices (ARCA/AFIP)."""
from __future__ import annotations
import json, os
from pathlib import Path
from datetime import datetime

_INVOICES_DIR = Path(__file__).resolve().parent.parent / "memory" / "invoices"


def arca_invoice(parameters=None, player=None, **kwargs):
    if parameters is None:
        parameters = {}
    action = parameters.get("action", "listar")

    _INVOICES_DIR.mkdir(parents=True, exist_ok=True)

    tipo_map = {1: "Factura A", 5: "Factura C", 6: "Factura B", 3: "NC A", 8: "NC B"}

    if action == "listar":
        return ("Tipos de comprobante:\n"
                "  1 = Factura A (responsable inscripto)\n"
                "  5 = Factura C (monotributo)\n"
                "  6 = Factura B (consumidor final)\n"
                "  3 = Nota de Crédito A\n"
                "  8 = Nota de Crédito B\n\n"
                "Usá action='generar' con tipo, razon_social, cuit_receptor y detalle.")

    elif action == "generar":
        tipo = parameters.get("tipo", 5)
        razon_social = parameters.get("razon_social", "Consumidor Final")
        cuit_receptor = parameters.get("cuit_receptor", "0")
        domicilio = parameters.get("domicilio", "")
        detalle = parameters.get("detalle", [])
        importe_neto = parameters.get("importe_neto", 0)
        iva_pct = parameters.get("iva_pct", 21.0)
        fecha = parameters.get("fecha", datetime.now().strftime("%Y-%m-%d"))

        if not detalle and not importe_neto:
            return "Falta detalle (productos) o importe_neto."

        if not detalle and importe_neto:
            detalle = [{"descripcion": "Producto/Servicio", "precio": importe_neto, "cantidad": 1}]

        neto = sum(d.get("precio", 0) * d.get("cantidad", 1) for d in detalle)
        iva = neto * (iva_pct / 100)
        total = neto + iva

        invoice = {
            "tipo": tipo,
            "tipo_desc": tipo_map.get(tipo, f"Tipo {tipo}"),
            "razon_social": razon_social,
            "cuit_receptor": cuit_receptor,
            "domicilio": domicilio,
            "fecha": fecha,
            "detalle": detalle,
            "importe_neto": round(neto, 2),
            "iva_pct": iva_pct,
            "iva": round(iva, 2),
            "total": round(total, 2),
            "generado": datetime.now().isoformat(),
            "cae": "0"  # Simulado offline
        }

        fname = f"factura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        fpath = _INVOICES_DIR / fname
        fpath.write_text(json.dumps(invoice, indent=2, ensure_ascii=False), encoding="utf-8")

        msg = (f"Comprobante generado: {tipo_map.get(tipo, '?')}\n"
               f"Receptor: {razon_social}\n"
               f"Neto: ${neto:.2f}\n"
               f"IVA ({iva_pct}%): ${iva:.2f}\n"
               f"Total: ${total:.2f}\n"
               f"Archivo: {fpath}\n\n"
               f"⚠️  Comprobante offline (sin CAE). Para facturación oficial con ARCA, "
               f"configurá certificado digital en config/arca_cert.p12")
        return msg

    elif action == "historial":
        files = list(_INVOICES_DIR.glob("*.json"))
        if not files:
            return "No hay comprobantes generados."
        entries = []
        for f in sorted(files, reverse=True)[:10]:
            data = json.loads(f.read_text())
            entries.append(f"  - {data['fecha']}: {data['tipo_desc']} - ${data['total']:.2f} ({data['razon_social']})")
        return "Historial de comprobantes:\n" + "\n".join(entries)

    return f"ARCA action '{action}' completado."
