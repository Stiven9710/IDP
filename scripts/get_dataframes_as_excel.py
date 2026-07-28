#!/usr/bin/env python3
"""
Script simple para obtener DataFrames como archivos Excel
Retorna archivos Excel listos para usar
"""

import os
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from consolidate_extractions import ExtractionConsolidator

def get_dataframes_as_excel():
    """Obtener DataFrames como archivos Excel"""
    try:
        print("🚀 OBTENIENDO DATAFRAMES COMO EXCEL")
        print("="*50)
        
        # Crear consolidador
        consolidator = ExtractionConsolidator()
        
        # Obtener extracciones
        extractions = consolidator.get_all_extractions()
        
        if not extractions:
            print("⚠️ No se encontraron extracciones")
            return None, None
        
        # Consolidar datos
        df_main = consolidator.consolidate_extractions(extractions)
        df_arrays = consolidator.extract_array_fields(extractions)
        
        # Crear directorio de salida
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Generar nombres de archivos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Archivo principal
        main_filename = f"extractions_main_{timestamp}.xlsx"
        main_filepath = output_dir / main_filename
        
        # Archivo de arrays
        arrays_filename = f"extractions_arrays_{timestamp}.xlsx"
        arrays_filepath = output_dir / arrays_filename
        
        # Guardar DataFrame principal
        print(f"💾 Guardando DataFrame principal: {main_filename}")
        with pd.ExcelWriter(main_filepath, engine='openpyxl') as writer:
            df_main.to_excel(writer, sheet_name='Extractions_Main', index=False)
            
            # Crear hoja con solo valores
            value_columns = [col for col in df_main.columns if col.endswith('_value')]
            if value_columns:
                df_values = df_main[['extraction_id', 'job_id', 'created_at', 'processing_mode'] + value_columns]
                df_values.to_excel(writer, sheet_name='Values_Only', index=False)
        
        print(f"✅ DataFrame principal guardado: {main_filepath}")
        
        # Guardar DataFrame de arrays si existe
        if not df_arrays.empty:
            print(f"💾 Guardando DataFrame de arrays: {arrays_filename}")
            with pd.ExcelWriter(arrays_filepath, engine='openpyxl') as writer:
                df_arrays.to_excel(writer, sheet_name='Arrays_Main', index=False)
                
                # Crear hoja por tipo de campo
                for field_name in df_arrays['field_name'].unique():
                    field_data = df_arrays[df_arrays['field_name'] == field_name]
                    sheet_name = f"Array_{field_name}"[:31]  # Excel limita a 31 caracteres
                    field_data.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"✅ DataFrame de arrays guardado: {arrays_filepath}")
        else:
            print("ℹ️ No hay arrays para guardar")
            arrays_filepath = None
        
        # Mostrar resumen
        print(f"\n📊 RESUMEN DE EXPORTACIÓN:")
        print(f"   📁 DataFrame principal: {main_filepath}")
        if arrays_filepath:
            print(f"   📁 DataFrame de arrays: {arrays_filepath}")
        print(f"   📈 Total extracciones: {len(df_main)}")
        print(f"   📋 Total campos: {len([col for col in df_main.columns if col.endswith('_value')])}")
        if not df_arrays.empty:
            print(f"   📦 Total elementos en arrays: {len(df_arrays)}")
        
        return str(main_filepath), str(arrays_filepath) if arrays_filepath else None
        
    except Exception as e:
        print(f"❌ Error obteniendo DataFrames: {e}")
        return None, None

def main():
    """Función principal"""
    try:
        main_file, arrays_file = get_dataframes_as_excel()
        
        if main_file:
            print(f"\n✅ EXCEL GENERADO EXITOSAMENTE")
            print(f"📁 Archivo principal: {main_file}")
            if arrays_file:
                print(f"📁 Archivo de arrays: {arrays_file}")
        else:
            print("\n❌ No se pudo generar Excel")
        
    except Exception as e:
        print(f"❌ Error en función principal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
