#!/usr/bin/env python3
"""
Script de prueba para el sistema IDP con configuración personalizada
Demuestra cómo enviar diferentes configuraciones de campos en la petición HTTP
"""

import json
import requests
import base64
from typing import Dict, List, Any

def test_factura_colombiana():
    """Configuración para factura colombiana"""
    return {
        "fields": [
            {
                "name": "numero_factura",
                "type": "string",
                "description": "El identificador único de la factura. Busca en frases que contengan 'Factura' o 'Invoice Number'"
            },
            {
                "name": "fecha_factura",
                "type": "date",
                "description": "La fecha de emisión de la factura. Busca invoice date en la parte superior del documento y formatéala como YYYY-MM-DD"
            },
            {
                "name": "proveedor_nombre",
                "type": "string",
                "description": "El nombre completo de la empresa o persona que emite la factura. Busca en la parte superior izquierda del documento"
            },
            {
                "name": "cliente_nombre",
                "type": "string",
                "description": "El nombre de la empresa o persona a quien se factura. Busca en la parte superior derecha del documento"
            },
            {
                "name": "total_a_pagar",
                "type": "number",
                "description": "El valor final y total de la factura después de todos los impuestos. Es el monto más grande y destacado en la sección de totales o el Total Amount"
            },
            {
                "name": "items_de_linea",
                "type": "array",
                "description": "Extrae todos los productos o servicios listados en la tabla de la factura. Cada línea debe ser un objeto JSON separado dentro de este array, con las claves: 'descripcion' y 'total_linea'"
            },
            {
                "name": "condiciones_pago",
                "type": "string",
                "description": "Las condiciones de pago especificadas en la factura. Por ejemplo: '30 días', 'contado', etc."
            },
            {
                "name": "moneda",
                "type": "string",
                "description": "La moneda en la que está expresada la factura. Por ejemplo: 'COP', 'USD', 'EUR'"
            },
            {
                "name": "observaciones",
                "type": "string",
                "description": "Cualquier observación o nota adicional que aparezca en la factura"
            }
        ],
        "prompt": "Actúa como un analista financiero experto especializado en facturas colombianas. Analiza la siguiente factura de un proveedor y extrae los campos detallados a continuación de forma precisa.",
        "processing_mode": "gpt_vision_only"
    }

def test_cedula_colombiana():
    """Configuración para cédula colombiana"""
    return {
        "fields": [
            {
                "name": "numero_cedula",
                "type": "string",
                "description": "Número de identificación de la cédula"
            },
            {
                "name": "nombres",
                "type": "string",
                "description": "Nombres completos de la persona"
            },
            {
                "name": "apellidos",
                "type": "string",
                "description": "Apellidos completos de la persona"
            },
            {
                "name": "fecha_nacimiento",
                "type": "date",
                "description": "Fecha de nacimiento en formato YYYY-MM-DD"
            },
            {
                "name": "lugar_nacimiento",
                "type": "string",
                "description": "Ciudad y departamento de nacimiento"
            },
            {
                "name": "fecha_expedicion",
                "type": "date",
                "description": "Fecha de expedición del documento en formato YYYY-MM-DD"
            },
            {
                "name": "lugar_expedicion",
                "type": "string",
                "description": "Ciudad y departamento de expedición"
            },
            {
                "name": "estado",
                "type": "string",
                "description": "Estado del documento (vigente, vencida, etc.)"
            }
        ],
        "prompt": "Actúa como un analista de documentos de identidad. Analiza la siguiente cédula colombiana y extrae la información solicitada de forma precisa.",
        "processing_mode": "gpt_vision_only"
    }

def test_recibo_servicios():
    """Configuración para recibo de servicios públicos"""
    return {
        "fields": [
            {
                "name": "numero_recibo",
                "type": "string",
                "description": "Número de recibo o factura"
            },
            {
                "name": "empresa_servicio",
                "type": "string",
                "description": "Nombre de la empresa que presta el servicio"
            },
            {
                "name": "tipo_servicio",
                "type": "string",
                "description": "Tipo de servicio (energía, agua, gas, internet, etc.)"
            },
            {
                "name": "cliente_nombre",
                "type": "string",
                "description": "Nombre del cliente o titular del servicio"
            },
            {
                "name": "direccion_servicio",
                "type": "string",
                "description": "Dirección donde se presta el servicio"
            },
            {
                "name": "periodo_facturacion",
                "type": "string",
                "description": "Período de facturación (ej: Enero 2025)"
            },
            {
                "name": "consumo_actual",
                "type": "number",
                "description": "Consumo actual del período"
            },
            {
                "name": "total_a_pagar",
                "type": "number",
                "description": "Total a pagar por el servicio"
            },
            {
                "name": "fecha_vencimiento",
                "type": "date",
                "description": "Fecha límite de pago en formato YYYY-MM-DD"
            }
        ],
        "prompt": "Actúa como un analista de servicios públicos. Analiza el siguiente recibo y extrae la información solicitada de forma precisa.",
        "processing_mode": "gpt_vision_only"
    }

def mostrar_configuracion(config: Dict[str, Any]):
    """Mostrar la configuración de campos de forma legible"""
    print(f"\n📋 CONFIGURACIÓN:")
    print(f"🎯 Modo: {config['processing_mode']}")
    print(f"📝 Prompt: {config['prompt'][:100]}...")
    print(f"🔢 Total de campos: {len(config['fields'])}")
    
    print("\n📊 CAMPOS A EXTRAER:")
    for i, field in enumerate(config['fields'], 1):
        print(f"  {i}. {field['name']} ({field['type']})")
        print(f"     Descripción: {field['description']}")
        print()

def generar_comando_curl(config: Dict[str, Any], nombre_test: str):
    """Generar comando curl para probar el endpoint"""
    fields_json = json.dumps(config['fields'])
    prompt = config['prompt']
    mode = config['processing_mode']
    
    print(f"\n🔧 COMANDO CURL PARA {nombre_test.upper()}:")
    print("curl -X POST 'http://159.203.149.247:8000/api/v1/documents/process-upload' \\")
    print(f"  -F 'file=@tests/Documentos/Invoice_2082463105.pdf' \\")
    print(f"  -F 'fields_config={fields_json}' \\")
    print(f"  -F 'prompt_general={prompt}' \\")
    print(f"  -F 'processing_mode={mode}'")
    
    # También mostrar el comando con escape de caracteres para copiar y pegar
    escaped_fields = fields_json.replace('"', '\\"')
    escaped_prompt = prompt.replace('"', '\\"')
    
    print(f"\n📋 COMANDO LISTO PARA COPIAR:")
    print(f'curl -X POST "http://159.203.149.247:8000/api/v1/documents/process-upload" \\')
    print(f'  -F "file=@tests/Documentos/Invoice_2082463105.pdf" \\')
    print(f'  -F "fields_config={escaped_fields}" \\')
    print(f'  -F "prompt_general={escaped_prompt}" \\')
    print(f'  -F "processing_mode={mode}"')

def main():
    """Función principal que ejecuta todas las pruebas"""
    print("🚀 SISTEMA IDP DINÁMICO - CONFIGURACIONES DE PRUEBA")
    print("=" * 70)
    
    # Lista de configuraciones de prueba
    configuraciones = [
        ("FACTURA COLOMBIANA", test_factura_colombiana()),
        ("CÉDULA COLOMBIANA", test_cedula_colombiana()),
        ("RECIBO DE SERVICIOS", test_recibo_servicios())
    ]
    
    # Mostrar cada configuración y generar comandos curl
    for nombre_test, config in configuraciones:
        print(f"\n{'='*70}")
        print(f"🧾 {nombre_test}")
        mostrar_configuracion(config)
        generar_comando_curl(config, nombre_test)
    
    print(f"\n{'='*70}")
    print("✅ TODAS LAS CONFIGURACIONES GENERADAS")
    print("\n🎯 CARACTERÍSTICAS DEL SISTEMA:")
    print("1. ✅ Completamente dinámico - campos configurables via HTTP")
    print("2. ✅ Soporta cualquier tipo de documento")
    print("3. ✅ Reglas del sistema aplicadas automáticamente")
    print("4. ✅ Validación de JSON en tiempo real")
    print("5. ✅ Campos por defecto si no se especifica configuración")
    print("6. ✅ Logs detallados del proceso")
    
    print("\n🔧 ENDPOINTS DISPONIBLES:")
    print("• POST /process-upload - Con configuración personalizada")
    print("• POST /process-upload-custom - Con configuración personalizada (alternativo)")
    print("• GET /{job_id}/status - Consultar estado")
    print("• GET /{job_id}/result - Obtener resultado")
    
    print("\n💡 USO EN PRODUCCIÓN:")
    print("• Envía la configuración de campos en cada petición")
    print("• No necesitas archivos de configuración locales")
    print("• El sistema se adapta a cualquier tipo de documento")
    print("• Las reglas se aplican según el contexto del prompt")

if __name__ == "__main__":
    main()
