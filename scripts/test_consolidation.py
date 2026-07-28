#!/usr/bin/env python3
"""
Script de prueba para la consolidación de extracciones
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from consolidate_extractions import ExtractionConsolidator

def test_consolidation():
    """Probar la consolidación de extracciones"""
    try:
        print("🧪 INICIANDO PRUEBA DE CONSOLIDACIÓN")
        print("="*50)
        
        # Crear consolidador
        consolidator = ExtractionConsolidator()
        
        # Obtener extracciones
        extractions = consolidator.get_all_extractions()
        
        if not extractions:
            print("⚠️ No se encontraron extracciones para probar")
            return
        
        print(f"📊 Se encontraron {len(extractions)} extracciones")
        
        # Mostrar estructura de la primera extracción
        if extractions:
            first_extraction = extractions[0]
            print(f"\n🔍 Estructura de la primera extracción:")
            print(f"   ID: {first_extraction.get('id', 'N/A')}")
            print(f"   Job ID: {first_extraction.get('job_id', 'N/A')}")
            print(f"   Processing Mode: {first_extraction.get('processing_mode', 'N/A')}")
            print(f"   Created At: {first_extraction.get('created_at', 'N/A')}")
            
            extraction_data = first_extraction.get('extraction_data', [])
            print(f"   Fields Count: {len(extraction_data)}")
            
            # Mostrar algunos campos
            for i, field in enumerate(extraction_data[:5]):  # Solo los primeros 5
                print(f"   Field {i+1}: {field.get('name', 'N/A')} = {field.get('value', 'N/A')[:50]}...")
        
        # Consolidar datos
        df_main = consolidator.consolidate_extractions(extractions)
        
        if not df_main.empty:
            print(f"\n📋 DataFrame principal creado:")
            print(f"   Filas: {df_main.shape[0]}")
            print(f"   Columnas: {df_main.shape[1]}")
            
            # Mostrar columnas disponibles
            value_columns = [col for col in df_main.columns if col.endswith('_value')]
            print(f"   Campos extraídos: {len(value_columns)}")
            print(f"   Primeros 10 campos: {value_columns[:10]}")
        
        # Extraer arrays
        df_arrays = consolidator.extract_array_fields(extractions)
        
        if not df_arrays.empty:
            print(f"\n📦 DataFrame de arrays creado:")
            print(f"   Filas: {df_arrays.shape[0]}")
            print(f"   Columnas: {df_arrays.shape[1]}")
            
            # Mostrar campos con arrays
            array_fields = df_arrays['field_name'].unique()
            print(f"   Campos con arrays: {list(array_fields)}")
        
        # Generar reporte
        consolidator.generate_summary_report(df_main, df_arrays)
        
        print("\n✅ PRUEBA COMPLETADA EXITOSAMENTE")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_consolidation()
