"""
Servicio para conversión de documentos PDF a imágenes
Optimizado para GPT-4o con DPI entre 150-400
"""

import base64
import logging
import os
import tempfile
from typing import List, Tuple
import fitz  # PyMuPDF
from PIL import Image
import io

logger = logging.getLogger(__name__)

class DocumentConverter:
    """Servicio para convertir documentos a imágenes optimizadas para GPT-4o"""
    
    def __init__(self, dpi_range: Tuple[int, int] = (150, 400)):
        """
        Inicializar conversor de documentos
        
        Args:
            dpi_range: Rango de DPI (min, max) para optimizar calidad vs rendimiento
        """
        self.dpi_range = dpi_range
        self.optimal_dpi = 300  # DPI óptimo para balance calidad/rendimiento
        logger.info(f"🔄 DocumentConverter inicializado con DPI óptimo: {self.optimal_dpi}")
    
    def pdf_to_images_png(
        self, 
        pdf_bytes: bytes, 
        max_pages: int = None,
        dpi: int = None
    ) -> List[str]:
        """
        Convertir PDF a imágenes PNG optimizadas para GPT-4o
        
        Args:
            pdf_bytes: Contenido del PDF en bytes
            max_pages: Número máximo de páginas a procesar (None = todas)
            dpi: DPI específico (None = usar DPI óptimo)
            
        Returns:
            Lista de imágenes en base64 con formato data:image/png;base64,...
        """
        logger.info("📄 Convirtiendo PDF a imágenes PNG optimizadas para GPT-4o")
        
        try:
            # Usar DPI especificado o el óptimo
            target_dpi = dpi if dpi else self.optimal_dpi
            
            # Validar DPI dentro del rango permitido
            if target_dpi < self.dpi_range[0] or target_dpi > self.dpi_range[1]:
                logger.warning(f"⚠️ DPI {target_dpi} fuera del rango {self.dpi_range}, usando DPI óptimo")
                target_dpi = self.optimal_dpi
            
            logger.info(f"🎯 Procesando PDF con DPI: {target_dpi}")
            
            # Abrir PDF con PyMuPDF
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(pdf_document)
            
            if max_pages and max_pages < total_pages:
                logger.info(f"📊 Procesando {max_pages} de {total_pages} páginas")
                pages_to_process = max_pages
            else:
                logger.info(f"📊 Procesando todas las {total_pages} páginas")
                pages_to_process = total_pages
            
            images_base64 = []
            
            for page_num in range(pages_to_process):
                logger.info(f"🔄 Procesando página {page_num + 1}/{pages_to_process}")
                
                # Obtener página
                page = pdf_document[page_num]
                
                # Calcular matriz de transformación para el DPI objetivo
                # PyMuPDF usa 72 DPI por defecto, calculamos el factor de escala
                scale_factor = target_dpi / 72.0
                mat = fitz.Matrix(scale_factor, scale_factor)
                
                # Renderizar página a imagen
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Convertir a PIL Image para optimización
                img_data = pix.tobytes("png")
                pil_image = Image.open(io.BytesIO(img_data))
                
                # Optimizar imagen para GPT-4o
                optimized_image = self._optimize_image_for_gpt4o(pil_image)
                
                # Convertir a base64
                img_buffer = io.BytesIO()
                optimized_image.save(img_buffer, format='PNG', optimize=True)
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                
                # Crear URL de datos con formato correcto para GPT-4o
                data_url = f"data:image/png;base64,{img_base64}"
                images_base64.append(data_url)
                
                logger.info(f"✅ Página {page_num + 1} convertida: {len(img_base64)} caracteres base64")
            
            pdf_document.close()
            
            logger.info(f"🎉 Conversión completada: {len(images_base64)} imágenes generadas")
            return images_base64
            
        except Exception as e:
            logger.error(f"❌ Error convirtiendo PDF a imágenes: {str(e)}")
            raise
    
    def _optimize_image_for_gpt4o(self, image: Image.Image) -> Image.Image:
        """
        Optimizar imagen para GPT-4o
        
        Args:
            image: Imagen PIL a optimizar
            
        Returns:
            Imagen optimizada
        """
        try:
            # Convertir a RGB si es necesario (GPT-4o prefiere RGB)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Redimensionar si la imagen es muy grande (GPT-4o tiene límites)
            max_dimension = 2048  # Límite recomendado para GPT-4o
            
            if image.width > max_dimension or image.height > max_dimension:
                # Mantener aspect ratio
                ratio = min(max_dimension / image.width, max_dimension / image.height)
                new_width = int(image.width * ratio)
                new_height = int(image.height * ratio)
                
                logger.info(f"🔄 Redimensionando imagen de {image.size} a ({new_width}, {new_height})")
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Aplicar optimizaciones adicionales si es necesario
            # Por ejemplo, ajustar contraste para mejor legibilidad
            from PIL import ImageEnhance
            
            # Aumentar ligeramente el contraste para mejor legibilidad
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.1)  # Aumentar contraste en 10%
            
            logger.info(f"✅ Imagen optimizada para GPT-4o: {image.size}, modo: {image.mode}")
            return image
            
        except Exception as e:
            logger.warning(f"⚠️ Error optimizando imagen: {str(e)}, retornando imagen original")
            return image
    
    def get_optimal_dpi_for_document(self, pdf_bytes: bytes) -> int:
        """
        Determinar DPI óptimo basado en el contenido del documento
        
        Args:
            pdf_bytes: Contenido del PDF en bytes
            
        Returns:
            DPI óptimo recomendado
        """
        try:
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            # Analizar primera página para determinar complejidad
            if len(pdf_document) > 0:
                page = pdf_document[0]
                
                # Contar elementos de texto
                text_blocks = page.get_text("dict")
                text_count = len(text_blocks.get("blocks", []))
                
                # Contar imágenes
                image_count = len(page.get_images())
                
                # Determinar DPI basado en complejidad
                if text_count > 50 or image_count > 5:
                    # Documento complejo, usar DPI alto
                    optimal_dpi = 400
                    logger.info("📊 Documento complejo detectado, usando DPI 400")
                elif text_count > 20:
                    # Documento moderado, usar DPI medio
                    optimal_dpi = 300
                    logger.info("📊 Documento moderado detectado, usando DPI 300")
                else:
                    # Documento simple, usar DPI bajo
                    optimal_dpi = 200
                    logger.info("📊 Documento simple detectado, usando DPI 200")
                
                pdf_document.close()
                return optimal_dpi
            else:
                pdf_document.close()
                return self.optimal_dpi
                
        except Exception as e:
            logger.warning(f"⚠️ Error analizando documento: {str(e)}, usando DPI por defecto")
            return self.optimal_dpi
