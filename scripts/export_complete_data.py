#!/usr/bin/env python3
"""
Script único para exportar todos los datos de extracciones
Genera: DataFrame principal + Tabla de productos expandida
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import ast  # Para parsear Python literal

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from consolidate_extractions import ExtractionConsolidator

class CompleteDataExporter:
    """Exportador completo de datos de extracciones"""
    
    def __init__(self):
        """Inicializar exportador"""
        self.consolidator = ExtractionConsolidator()
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def export_all_data(self) -> dict:
        """Exportar todos los datos disponibles"""
        try:
            print("🚀 EXPORTANDO DATOS COMPLETOS DE EXTRACCIONES")
            print("="*70)
            
            # Obtener extracciones
            extractions = self.consolidator.get_all_extractions()
            
            if not extractions:
                print("⚠️ No se encontraron extracciones")
                return {}
            
            print(f"📊 Total extracciones encontradas: {len(extractions)}")
            
            # Generar timestamp único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 1. Exportar DataFrame principal
            print(f"\n📋 PASO 1: EXPORTANDO DATAFRAME PRINCIPAL")
            main_file = self._export_main_dataframe(extractions, timestamp)
            
            # 2. Exportar tabla de productos expandida
            print(f"\n📦 PASO 2: EXPORTANDO TABLA DE PRODUCTOS")
            products_file = self._export_products_table(extractions, timestamp)
            
            # 3. Exportar archivo consolidado
            print(f"\n📊 PASO 3: EXPORTANDO ARCHIVO CONSOLIDADO")
            consolidated_file = self._export_consolidated_file(extractions, timestamp)
            
            # 4. Generar reporte de resumen
            print(f"\n📈 PASO 4: GENERANDO REPORTE DE RESUMEN")
            summary_file = self._generate_summary_report(extractions, timestamp)
            
            # Mostrar resumen final
            exported_files = {
                'main_dataframe': main_file,
                'products_table': products_file,
                'consolidated': consolidated_file,
                'summary': summary_file
            }
            
            print(f"\n✅ EXPORTACIÓN COMPLETADA EXITOSAMENTE")
            print(f"📁 Archivos generados: {len([f for f in exported_files.values() if f])}")
            for file_type, file_path in exported_files.items():
                if file_path:
                    print(f"   • {file_type}: {file_path}")
            
            return exported_files
            
        except Exception as e:
            print(f"❌ Error en exportación completa: {e}")
            return {}
    
    def _export_main_dataframe(self, extractions: list, timestamp: str) -> str:
        """Exportar DataFrame principal"""
        try:
            print("   🔄 Consolidando extracciones...")
            
            # Consolidar datos
            df_main = self.consolidator.consolidate_extractions(extractions)
            
            if df_main.empty:
                print("   ⚠️ No se pudo consolidar el DataFrame principal")
                return None
            
            filename = f"extractions_main_{timestamp}.xlsx"
            filepath = self.output_dir / filename
            
            print(f"   💾 Guardando DataFrame principal: {filename}")
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja principal
                df_main.to_excel(writer, sheet_name='Extractions_Main', index=False)
                
                # Hoja con solo valores
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
            
            print(f"   ✅ DataFrame principal guardado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"   ❌ Error exportando DataFrame principal: {e}")
            return None
    
    def _export_products_table(self, extractions: list, timestamp: str) -> str:
        """Exportar tabla de productos expandida"""
        try:
            print("   🔄 Expandiendo tabla de productos...")
            
            products_data = []
            parsing_errors = 0
            successful_parsings = 0
            
            for extraction in extractions:
                extraction_id = extraction.get('id', 'unknown')
                job_id = extraction.get('job_id', 'unknown')
                created_at = extraction.get('created_at', '')
                processing_mode = extraction.get('processing_mode', 'unknown')
                
                # Buscar número de factura
                invoice_number = self._find_invoice_number(extraction)
                
                # Buscar campo items_de_linea
                items_field = self._find_items_field(extraction)
                
                if items_field and items_field.get('value'):
                    items_value = items_field.get('value', '')
                    items_list = self._parse_items_value(items_value)
                    
                    if items_list:
                        successful_parsings += 1
                        # Procesar cada item
                        for i, item in enumerate(items_list):
                            if isinstance(item, dict):
                                product_row = {
                                    'extraction_id': extraction_id,
                                    'job_id': job_id,
                                    'invoice_number': invoice_number,
                                    'created_at': created_at,
                                    'processing_mode': processing_mode,
                                    'item_index': i,
                                    'descripcion': item.get('descripcion', ''),
                                    'cantidad': item.get('cantidad', 0),
                                    'precio_unitario': item.get('precio_unitario', 0),
                                    'impuesto_porcentaje': item.get('impuesto_porcentaje', 0),
                                    'total_linea': item.get('total_linea', 0),
                                    'confidence': items_field.get('confidence', 0),
                                    'source_strategy': items_field.get('source_strategy', 'unknown')
                                }
                                products_data.append(product_row)
                    else:
                        parsing_errors += 1
            
            # Crear DataFrame
            df_products = pd.DataFrame(products_data)
            
            if df_products.empty:
                print("   ⚠️ No se pudieron expandir los productos")
                return None
            
            filename = f"products_table_{timestamp}.xlsx"
            filepath = self.output_dir / filename
            
            print(f"   💾 Guardando tabla de productos: {filename}")
            print(f"   📊 Total productos: {len(df_products)}")
            print(f"   ✅ Parsings exitosos: {successful_parsings}")
            print(f"   ❌ Errores de parsing: {parsing_errors}")
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja principal con todos los productos
                df_products.to_excel(writer, sheet_name='Products_Table', index=False)
                
                # Hoja con resumen por factura
                if not df_products.empty:
                    invoice_summary = self._create_invoice_summary(df_products)
                    invoice_summary.to_excel(writer, sheet_name='Invoice_Summary', index=False)
                
                # Hoja con resumen por producto
                if not df_products.empty:
                    product_summary = self._create_product_summary(df_products)
                    product_summary.to_excel(writer, sheet_name='Product_Summary', index=False)
                
                # Hoja con estadísticas
                stats_data = self._create_products_stats_sheet(df_products)
                stats_data.to_excel(writer, sheet_name='Statistics', index=False)
            
            print(f"   ✅ Tabla de productos guardada: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"   ❌ Error exportando tabla de productos: {e}")
            return None
    
    def _export_consolidated_file(self, extractions: list, timestamp: str) -> str:
        """Exportar archivo consolidado con todos los datos"""
        try:
            print("   🔄 Creando archivo consolidado...")
            
            # Consolidar datos principales
            df_main = self.consolidator.consolidate_extractions(extractions)
            
            # Expandir productos
            products_data = []
            for extraction in extractions:
                extraction_id = extraction.get('id', 'unknown')
                job_id = extraction.get('job_id', 'unknown')
                invoice_number = self._find_invoice_number(extraction)
                items_field = self._find_items_field(extraction)
                
                if items_field and items_field.get('value'):
                    items_list = self._parse_items_value(items_field.get('value', ''))
                    if items_list:
                        for i, item in enumerate(items_list):
                            if isinstance(item, dict):
                                product_row = {
                                    'extraction_id': extraction_id,
                                    'job_id': job_id,
                                    'invoice_number': invoice_number,
                                    'item_index': i,
                                    'descripcion': item.get('descripcion', ''),
                                    'cantidad': item.get('cantidad', 0),
                                    'precio_unitario': item.get('precio_unitario', 0),
                                    'impuesto_porcentaje': item.get('impuesto_porcentaje', 0),
                                    'total_linea': item.get('total_linea', 0)
                                }
                                products_data.append(product_row)
            
            df_products = pd.DataFrame(products_data)
            
            filename = f"extractions_consolidated_{timestamp}.xlsx"
            filepath = self.output_dir / filename
            
            print(f"   💾 Guardando archivo consolidado: {filename}")
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja principal
                df_main.to_excel(writer, sheet_name='Extractions_Main', index=False)
                
                # Hoja de productos
                if not df_products.empty:
                    df_products.to_excel(writer, sheet_name='Products_Table', index=False)
                
                # Hoja de resumen general
                summary_data = self._create_general_summary(df_main, df_products)
                summary_data.to_excel(writer, sheet_name='General_Summary', index=False)
            
            print(f"   ✅ Archivo consolidado guardado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"   ❌ Error exportando archivo consolidado: {e}")
            return None
    
    def _generate_summary_report(self, extractions: list, timestamp: str) -> str:
        """Generar reporte de resumen"""
        try:
            print("   🔄 Generando reporte de resumen...")
            
            # Consolidar datos
            df_main = self.consolidator.consolidate_extractions(extractions)
            
            # Expandir productos
            products_data = []
            for extraction in extractions:
                items_field = self._find_items_field(extraction)
                if items_field and items_field.get('value'):
                    items_list = self._parse_items_value(items_field.get('value', ''))
                    if items_list:
                        for item in items_list:
                            if isinstance(item, dict):
                                products_data.append(item)
            
            df_products = pd.DataFrame(products_data)
            
            filename = f"summary_report_{timestamp}.xlsx"
            filepath = self.output_dir / filename
            
            print(f"   💾 Guardando reporte de resumen: {filename}")
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja de estadísticas generales
                general_stats = self._create_general_summary(df_main, df_products)
                general_stats.to_excel(writer, sheet_name='General_Statistics', index=False)
                
                # Hoja de análisis de campos
                field_analysis = self._create_field_analysis(df_main)
                field_analysis.to_excel(writer, sheet_name='Field_Analysis', index=False)
                
                # Hoja de análisis de productos
                if not df_products.empty:
                    product_analysis = self._create_product_analysis(df_products)
                    product_analysis.to_excel(writer, sheet_name='Product_Analysis', index=False)
            
            print(f"   ✅ Reporte de resumen guardado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"   ❌ Error generando reporte de resumen: {e}")
            return None
    
    def _parse_items_value(self, items_value: str) -> list:
        """Parsear valor de items con múltiples métodos"""
        try:
            # Método 1: JSON estándar
            if items_value.startswith('[') and items_value.endswith(']'):
                try:
                    return json.loads(items_value)
                except json.JSONDecodeError:
                    pass
            
            # Método 2: Python literal (para comillas simples)
            try:
                return ast.literal_eval(items_value)
            except (ValueError, SyntaxError):
                pass
            
            # Método 3: Reemplazar comillas simples por dobles
            try:
                fixed_value = items_value.replace("'", '"')
                return json.loads(fixed_value)
            except json.JSONDecodeError:
                pass
            
            return None
            
        except Exception as e:
            return None
    
    def _find_invoice_number(self, extraction: dict) -> str:
        """Buscar número de factura en la extracción"""
        extraction_data = extraction.get('extraction_data', [])
        
        for field in extraction_data:
            field_name = field.get('name', '').lower()
            if 'factura' in field_name or 'invoice' in field_name:
                return field.get('value', '')
        
        return 'N/A'
    
    def _find_items_field(self, extraction: dict) -> dict:
        """Buscar campo de items de línea"""
        extraction_data = extraction.get('extraction_data', [])
        
        for field in extraction_data:
            field_name = field.get('name', '').lower()
            if 'items' in field_name or 'linea' in field_name:
                return field
        
        return None
    
    def _create_invoice_summary(self, df_products: pd.DataFrame) -> pd.DataFrame:
        """Crear resumen por factura"""
        try:
            if df_products.empty:
                return pd.DataFrame()
            
            summary = df_products.groupby(['invoice_number', 'job_id']).agg({
                'descripcion': 'count',
                'cantidad': 'sum',
                'total_linea': 'sum',
                'created_at': 'first',
                'processing_mode': 'first'
            }).reset_index()
            
            summary.columns = ['invoice_number', 'job_id', 'total_products', 'total_quantity', 'total_amount', 'created_at', 'processing_mode']
            
            return summary
            
        except Exception as e:
            return pd.DataFrame()
    
    def _create_product_summary(self, df_products: pd.DataFrame) -> pd.DataFrame:
        """Crear resumen por producto"""
        try:
            if df_products.empty:
                return pd.DataFrame()
            
            summary = df_products.groupby('descripcion').agg({
                'cantidad': 'sum',
                'total_linea': 'sum',
                'invoice_number': 'nunique',
                'precio_unitario': 'mean'
            }).reset_index()
            
            summary.columns = ['product_description', 'total_quantity', 'total_amount', 'invoices_count', 'avg_unit_price']
            summary = summary.sort_values('total_quantity', ascending=False)
            
            return summary
            
        except Exception as e:
            return pd.DataFrame()
    
    def _create_products_stats_sheet(self, df_products: pd.DataFrame) -> pd.DataFrame:
        """Crear hoja de estadísticas de productos"""
        try:
            if df_products.empty:
                return pd.DataFrame()
            
            stats = {
                'Metric': [
                    'Total Products',
                    'Total Invoices',
                    'Total Quantity',
                    'Total Amount',
                    'Average Products per Invoice',
                    'Most Common Product',
                    'Date Generated'
                ],
                'Value': [
                    len(df_products),
                    df_products['invoice_number'].nunique(),
                    df_products['cantidad'].sum(),
                    df_products['total_linea'].sum(),
                    len(df_products) / df_products['invoice_number'].nunique() if df_products['invoice_number'].nunique() > 0 else 0,
                    df_products['descripcion'].mode().iloc[0] if not df_products['descripcion'].mode().empty else 'N/A',
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ]
            }
            
            return pd.DataFrame(stats)
            
        except Exception as e:
            return pd.DataFrame()
    
    def _create_general_summary(self, df_main: pd.DataFrame, df_products: pd.DataFrame) -> pd.DataFrame:
        """Crear resumen general"""
        try:
            stats = {
                'Metric': [
                    'Total Extractions',
                    'Total Fields',
                    'Total Products',
                    'Total Invoices',
                    'Processing Modes',
                    'Date Generated'
                ],
                'Value': [
                    len(df_main),
                    len([col for col in df_main.columns if col.endswith('_value')]),
                    len(df_products) if not df_products.empty else 0,
                    df_products['invoice_number'].nunique() if not df_products.empty else 0,
                    df_main['processing_mode'].nunique() if 'processing_mode' in df_main.columns else 0,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ]
            }
            
            return pd.DataFrame(stats)
            
        except Exception as e:
            return pd.DataFrame()
    
    def _create_field_analysis(self, df_main: pd.DataFrame) -> pd.DataFrame:
        """Crear análisis de campos"""
        try:
            value_columns = [col for col in df_main.columns if col.endswith('_value')]
            
            field_analysis = []
            for col in value_columns:
                field_name = col.replace('_value', '')
                non_null_count = df_main[col].notna().sum()
                null_count = df_main[col].isna().sum()
                
                field_analysis.append({
                    'field_name': field_name,
                    'extractions_with_value': non_null_count,
                    'extractions_without_value': null_count,
                    'completion_rate': (non_null_count / len(df_main)) * 100 if len(df_main) > 0 else 0
                })
            
            return pd.DataFrame(field_analysis)
            
        except Exception as e:
            return pd.DataFrame()
    
    def _create_product_analysis(self, df_products: pd.DataFrame) -> pd.DataFrame:
        """Crear análisis de productos"""
        try:
            if df_products.empty:
                return pd.DataFrame()
            
            analysis = {
                'Metric': [
                    'Total Products',
                    'Unique Products',
                    'Total Quantity',
                    'Total Amount',
                    'Average Unit Price',
                    'Most Expensive Product',
                    'Cheapest Product'
                ],
                'Value': [
                    len(df_products),
                    df_products['descripcion'].nunique(),
                    df_products['cantidad'].sum(),
                    df_products['total_linea'].sum(),
                    df_products['precio_unitario'].mean(),
                    df_products.loc[df_products['precio_unitario'].idxmax(), 'descripcion'] if not df_products.empty else 'N/A',
                    df_products.loc[df_products['precio_unitario'].idxmin(), 'descripcion'] if not df_products.empty else 'N/A'
                ]
            }
            
            return pd.DataFrame(analysis)
            
        except Exception as e:
            return pd.DataFrame()

def main():
    """Función principal"""
    try:
        # Crear exportador
        exporter = CompleteDataExporter()
        
        # Exportar todos los datos
        exported_files = exporter.export_all_data()
        
        if exported_files:
            print(f"\n🎉 EXPORTACIÓN COMPLETA EXITOSA")
            print(f"📊 Total de archivos generados: {len([f for f in exported_files.values() if f])}")
        else:
            print("\n❌ No se pudieron generar archivos")
        
    except Exception as e:
        print(f"❌ Error en función principal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

