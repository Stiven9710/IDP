#!/usr/bin/env python3
"""
Script de debugging para investigar el parsing de productos
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from consolidate_extractions import ExtractionConsolidator

def debug_products_parsing():
    """Debuggear el parsing de productos"""
    try:
        print("🔍 DEBUGGING PARSING DE PRODUCTOS")
        print("="*50)
        
        # Crear consolidador
        consolidator = ExtractionConsolidator()
        
        # Obtener extracciones
        extractions = consolidator.get_all_extractions()
        
        if not extractions:
            print("⚠️ No se encontraron extracciones")
            return
        
        print(f"📊 Total extracciones: {len(extractions)}")
        
        # Analizar las primeras 5 extracciones
        for i, extraction in enumerate(extractions[:5]):
            print(f"\n🔍 EXTRACCIÓN {i+1}:")
            print(f"   ID: {extraction.get('id', 'N/A')}")
            print(f"   Job ID: {extraction.get('job_id', 'N/A')}")
            
            # Buscar campo items_de_linea
            extraction_data = extraction.get('extraction_data', [])
            items_field = None
            
            for field in extraction_data:
                field_name = field.get('name', '').lower()
                if 'items' in field_name or 'linea' in field_name:
                    items_field = field
                    break
            
            if items_field:
                print(f"   ✅ Campo items encontrado: {items_field.get('name', 'N/A')}")
                print(f"   📝 Valor: {items_field.get('value', 'N/A')[:100]}...")
                
                # Intentar parsear
                try:
                    items_value = items_field.get('value', '')
                    if items_value.startswith('['):
                        items_list = json.loads(items_value)
                        print(f"   ✅ JSON parseado exitosamente: {len(items_list)} items")
                        
                        # Mostrar primeros items
                        for j, item in enumerate(items_list[:3]):
                            print(f"      Item {j+1}: {item}")
                    else:
                        print(f"   ⚠️ Valor no es un array JSON")
                except json.JSONDecodeError as e:
                    print(f"   ❌ Error parseando JSON: {e}")
            else:
                print(f"   ⚠️ No se encontró campo items_de_linea")
                
                # Mostrar todos los campos disponibles
                print(f"   📋 Campos disponibles:")
                for field in extraction_data:
                    field_name = field.get('name', 'N/A')
                    field_value = field.get('value', 'N/A')
                    print(f"      • {field_name}: {str(field_value)[:50]}...")
        
        # Buscar patrones en los nombres de campos
        print(f"\n🔍 ANÁLISIS DE NOMBRES DE CAMPOS:")
        all_field_names = []
        for extraction in extractions:
            extraction_data = extraction.get('extraction_data', [])
            for field in extraction_data:
                field_name = field.get('name', '')
                all_field_names.append(field_name)
        
        # Contar frecuencia de nombres
        field_counts = pd.Series(all_field_names).value_counts()
        print(f"   📊 Campos más comunes:")
        for field_name, count in field_counts.head(10).items():
            print(f"      • {field_name}: {count} veces")
        
        # Buscar campos que contengan "items" o "linea"
        items_fields = [name for name in all_field_names if 'items' in name.lower() or 'linea' in name.lower()]
        print(f"\n🔍 CAMPOS CON 'items' O 'linea':")
        for field_name in items_fields:
            print(f"   • {field_name}")
        
    except Exception as e:
        print(f"❌ Error en debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_products_parsing()
