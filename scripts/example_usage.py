#!/usr/bin/env python3
"""
Ejemplo de uso de los scripts de consolidación
Muestra cómo obtener y usar los DataFrames como Excel
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from consolidate_extractions import ExtractionConsolidator

def example_usage():
    """Ejemplo de uso de los scripts"""
    try:
        print("📚 EJEMPLO DE USO DE SCRIPTS DE CONSOLIDACIÓN")
        print("="*60)
        
        # Crear consolidador
        consolidator = ExtractionConsolidator()
        
        # Obtener extracciones
        extractions = consolidator.get_all_extractions()
        
        if not extractions:
            print("⚠️ No se encontraron extracciones para el ejemplo")
            return
        
        print(f"📊 Se encontraron {len(extractions)} extracciones")
        
        # Consolidar datos
        df_main = consolidator.consolidate_extractions(extractions)
        df_arrays = consolidator.extract_array_fields(extractions)
        
        # Mostrar información de los DataFrames
        print(f"\n📋 DATAFRAME PRINCIPAL:")
        print(f"   Filas: {df_main.shape[0]}")
        print(f"   Columnas: {df_main.shape[1]}")
        
        # Mostrar columnas de valores
        value_columns = [col for col in df_main.columns if col.endswith('_value')]
        print(f"   Campos extraídos: {len(value_columns)}")
        print(f"   Primeros 5 campos: {value_columns[:5]}")
        
        # Mostrar información de arrays
        if not df_arrays.empty:
            print(f"\n📦 DATAFRAME DE ARRAYS:")
            print(f"   Filas: {df_arrays.shape[0]}")
            print(f"   Columnas: {df_arrays.shape[1]}")
            
            # Mostrar campos con arrays
            array_fields = df_arrays['field_name'].unique()
            print(f"   Campos con arrays: {list(array_fields)}")
        else:
            print(f"\n📦 DATAFRAME DE ARRAYS: Vacío")
        
        # Crear directorio de salida
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Guardar como Excel
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        
        # Archivo principal
        main_file = output_dir / f"example_main_{timestamp}.xlsx"
        with pd.ExcelWriter(main_file, engine='openpyxl') as writer:
            df_main.to_excel(writer, sheet_name='Extractions_Main', index=False)
            
            # Hoja con solo valores
            if value_columns:
                df_values = df_main[['extraction_id', 'job_id', 'created_at', 'processing_mode'] + value_columns]
                df_values.to_excel(writer, sheet_name='Values_Only', index=False)
        
        print(f"\n💾 ARCHIVO EXCEL CREADO:")
        print(f"   📁 Archivo principal: {main_file}")
        
        # Archivo de arrays si existe
        if not df_arrays.empty:
            arrays_file = output_dir / f"example_arrays_{timestamp}.xlsx"
            with pd.ExcelWriter(arrays_file, engine='openpyxl') as writer:
                df_arrays.to_excel(writer, sheet_name='Arrays_Main', index=False)
                
                # Hoja por tipo de campo
                for field_name in df_arrays['field_name'].unique():
                    field_data = df_arrays[df_arrays['field_name'] == field_name]
                    sheet_name = f"Array_{field_name}"[:31]
                    field_data.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"   📁 Archivo de arrays: {arrays_file}")
        
        # Mostrar estadísticas
        print(f"\n📈 ESTADÍSTICAS:")
        print(f"   Total extracciones: {len(df_main)}")
        print(f"   Total campos únicos: {len(value_columns)}")
        print(f"   Total elementos en arrays: {len(df_arrays) if not df_arrays.empty else 0}")
        
        # Mostrar campos más comunes
        if value_columns:
            print(f"\n📝 CAMPOS MÁS COMUNES:")
            for col in value_columns[:10]:
                field_name = col.replace('_value', '')
                non_null_count = df_main[col].notna().sum()
                print(f"   • {field_name}: {non_null_count} extracciones")
        
        print(f"\n✅ EJEMPLO COMPLETADO EXITOSAMENTE")
        print(f"📁 Archivos generados en: {output_dir.absolute()}")
        
    except Exception as e:
        print(f"❌ Error en ejemplo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    example_usage()
