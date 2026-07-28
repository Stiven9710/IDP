#!/usr/bin/env python3
"""
Script para expandir arrays de productos en tabla separada
Convierte items_de_linea en registros individuales para análisis
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from consolidate_extractions import ExtractionConsolidator

class ProductsTableExpander:
    """Expansor de arrays de productos en tabla separada"""
    
    def __init__(self):
        """Inicializar expansor"""
        self.consolidator = ExtractionConsolidator()
    
    def expand_products_table(self) -> pd.DataFrame:
        """Expandir arrays de productos en tabla separada"""
        try:
            print("🔄 EXPANDIENDO TABLA DE PRODUCTOS")
            print("="*50)
            
            # Obtener extracciones
            extractions = self.consolidator.get_all_extractions()
            
            if not extractions:
                print("⚠️ No se encontraron extracciones")
                return pd.DataFrame()
            
            print(f"📊 Procesando {len(extractions)} extracciones...")
            
            products_data = []
            
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
                    
                    # Intentar parsear como JSON
                    try:
                        items_list = json.loads(items_value)
                        
                        if isinstance(items_list, list):
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
                                    
                    except json.JSONDecodeError:
                        # Si no se puede parsear, crear registro con valor raw
                        product_row = {
                            'extraction_id': extraction_id,
                            'job_id': job_id,
                            'invoice_number': invoice_number,
                            'created_at': created_at,
                            'processing_mode': processing_mode,
                            'item_index': 0,
                            'descripcion': 'ERROR_PARSING',
                            'cantidad': 0,
                            'precio_unitario': 0,
                            'impuesto_porcentaje': 0,
                            'total_linea': 0,
                            'confidence': items_field.get('confidence', 0),
                            'source_strategy': items_field.get('source_strategy', 'unknown'),
                            'raw_value': items_value
                        }
                        products_data.append(product_row)
            
            # Crear DataFrame
            df_products = pd.DataFrame(products_data)
            
            print(f"✅ Tabla de productos creada: {df_products.shape[0]} productos")
            print(f"   📊 Extracciones con productos: {df_products['extraction_id'].nunique()}")
            print(f"   📋 Facturas únicas: {df_products['invoice_number'].nunique()}")
            
            return df_products
            
        except Exception as e:
            print(f"❌ Error expandiendo tabla de productos: {e}")
            return pd.DataFrame()
    
    def _find_invoice_number(self, extraction: dict) -> str:
        """Buscar número de factura en la extracción"""
        extraction_data = extraction.get('extraction_data', [])
        
        # Buscar campos que contengan "factura" o "invoice"
        for field in extraction_data:
            field_name = field.get('name', '').lower()
            if 'factura' in field_name or 'invoice' in field_name:
                return field.get('value', '')
        
        return 'N/A'
    
    def _find_items_field(self, extraction: dict) -> dict:
        """Buscar campo de items de línea"""
        extraction_data = extraction.get('extraction_data', [])
        
        # Buscar campos que contengan "items" o "linea"
        for field in extraction_data:
            field_name = field.get('name', '').lower()
            if 'items' in field_name or 'linea' in field_name:
                return field
        
        return None
    
    def save_products_table(self, df_products: pd.DataFrame, filename: str = None) -> str:
        """Guardar tabla de productos en Excel"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"products_table_{timestamp}.xlsx"
            
            # Crear directorio de salida
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            filepath = output_dir / filename
            
            print(f"💾 Guardando tabla de productos: {filename}")
            
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
                stats_data = self._create_stats_sheet(df_products)
                stats_data.to_excel(writer, sheet_name='Statistics', index=False)
            
            print(f"✅ Tabla de productos guardada: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ Error guardando tabla de productos: {e}")
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
            print(f"⚠️ Error creando resumen por factura: {e}")
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
            print(f"⚠️ Error creando resumen por producto: {e}")
            return pd.DataFrame()
    
    def _create_stats_sheet(self, df_products: pd.DataFrame) -> pd.DataFrame:
        """Crear hoja de estadísticas"""
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
            print(f"⚠️ Error creando estadísticas: {e}")
            return pd.DataFrame()

def main():
    """Función principal"""
    try:
        print("🚀 EXPANDIENDO TABLA DE PRODUCTOS")
        print("="*60)
        
        # Crear expansor
        expander = ProductsTableExpander()
        
        # Expandir tabla de productos
        df_products = expander.expand_products_table()
        
        if df_products.empty:
            print("⚠️ No se pudieron expandir los productos")
            return
        
        # Guardar tabla
        excel_file = expander.save_products_table(df_products)
        
        if excel_file:
            print(f"\n✅ TABLA DE PRODUCTOS EXPANDIDA EXITOSAMENTE")
            print(f"📁 Archivo generado: {excel_file}")
            print(f"📊 Total productos: {len(df_products)}")
            print(f"📋 Total facturas: {df_products['invoice_number'].nunique()}")
        else:
            print("\n❌ No se pudo guardar la tabla de productos")
        
    except Exception as e:
        print(f"❌ Error en función principal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
