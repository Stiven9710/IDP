#!/usr/bin/env python3
"""
Script para exportar DataFrames como archivos Excel separados
Retorna archivos Excel individuales para cada DataFrame
"""

import os
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from consolidate_extractions import ExtractionConsolidator

class DataFrameExcelExporter:
    """Exportador de DataFrames a archivos Excel separados"""
    
    def __init__(self, output_dir: str = "output"):
        """Inicializar exportador"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Crear consolidador
        self.consolidator = ExtractionConsolidator()
    
    def export_main_dataframe(self, df_main: pd.DataFrame, filename: str = None) -> str:
        """Exportar DataFrame principal a Excel"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"extractions_main_{timestamp}.xlsx"
            
            filepath = self.output_dir / filename
            
            print(f"💾 Exportando DataFrame principal: {filename}")
            
            # Crear Excel con múltiples hojas
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja principal
                df_main.to_excel(writer, sheet_name='Extractions_Main', index=False)
                
                # Hoja con solo valores (sin confidence y strategy)
                value_columns = [col for col in df_main.columns if col.endswith('_value')]
                if value_columns:
                    df_values = df_main[['extraction_id', 'job_id', 'created_at', 'processing_mode'] + value_columns]
                    df_values.to_excel(writer, sheet_name='Values_Only', index=False)
                
                # Hoja con solo confidence
                confidence_columns = [col for col in df_main.columns if col.endswith('_confidence')]
                if confidence_columns:
                    df_confidence = df_main[['extraction_id', 'job_id'] + confidence_columns]
                    df_confidence.to_excel(writer, sheet_name='Confidence_Scores', index=False)
                
                # Hoja con solo strategies
                strategy_columns = [col for col in df_main.columns if col.endswith('_strategy')]
                if strategy_columns:
                    df_strategies = df_main[['extraction_id', 'job_id'] + strategy_columns]
                    df_strategies.to_excel(writer, sheet_name='Processing_Strategies', index=False)
                
                # Hoja de resumen
                self._create_summary_sheet(writer, df_main)
            
            print(f"✅ DataFrame principal exportado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ Error exportando DataFrame principal: {e}")
            return None
    
    def export_arrays_dataframe(self, df_arrays: pd.DataFrame, filename: str = None) -> str:
        """Exportar DataFrame de arrays a Excel"""
        try:
            if df_arrays.empty:
                print("ℹ️ No hay arrays para exportar")
                return None
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"extractions_arrays_{timestamp}.xlsx"
            
            filepath = self.output_dir / filename
            
            print(f"💾 Exportando DataFrame de arrays: {filename}")
            
            # Crear Excel con múltiples hojas
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja principal de arrays
                df_arrays.to_excel(writer, sheet_name='Arrays_Main', index=False)
                
                # Hoja por tipo de campo
                for field_name in df_arrays['field_name'].unique():
                    field_data = df_arrays[df_arrays['field_name'] == field_name]
                    sheet_name = f"Array_{field_name}"[:31]  # Excel limita nombres de hoja a 31 caracteres
                    field_data.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Hoja de resumen de arrays
                self._create_arrays_summary_sheet(writer, df_arrays)
            
            print(f"✅ DataFrame de arrays exportado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ Error exportando DataFrame de arrays: {e}")
            return None
    
    def _create_summary_sheet(self, writer, df_main: pd.DataFrame):
        """Crear hoja de resumen para DataFrame principal"""
        try:
            # Estadísticas básicas
            summary_data = {
                'Metric': [
                    'Total Extractions',
                    'Total Fields',
                    'Date Generated',
                    'Processing Modes',
                    'Most Common Field',
                    'Average Confidence'
                ],
                'Value': [
                    len(df_main),
                    len([col for col in df_main.columns if col.endswith('_value')]),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    df_main['processing_mode'].nunique() if 'processing_mode' in df_main.columns else 0,
                    'N/A',  # Se calculará después
                    'N/A'   # Se calculará después
                ]
            }
            
            # Calcular campo más común
            value_columns = [col for col in df_main.columns if col.endswith('_value')]
            if value_columns:
                field_counts = {}
                for col in value_columns:
                    field_name = col.replace('_value', '')
                    non_null_count = df_main[col].notna().sum()
                    field_counts[field_name] = non_null_count
                
                if field_counts:
                    most_common_field = max(field_counts, key=field_counts.get)
                    summary_data['Value'][4] = f"{most_common_field} ({field_counts[most_common_field]} extracciones)"
            
            # Calcular confianza promedio
            confidence_columns = [col for col in df_main.columns if col.endswith('_confidence')]
            if confidence_columns:
                all_confidence = []
                for col in confidence_columns:
                    conf_values = df_main[col].dropna()
                    all_confidence.extend(conf_values.tolist())
                
                if all_confidence:
                    avg_confidence = sum(all_confidence) / len(all_confidence)
                    summary_data['Value'][5] = f"{avg_confidence:.2f}"
            
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            
        except Exception as e:
            print(f"⚠️ Error creando hoja de resumen: {e}")
    
    def _create_arrays_summary_sheet(self, writer, df_arrays: pd.DataFrame):
        """Crear hoja de resumen para DataFrame de arrays"""
        try:
            # Estadísticas de arrays
            array_fields = df_arrays['field_name'].value_counts()
            
            summary_data = {
                'Field Name': array_fields.index.tolist(),
                'Total Items': array_fields.values.tolist(),
                'Unique Jobs': [df_arrays[df_arrays['field_name'] == field]['job_id'].nunique() 
                               for field in array_fields.index]
            }
            
            df_arrays_summary = pd.DataFrame(summary_data)
            df_arrays_summary.to_excel(writer, sheet_name='Arrays_Summary', index=False)
            
        except Exception as e:
            print(f"⚠️ Error creando hoja de resumen de arrays: {e}")
    
    def export_all_dataframes(self) -> dict:
        """Exportar todos los DataFrames como archivos Excel separados"""
        try:
            print("🚀 INICIANDO EXPORTACIÓN DE DATAFRAMES A EXCEL")
            print("="*60)
            
            # Obtener extracciones
            extractions = self.consolidator.get_all_extractions()
            
            if not extractions:
                print("⚠️ No se encontraron extracciones para exportar")
                return {}
            
            # Consolidar datos
            df_main = self.consolidator.consolidate_extractions(extractions)
            df_arrays = self.consolidator.extract_array_fields(extractions)
            
            # Exportar DataFrames
            exported_files = {}
            
            # Exportar DataFrame principal
            main_file = self.export_main_dataframe(df_main)
            if main_file:
                exported_files['main_dataframe'] = main_file
            
            # Exportar DataFrame de arrays
            arrays_file = self.export_arrays_dataframe(df_arrays)
            if arrays_file:
                exported_files['arrays_dataframe'] = arrays_file
            
            # Crear archivo consolidado
            consolidated_file = self._create_consolidated_excel(df_main, df_arrays)
            if consolidated_file:
                exported_files['consolidated'] = consolidated_file
            
            print(f"\n✅ EXPORTACIÓN COMPLETADA")
            print(f"📁 Archivos generados: {len(exported_files)}")
            for file_type, file_path in exported_files.items():
                print(f"   • {file_type}: {file_path}")
            
            return exported_files
            
        except Exception as e:
            print(f"❌ Error en exportación: {e}")
            return {}
    
    def _create_consolidated_excel(self, df_main: pd.DataFrame, df_arrays: pd.DataFrame) -> str:
        """Crear archivo Excel consolidado con todos los datos"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"extractions_consolidated_{timestamp}.xlsx"
            filepath = self.output_dir / filename
            
            print(f"💾 Creando archivo Excel consolidado: {filename}")
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja principal
                df_main.to_excel(writer, sheet_name='Extractions_Main', index=False)
                
                # Hoja de arrays si existe
                if not df_arrays.empty:
                    df_arrays.to_excel(writer, sheet_name='Extractions_Arrays', index=False)
                
                # Hoja de resumen
                self._create_summary_sheet(writer, df_main)
                
                # Hoja de resumen de arrays si existe
                if not df_arrays.empty:
                    self._create_arrays_summary_sheet(writer, df_arrays)
            
            print(f"✅ Archivo Excel consolidado creado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ Error creando archivo consolidado: {e}")
            return None

def main():
    """Función principal"""
    try:
        # Crear exportador
        exporter = DataFrameExcelExporter()
        
        # Exportar todos los DataFrames
        exported_files = exporter.export_all_dataframes()
        
        if exported_files:
            print(f"\n🎉 EXPORTACIÓN EXITOSA")
            print(f"📊 Total de archivos generados: {len(exported_files)}")
        else:
            print("\n⚠️ No se pudieron generar archivos Excel")
        
    except Exception as e:
        print(f"❌ Error en función principal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
