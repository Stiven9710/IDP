#!/usr/bin/env python3
"""
Script para consolidar datos de extracciones desde Cosmos DB
Conecta al container 'extractions' y consolida los datos en DataFrames
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncio
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError

# Agregar el directorio raíz al path para importar configuraciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

class ExtractionConsolidator:
    """Consolidador de datos de extracciones desde Cosmos DB"""
    
    def __init__(self):
        """Inicializar el consolidador"""
        self.cosmos_client = None
        self.database = None
        self.container = None
        self._initialize_cosmos()
    
    def _initialize_cosmos(self):
        """Inicializar conexión a Cosmos DB"""
        try:
            print("🔗 Conectando a Cosmos DB...")
            print(f"   📍 Endpoint: {settings.azure_cosmos_endpoint}")
            print(f"   🗄️ Database: {settings.azure_cosmos_database_name}")
            print(f"   📦 Container: extractions")
            
            # Crear cliente de Cosmos DB
            self.cosmos_client = CosmosClient(
                url=settings.azure_cosmos_endpoint,
                credential=settings.azure_cosmos_key
            )
            
            # Obtener base de datos
            self.database = self.cosmos_client.get_database_client(
                database=settings.azure_cosmos_database_name
            )
            
            # Obtener container
            self.container = self.database.get_container_client("extractions")
            
            print("✅ Conexión a Cosmos DB establecida exitosamente")
            
        except Exception as e:
            print(f"❌ Error conectando a Cosmos DB: {e}")
            sys.exit(1)
    
    def get_all_extractions(self) -> List[Dict[str, Any]]:
        """Obtener todas las extracciones del container"""
        try:
            print("📥 Obteniendo todas las extracciones...")
            
            # Query para obtener todas las extracciones
            query = "SELECT * FROM c"
            
            # Ejecutar query
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            print(f"✅ Se encontraron {len(items)} extracciones")
            return items
            
        except Exception as e:
            print(f"❌ Error obteniendo extracciones: {e}")
            return []
    
    def consolidate_extractions(self, extractions: List[Dict[str, Any]]) -> pd.DataFrame:
        """Consolidar extracciones en un DataFrame principal"""
        try:
            print("🔄 Consolidando extracciones en DataFrame...")
            
            consolidated_data = []
            
            for extraction in extractions:
                # Extraer información básica
                extraction_id = extraction.get('id', 'unknown')
                job_id = extraction.get('job_id', 'unknown')
                created_at = extraction.get('created_at', '')
                processing_mode = extraction.get('processing_mode', 'unknown')
                
                # Extraer extraction_data
                extraction_data = extraction.get('extraction_data', [])
                
                # Crear fila base
                base_row = {
                    'extraction_id': extraction_id,
                    'job_id': job_id,
                    'created_at': created_at,
                    'processing_mode': processing_mode
                }
                
                # Procesar cada campo de extracción
                for field in extraction_data:
                    field_name = field.get('name', 'unknown')
                    field_value = field.get('value', '')
                    confidence = field.get('confidence', 0.0)
                    source_strategy = field.get('source_strategy', 'unknown')
                    
                    # Agregar campo a la fila
                    base_row[f"{field_name}_value"] = field_value
                    base_row[f"{field_name}_confidence"] = confidence
                    base_row[f"{field_name}_strategy"] = source_strategy
                
                consolidated_data.append(base_row)
            
            # Crear DataFrame
            df = pd.DataFrame(consolidated_data)
            
            print(f"✅ DataFrame consolidado creado: {df.shape[0]} filas, {df.shape[1]} columnas")
            return df
            
        except Exception as e:
            print(f"❌ Error consolidando extracciones: {e}")
            return pd.DataFrame()
    
    def extract_array_fields(self, extractions: List[Dict[str, Any]]) -> pd.DataFrame:
        """Extraer campos que contienen arrays en un DataFrame separado"""
        try:
            print("🔄 Extrayendo campos con arrays...")
            
            array_data = []
            
            for extraction in extractions:
                extraction_id = extraction.get('id', 'unknown')
                job_id = extraction.get('job_id', 'unknown')
                
                # Extraer extraction_data
                extraction_data = extraction.get('extraction_data', [])
                
                # Buscar campos que contengan arrays
                for field in extraction_data:
                    field_name = field.get('name', 'unknown')
                    field_value = field.get('value', '')
                    
                    # Verificar si el valor es un array (string que representa JSON)
                    if isinstance(field_value, str) and field_value.startswith('['):
                        try:
                            # Intentar parsear como JSON
                            array_content = json.loads(field_value)
                            
                            if isinstance(array_content, list):
                                # Procesar cada elemento del array
                                for i, item in enumerate(array_content):
                                    if isinstance(item, dict):
                                        # Crear fila para cada elemento del array
                                        array_row = {
                                            'extraction_id': extraction_id,
                                            'job_id': job_id,
                                            'field_name': field_name,
                                            'array_index': i,
                                            'field_name_original': field_name
                                        }
                                        
                                        # Agregar todas las propiedades del item
                                        for key, value in item.items():
                                            array_row[f"item_{key}"] = value
                                        
                                        array_data.append(array_row)
                                    
                        except json.JSONDecodeError:
                            # Si no se puede parsear como JSON, tratarlo como string
                            array_row = {
                                'extraction_id': extraction_id,
                                'job_id': job_id,
                                'field_name': field_name,
                                'array_index': 0,
                                'field_name_original': field_name,
                                'item_raw_value': field_value
                            }
                            array_data.append(array_row)
            
            # Crear DataFrame de arrays
            df_arrays = pd.DataFrame(array_data)
            
            if not df_arrays.empty:
                print(f"✅ DataFrame de arrays creado: {df_arrays.shape[0]} filas, {df_arrays.shape[1]} columnas")
            else:
                print("ℹ️ No se encontraron campos con arrays")
            
            return df_arrays
            
        except Exception as e:
            print(f"❌ Error extrayendo arrays: {e}")
            return pd.DataFrame()
    
    def save_to_excel(self, df_main: pd.DataFrame, df_arrays: pd.DataFrame, filename: str = None):
        """Guardar DataFrames en archivo Excel"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"extractions_consolidated_{timestamp}.xlsx"
            
            print(f"💾 Guardando datos en Excel: {filename}")
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Hoja principal con datos consolidados
                df_main.to_excel(writer, sheet_name='Extractions_Main', index=False)
                
                # Hoja con arrays si existe
                if not df_arrays.empty:
                    df_arrays.to_excel(writer, sheet_name='Extractions_Arrays', index=False)
                
                # Hoja con resumen
                summary_data = {
                    'Metric': ['Total Extractions', 'Total Fields', 'Array Fields', 'Date Generated'],
                    'Value': [
                        len(df_main),
                        len(df_main.columns) - 4,  # Excluir columnas base
                        len(df_arrays) if not df_arrays.empty else 0,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ]
                }
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='Summary', index=False)
            
            print(f"✅ Archivo Excel guardado exitosamente: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error guardando Excel: {e}")
            return None
    
    def generate_summary_report(self, df_main: pd.DataFrame, df_arrays: pd.DataFrame):
        """Generar reporte de resumen"""
        try:
            print("\n" + "="*80)
            print("📊 REPORTE DE CONSOLIDACIÓN DE EXTRACCIONES")
            print("="*80)
            
            # Estadísticas principales
            print(f"📈 Total de extracciones: {len(df_main)}")
            print(f"📋 Total de campos únicos: {len([col for col in df_main.columns if col.endswith('_value')])}")
            print(f"🔢 Total de elementos en arrays: {len(df_arrays) if not df_arrays.empty else 0}")
            
            # Campos más comunes
            value_columns = [col for col in df_main.columns if col.endswith('_value')]
            print(f"\n📝 Campos extraídos más comunes:")
            for col in value_columns[:10]:  # Mostrar solo los primeros 10
                field_name = col.replace('_value', '')
                non_null_count = df_main[col].notna().sum()
                print(f"   • {field_name}: {non_null_count} extracciones")
            
            # Estrategias de procesamiento
            if 'processing_mode' in df_main.columns:
                print(f"\n🤖 Estrategias de procesamiento:")
                strategy_counts = df_main['processing_mode'].value_counts()
                for strategy, count in strategy_counts.items():
                    print(f"   • {strategy}: {count} extracciones")
            
            # Campos con arrays
            if not df_arrays.empty:
                print(f"\n📦 Campos con arrays:")
                array_fields = df_arrays['field_name'].value_counts()
                for field, count in array_fields.items():
                    print(f"   • {field}: {count} elementos")
            
            print("="*80)
            
        except Exception as e:
            print(f"❌ Error generando reporte: {e}")

def main():
    """Función principal"""
    try:
        print("🚀 INICIANDO CONSOLIDACIÓN DE EXTRACCIONES")
        print("="*60)
        
        # Crear consolidador
        consolidator = ExtractionConsolidator()
        
        # Obtener todas las extracciones
        extractions = consolidator.get_all_extractions()
        
        if not extractions:
            print("⚠️ No se encontraron extracciones para consolidar")
            return
        
        # Consolidar en DataFrame principal
        df_main = consolidator.consolidate_extractions(extractions)
        
        if df_main.empty:
            print("⚠️ No se pudo consolidar los datos")
            return
        
        # Extraer campos con arrays
        df_arrays = consolidator.extract_array_fields(extractions)
        
        # Generar reporte de resumen
        consolidator.generate_summary_report(df_main, df_arrays)
        
        # Guardar en Excel
        excel_filename = consolidator.save_to_excel(df_main, df_arrays)
        
        if excel_filename:
            print(f"\n✅ CONSOLIDACIÓN COMPLETADA EXITOSAMENTE")
            print(f"📁 Archivo Excel generado: {excel_filename}")
            print(f"📊 Ubicación: {os.path.abspath(excel_filename)}")
        else:
            print("\n⚠️ CONSOLIDACIÓN COMPLETADA PERO NO SE PUDO GUARDAR EXCEL")
        
    except Exception as e:
        print(f"❌ Error en función principal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
