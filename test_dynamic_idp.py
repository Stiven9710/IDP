#!/usr/bin/env python3
"""
Script de prueba para demostrar la flexibilidad del sistema IDP
Permite probar diferentes configuraciones de campos y tipos de documentos
"""

import json
import requests
import base64
from typing import Dict, List, Any

def test_factura_colombiana():
    """Probar con configuración de factura colombiana"""
    print("🧾 === PRUEBA: FACTURA COLOMBIANA ===")
    
    # Configuración para factura colombiana
    fields_config = [
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
    ]
    
    prompt = "Actúa como un analista financiero experto especializado en facturas colombianas. Analiza la siguiente factura de un proveedor y extrae los campos detallados a continuación de forma precisa."
    
    return {
        "fields": fields_config,
        "prompt": prompt,
        "processing_mode": "gpt_vision_only"
    }

def test_cedula_colombiana():
    """Probar con configuración de cédula colombiana"""
    print("🆔 === PRUEBA: CÉDULA COLOMBIANA ===")
    
    fields_config = [
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
    ]
    
    prompt = "Actúa como un analista de documentos de identidad. Analiza la siguiente cédula colombiana y extrae la información solicitada de forma precisa."
    
    return {
        "fields": fields_config,
        "prompt": prompt,
        "processing_mode": "gpt_vision_only"
    }

def test_recibo_servicios():
    """Probar con configuración de recibo de servicios públicos"""
    print("💡 === PRUEBA: RECIBO DE SERVICIOS ===")
    
    fields_config = [
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
            "name": "consumo_anterior",
            "type": "number",
            "description": "Consumo del período anterior"
        },
        {
            "name": "valor_unitario",
            "type": "number",
            "description": "Valor por unidad de consumo"
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
    ]
    
    prompt = "Actúa como un analista de servicios públicos. Analiza el siguiente recibo y extrae la información solicitada de forma precisa."
    
    return {
        "fields": fields_config,
        "prompt": prompt,
        "processing_mode": "gpt_vision_only"
    }

def test_contrato_laboral():
    """Probar con configuración de contrato laboral"""
    print("📋 === PRUEBA: CONTRATO LABORAL ===")
    
    fields_config = [
        {
            "name": "numero_contrato",
            "type": "string",
            "description": "Número de identificación del contrato"
        },
        {
            "name": "tipo_contrato",
            "type": "string",
            "description": "Tipo de contrato (término fijo, término indefinido, obra o labor, etc.)"
        },
        {
            "name": "empleador_nombre",
            "type": "string",
            "description": "Nombre de la empresa empleadora"
        },
        {
            "name": "empleado_nombre",
            "type": "string",
            "description": "Nombre completo del empleado"
        },
        {
            "name": "cargo",
            "type": "string",
            "description": "Cargo o puesto de trabajo"
        },
        {
            "name": "fecha_inicio",
            "type": "date",
            "description": "Fecha de inicio del contrato en formato YYYY-MM-DD"
        },
        {
            "name": "fecha_fin",
            "type": "date",
            "description": "Fecha de terminación del contrato en formato YYYY-MM-DD (si aplica)"
        },
        {
            "name": "salario_base",
            "type": "number",
            "description": "Salario base mensual"
        },
        {
            "name": "jornada_laboral",
            "type": "string",
            "description": "Jornada laboral (tiempo completo, medio tiempo, etc.)"
        },
        {
            "name": "lugar_trabajo",
            "type": "string",
            "description": "Lugar donde se presta el servicio"
        }
    ]
    
    prompt = "Actúa como un analista de recursos humanos. Analiza el siguiente contrato laboral y extrae la información solicitada de forma precisa."
    
    return {
        "fields": fields_config,
        "prompt": prompt,
        "processing_mode": "gpt_vision_only"
    }

def test_documento_generico():
    """Probar con configuración genérica para cualquier documento"""
    print("📄 === PRUEBA: DOCUMENTO GENÉRICO ===")
    
    fields_config = [
        {
            "name": "tipo_documento",
            "type": "string",
            "description": "Tipo de documento identificado"
        },
        {
            "name": "titulo",
            "type": "string",
            "description": "Título o encabezado principal del documento"
        },
        {
            "name": "fecha_documento",
            "type": "date",
            "description": "Fecha del documento si está presente, en formato YYYY-MM-DD"
        },
        {
            "name": "emisor",
            "type": "string",
            "description": "Persona o entidad que emite o crea el documento"
        },
        {
            "name": "destinatario",
            "type": "string",
            "description": "Persona o entidad a quien va dirigido el documento"
        },
        {
            "name": "contenido_principal",
            "type": "string",
            "description": "Contenido principal o resumen del documento"
        },
        {
            "name": "palabras_clave",
            "type": "array",
            "description": "Lista de palabras clave o términos importantes encontrados en el documento"
        },
        {
            "name": "referencias",
            "type": "array",
            "description": "Referencias, números de identificación o códigos mencionados en el documento"
        }
    ]
    
    prompt = "Actúa como un analista de documentos general. Analiza el siguiente documento y extrae la información solicitada de forma precisa, sin importar el tipo de documento."
    
    return {
        "fields": fields_config,
        "prompt": prompt,
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

def main():
    """Función principal que ejecuta todas las pruebas"""
    print("🚀 SISTEMA IDP DINÁMICO - PRUEBAS DE FLEXIBILIDAD")
    print("=" * 60)
    
    # Lista de configuraciones de prueba
    configuraciones = [
        test_factura_colombiana(),
        test_cedula_colombiana(),
        test_recibo_servicios(),
        test_contrato_laboral(),
        test_documento_generico()
    ]
    
    # Mostrar cada configuración
    for i, config in enumerate(configuraciones, 1):
        print(f"\n{'='*60}")
        mostrar_configuracion(config)
        
        # Guardar configuración en archivo temporal para pruebas
        filename = f"test_config_{i}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"💾 Configuración guardada en: {filename}")
    
    print(f"\n{'='*60}")
    print("✅ TODAS LAS CONFIGURACIONES GENERADAS")
    print("\n🎯 USO:")
    print("1. El sistema IDP ahora es completamente dinámico")
    print("2. Puedes cambiar los campos sin modificar el código")
    print("3. Soporta cualquier tipo de documento")
    print("4. Las reglas del sistema se aplican automáticamente")
    print("5. Usa /process-upload para configuración por defecto")
    print("6. Usa /process-upload-custom para configuración personalizada")
    
    print("\n🔧 EJEMPLO DE USO:")
    print("curl -X POST 'http://localhost:8000/api/v1/documents/process-upload-custom' \\")
    print("  -F 'file=@tests/Documentos/Invoice_2082463105.pdf' \\")
    print("  -F 'fields_config=@test_config_1.json' \\")
    print("  -F 'prompt_general=Analiza esta factura colombiana' \\")
    print("  -F 'processing_mode=gpt_vision_only'")

if __name__ == "__main__":
    main()
