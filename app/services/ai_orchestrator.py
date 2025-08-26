"""
Orquestador de servicios de IA para el procesamiento de documentos
"""

import asyncio
import base64
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.core.config import settings
from app.models.request import FieldDefinition
from app.models.response import ExtractionField, ProcessingMode
from app.utils.azure_clients import AzureOpenAIClient, CustomDocumentIntelligenceClient

# Configurar logging
logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Resultado de la extracción de datos"""
    extraction_data: List[ExtractionField]
    pages_processed: int
    review_flags: List[str]
    processing_time_ms: int
    strategy_used: str


class AIOrchestrator:
    """Servicio orquestador de IA para procesamiento de documentos"""
    
    def __init__(self):
        """Inicializar el orquestador de IA"""
        self.openai_client = AzureOpenAIClient()
        self.doc_intelligence_client = CustomDocumentIntelligenceClient()
        
        logger.info("🤖 AIOrchestrator inicializado correctamente")
    
    async def process_document(
        self,
        document_content: bytes,
        fields: List[FieldDefinition],
        prompt_general: str,
        processing_mode: str
    ) -> ExtractionResult:
        """
        Procesar documento con la estrategia de IA especificada
        
        Args:
            document_content: Contenido del documento en bytes
            fields: Lista de campos a extraer
            prompt_general: Prompt general para la extracción
            processing_mode: Modo de procesamiento a utilizar
            
        Returns:
            Resultado de la extracción con los datos procesados
        """
        start_time = time.time()
        logger.info(f"🤖 Iniciando procesamiento de IA con modo: {processing_mode}")
        logger.info(f"📝 Número de campos a extraer: {len(fields)}")
        
        try:
            # Determinar estrategia de procesamiento
            if processing_mode == ProcessingMode.DUAL_SERVICE:
                logger.info("🔄 Procesando con estrategia DUAL SERVICE")
                result = await self._process_dual_service(
                    document_content, fields, prompt_general
                )
            elif processing_mode == ProcessingMode.GPT_VISION_ONLY:
                logger.info("👁️ Procesando con estrategia GPT VISION ONLY")
                result = await self._process_gpt_vision_only(
                    document_content, fields, prompt_general
                )
            elif processing_mode == ProcessingMode.HYBRID_CONSENSUS:
                logger.info("🎯 Procesando con estrategia HYBRID CONSENSUS")
                result = await self._process_hybrid_consensus(
                    document_content, fields, prompt_general
                )
            else:
                raise ValueError(f"Modo de procesamiento no soportado: {processing_mode}")
            
            # Calcular tiempo total
            processing_time_ms = int((time.time() - start_time) * 1000)
            result.processing_time_ms = processing_time_ms
            
            logger.info(f"✅ Procesamiento de IA completado en {processing_time_ms}ms")
            logger.info(f"📊 Campos extraídos: {len(result.extraction_data)}")
            logger.info(f"🔍 Banderas de revisión: {len(result.review_flags)}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en el procesamiento de IA: {str(e)}")
            raise
    
    async def _process_dual_service(
        self,
        document_content: bytes,
        fields: List[FieldDefinition],
        prompt_general: str
    ) -> ExtractionResult:
        """Procesar documento usando ambos servicios en paralelo"""
        logger.info("🔄 Iniciando procesamiento DUAL SERVICE")
        
        # Ejecutar ambos servicios en paralelo
        openai_task = self._process_with_openai(document_content, fields, prompt_general)
        doc_intelligence_task = self._process_with_document_intelligence(
            document_content, fields, prompt_general
        )
        
        openai_result, doc_intelligence_result = await asyncio.gather(
            openai_task, doc_intelligence_task, return_exceptions=True
        )
        
        # Analizar resultados y crear consenso
        extraction_data = []
        review_flags = []
        
        for field in fields:
            field_name = field.name
            openai_value = None
            doc_intelligence_value = None
            
            # Obtener valores de cada servicio
            if not isinstance(openai_result, Exception):
                openai_value = self._get_field_value(openai_result, field_name)
            
            if not isinstance(doc_intelligence_result, Exception):
                doc_intelligence_value = self._get_field_value(doc_intelligence_result, field_name)
            
            # Crear campo con consenso
            field_result = self._create_consensus_field(
                field_name, openai_value, doc_intelligence_value, field
            )
            extraction_data.append(field_result)
            
            # Marcar para revisión si hay discrepancias
            if (openai_value is not None and doc_intelligence_value is not None and 
                openai_value != doc_intelligence_value):
                review_flags.append(f"Discrepancia en campo '{field_name}' entre servicios")
        
        return ExtractionResult(
            extraction_data=extraction_data,
            pages_processed=1,  # Por defecto, ajustar según el documento
            review_flags=review_flags,
            processing_time_ms=0,  # Se calcula después
            strategy_used="dual_service"
        )
    
    async def _process_gpt_vision_only(
        self,
        document_content: bytes,
        fields: List[FieldDefinition],
        prompt_general: str
    ) -> ExtractionResult:
        """Procesar documento usando solo Azure OpenAI GPT-4 Vision con estrategia cascada"""
        logger.info("👁️ Iniciando procesamiento GPT VISION ONLY con estrategia cascada")
        logger.info(f"   📊 Tamaño del documento: {len(document_content)} bytes")
        logger.info(f"   🔍 Primeros bytes: {document_content[:10]}")
        
        try:
            # Usar procesamiento cascada para mantener contexto entre páginas
            logger.info("   🔄 Llamando a _process_with_openai_cascade...")
            result = await self._process_with_openai_cascade(document_content, fields, prompt_general)
            logger.info("   ✅ _process_with_openai_cascade completado exitosamente")
            
            extraction_data = []
            for field in fields:
                field_value = self._get_field_value(result, field.name)
                field_result = ExtractionField(
                    name=field.name,
                    value=field_value,
                    confidence=0.9,  # Alta confianza para GPT-4 Vision
                    review_required=False,
                    source_strategy="gpt_vision_only_cascade",
                    extraction_time_ms=0
                )
                extraction_data.append(field_result)
            
            return ExtractionResult(
                extraction_data=extraction_data,
                pages_processed=result.get('pages_processed', 1),
                review_flags=[],
                processing_time_ms=0,
                strategy_used="gpt_vision_only_cascade"
            )
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento GPT Vision Cascada: {str(e)}")
            raise
    
    async def _process_hybrid_consensus(
        self,
        document_content: bytes,
        fields: List[FieldDefinition],
        prompt_general: str
    ) -> ExtractionResult:
        """Procesar documento usando consenso híbrido"""
        logger.info("🎯 Iniciando procesamiento HYBRID CONSENSUS")
        
        # Obtener resultados de ambos servicios
        openai_result = await self._process_with_openai(document_content, fields, prompt_general)
        doc_intelligence_result = await self._process_with_document_intelligence(
            document_content, fields, prompt_general
        )
        
        extraction_data = []
        review_flags = []
        
        for field in fields:
            field_name = field.name
            openai_value = self._get_field_value(openai_result, field_name)
            doc_intelligence_value = self._get_field_value(doc_intelligence_result, field_name)
            
            # Lógica de consenso híbrido
            if openai_value is not None and doc_intelligence_value is not None:
                if openai_value == doc_intelligence_value:
                    # Consenso perfecto
                    final_value = openai_value
                    confidence = 0.95
                    review_required = False
                else:
                    # Discrepancia - usar OpenAI como autoridad
                    final_value = openai_value
                    confidence = 0.8
                    review_required = True
                    review_flags.append(f"Discrepancia en '{field_name}': OpenAI='{openai_value}', DI='{doc_intelligence_value}'")
            elif openai_value is not None:
                # Solo OpenAI tiene valor
                final_value = openai_value
                confidence = 0.85
                review_required = False
            elif doc_intelligence_value is not None:
                # Solo Document Intelligence tiene valor
                final_value = doc_intelligence_value
                confidence = 0.75
                review_required = True
                review_flags.append(f"Campo '{field_name}' solo extraído por Document Intelligence")
            else:
                # Ningún servicio extrajo valor
                final_value = None
                confidence = 0.0
                review_required = True
                review_flags.append(f"Campo '{field_name}' no extraído por ningún servicio")
            
            field_result = ExtractionField(
                name=field_name,
                value=final_value,
                confidence=confidence,
                review_required=review_required,
                source_strategy="hybrid_consensus",
                extraction_time_ms=0
            )
            extraction_data.append(field_result)
        
        return ExtractionResult(
            extraction_data=extraction_data,
            pages_processed=1,
            review_flags=review_flags,
            processing_time_ms=0,
            strategy_used="hybrid_consensus"
        )
    
    async def _process_with_openai(
        self,
        document_content: bytes,
        fields: List[FieldDefinition],
        prompt_general: str
    ) -> Dict[str, Any]:
        """Procesar documento con Azure OpenAI GPT-4 Vision"""
        logger.info("🤖 Procesando con Azure OpenAI GPT-4 Vision")
        
        try:
            # Convertir documento a base64
            document_b64 = base64.b64encode(document_content).decode('utf-8')
            
            # Construir prompt específico
            fields_description = self._build_fields_description(fields)
            full_prompt = f"{prompt_general}\n\n{fields_description}"
            
            # Llamar a OpenAI
            response = await self.openai_client.process_document_vision(
                document_b64=document_b64,
                prompt=full_prompt,
                fields=fields
            )
            
            logger.info("✅ Procesamiento con OpenAI completado exitosamente")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento OpenAI: {str(e)}")
            raise
    
    async def _process_with_openai_cascade(
        self,
        document_content: bytes,
        fields: List[FieldDefinition],
        prompt_general: str
    ) -> Dict[str, Any]:
        """Procesar documento con Azure OpenAI GPT-4 Vision usando estrategia cascada para mantener contexto"""
        logger.info("🔄 Iniciando procesamiento GPT-4 Vision con estrategia cascada")
        logger.info(f"   📊 Tamaño del documento: {len(document_content)} bytes")
        logger.info(f"   🔍 Primeros bytes: {document_content[:10]}")
        
        try:
            # Importar convertidores inteligentes
            logger.info("   📦 Importando convertidores...")
            from app.utils.document_converter import DocumentConverter
            from app.utils.office_converter import OfficeConverter
            logger.info("   ✅ Convertidores importados correctamente")
            
            # Determinar tipo de archivo y usar conversor apropiado
            logger.info("🔍 Determinando tipo de archivo para conversión...")
            
            # Intentar detectar tipo por contenido (método simple)
            if document_content.startswith(b'%PDF'):
                # Es un PDF
                logger.info("📄 Archivo detectado como PDF, usando DocumentConverter")
                converter = DocumentConverter()
                images = converter.pdf_to_images_png(document_content)
            elif document_content.startswith(b'PK'):
                # Es un archivo Office (ZIP)
                logger.info("📊 Archivo detectado como Office (ZIP), usando OfficeConverter")
                converter = OfficeConverter()
                images = converter.office_to_images_png(document_content)
            else:
                # Intentar con OfficeConverter por defecto (más versátil)
                logger.info("🔍 Tipo no detectado, intentando con OfficeConverter")
                logger.info(f"   🔍 Bytes de inicio: {document_content[:20]}")
                converter = OfficeConverter()
                images = converter.office_to_images_png(document_content)
            
            logger.info(f"🔄 Convertidas {len(images)} páginas del documento a imágenes")
            
            if len(images) <= 5:
                # Una sola petición para documentos pequeños
                logger.info(f"📄 Documento pequeño ({len(images)} páginas), procesando en una petición")
                return await self._process_single_batch(images, fields, prompt_general)
            else:
                # Procesamiento cascada para documentos grandes
                logger.info(f"📚 Documento grande ({len(images)} páginas), procesando en cascada")
                return await self._process_cascade_batches(images, fields, prompt_general)
                
        except Exception as e:
            logger.error(f"❌ Error en procesamiento cascada: {str(e)}")
            raise
    
    async def _process_single_batch(
        self,
        images: List[str],
        fields: List[FieldDefinition],
        prompt_general: str
    ) -> Dict[str, Any]:
        """Procesar un lote de imágenes en una sola petición"""
        logger.info(f"📄 Procesando {len(images)} imágenes en una sola petición")
        
        try:
            # Verificar si las imágenes ya están en base64 o son rutas de archivo
            logger.info(f"   🔍 Verificando formato de las imágenes...")
            logger.info(f"   📊 Primera imagen (primeros 50 chars): {images[0][:50] if images else 'No hay imágenes'}")
            
            # Las imágenes del OfficeConverter ya están en base64
            if images and images[0].startswith('data:image') or len(images[0]) > 1000:
                # Ya están en base64, usar directamente
                logger.info(f"   ✅ Imágenes ya están en base64, usando directamente")
                images_b64 = images
            else:
                # Convertir a base64 si son rutas de archivo
                logger.info(f"   🔄 Convirtiendo rutas de archivo a base64...")
                images_b64 = []
                for img_path in images:
                    try:
                        with open(img_path, 'rb') as img_file:
                            img_data = img_file.read()
                            img_b64 = base64.b64encode(img_data).decode('utf-8')
                            images_b64.append(img_b64)
                    except Exception as img_error:
                        logger.warning(f"   ⚠️ Error convirtiendo imagen {img_path}: {str(img_error)}")
                        continue
            
            if not images_b64:
                raise Exception("No se pudieron procesar las imágenes")
            
            logger.info(f"   ✅ {len(images_b64)} imágenes preparadas para GPT-4o")
            
            # Construir prompt específico
            fields_description = self._build_fields_description(fields)
            full_prompt = f"{prompt_general}\n\n{fields_description}"
            
            # Llamar a OpenAI con TODAS las imágenes del lote
            logger.info(f"   🖼️ Enviando {len(images_b64)} imágenes a GPT-4o para análisis conjunto")
            
            # Crear prompt mejorado para múltiples páginas
            enhanced_prompt = f"""
            {full_prompt}
            
            📄 INSTRUCCIONES ESPECIALES PARA MÚLTIPLES PÁGINAS:
            - Estás analizando {len(images_b64)} páginas del mismo documento
            - Cada página puede contener información diferente
            - Combina y consolida la información de TODAS las páginas
            - Si un campo aparece en múltiples páginas, usa la información más completa
            - NO devuelvas null a menos que el campo no aparezca en NINGUNA página
            - Busca información complementaria entre las páginas
            - Analiza cada imagen secuencialmente para construir una respuesta completa
            """
            
            # Enviar TODAS las imágenes del lote a GPT-4o
            response = await self.openai_client.process_multiple_images_vision(
                images_b64=images_b64,
                prompt=enhanced_prompt,
                fields=fields
            )
            
            # Agregar información de que se analizaron múltiples páginas
            response['multi_page_analysis'] = True
            response['total_pages_analyzed'] = len(images_b64)
            
            # Agregar información de páginas procesadas
            response['pages_processed'] = len(images)
            
            logger.info(f"✅ Procesamiento de lote único completado: {len(images)} páginas")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento de lote único: {str(e)}")
            raise
    
    async def _process_cascade_batches(
        self,
        images: List[str],
        fields: List[FieldDefinition],
        prompt_general: str
    ) -> Dict[str, Any]:
        """Procesar imágenes en lotes usando estrategia cascada para mantener contexto"""
        logger.info(f"🔄 Iniciando procesamiento cascada para {len(images)} imágenes")
        
        try:
            # Procesar primer lote (base)
            logger.info("🔄 Procesando lote base (páginas 1-5)")
            base_extraction = await self._process_single_batch(images[0:5], fields, prompt_general)
            
            # Procesar lotes subsiguientes con referencia al anterior
            for batch_idx in range(5, len(images), 5):
                batch = images[batch_idx:batch_idx + 5]
                current_pages = f"{batch_idx+1}-{min(batch_idx+5, len(images))}"
                
                logger.info(f"🔄 Procesando lote {batch_idx//5 + 2} (páginas {current_pages})")
                
                # Prompt que referencia la extracción anterior
                reference_prompt = f"""
                {prompt_general}
                
                🔄 INFORMACIÓN EXTRAÍDA ANTERIORMENTE:
                {self._format_extraction_for_prompt(base_extraction)}
                
                📄 INSTRUCCIONES ESPECIALES:
                - Complementa la información anterior con datos de las páginas {current_pages}
                - Si hay contradicciones, prioriza la información más reciente
                - Mantén la coherencia con los datos ya extraídos
                - Agrega nuevos campos si los encuentras
                """
                
                batch_extraction = await self._process_single_batch(batch, fields, reference_prompt)
                base_extraction = self._merge_extractions(base_extraction, batch_extraction)
                
                logger.info(f"✅ Lote {batch_idx//5 + 2} procesado y consolidado")
            
            # Agregar información de páginas procesadas
            base_extraction['pages_processed'] = len(images)
            
            logger.info(f"✅ Procesamiento cascada completado: {len(images)} páginas procesadas")
            return base_extraction
                
        except Exception as e:
            logger.error(f"❌ Error en procesamiento cascada: {str(e)}")
            raise
    
    def _format_extraction_for_prompt(self, extraction: Dict[str, Any]) -> str:
        """Formatear extracción para incluir en prompt de referencia"""
        try:
            formatted = []
            for key, value in extraction.items():
                if key not in ['pages_processed', '_rid', '_etag', '_ts'] and value is not None:
                    formatted.append(f"- {key}: {value}")
            return "\n".join(formatted)
        except Exception as e:
            logger.warning(f"⚠️ Error formateando extracción para prompt: {str(e)}")
            return "Información anterior no disponible"
    
    def _merge_extractions(self, base: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """Combinar extracciones manteniendo coherencia"""
        try:
            merged = base.copy()
            
            for key, value in new.items():
                if key in ['pages_processed', '_rid', '_etag', '_ts']:
                    continue
                    
                if key in merged:
                    # Si el campo ya existe, usar el valor más reciente si no es None
                    if value is not None:
                        merged[key] = value
                else:
                    # Nuevo campo
                    merged[key] = value
            
            logger.info(f"🔄 Extracciones combinadas: {len(merged)} campos totales")
            return merged
            
        except Exception as e:
            logger.error(f"❌ Error combinando extracciones: {str(e)}")
            return base
    
    async def _process_with_document_intelligence(
        self,
        document_content: bytes,
        fields: List[FieldDefinition],
        prompt_general: str
    ) -> Dict[str, Any]:
        """Procesar documento con Azure Document Intelligence"""
        logger.info("📄 Procesando con Azure Document Intelligence")
        
        try:
            # Llamar a Document Intelligence
            response = await self.doc_intelligence_client.process_document(
                document_content=document_content,
                fields=fields,
                prompt_general=prompt_general
            )
            
            logger.info("✅ Procesamiento con Document Intelligence completado exitosamente")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento Document Intelligence: {str(e)}")
            raise
    
    def _build_fields_description(self, fields: List[FieldDefinition]) -> str:
        """Construir descripción de campos para el prompt"""
        fields_desc = "Campos a extraer:\n"
        for field in fields:
            fields_desc += f"- {field.name} ({field.type}): {field.description}\n"
        return fields_desc
    
    def _get_field_value(self, result: Dict[str, Any], field_name: str) -> Any:
        """Obtener valor de un campo específico del resultado"""
        try:
            return result.get(field_name)
        except (KeyError, AttributeError):
            return None
    
    def _create_consensus_field(
        self,
        field_name: str,
        openai_value: Any,
        doc_intelligence_value: Any,
        field_definition: FieldDefinition
    ) -> ExtractionField:
        """Crear campo con consenso entre servicios"""
        
        # Determinar valor final y confianza
        if openai_value is not None and doc_intelligence_value is not None:
            if openai_value == doc_intelligence_value:
                final_value = openai_value
                confidence = 0.95
                review_required = False
            else:
                # Discrepancia - usar OpenAI como autoridad
                final_value = openai_value
                confidence = 0.8
                review_required = True
        elif openai_value is not None:
            final_value = openai_value
            confidence = 0.85
            review_required = False
        elif doc_intelligence_value is not None:
            final_value = doc_intelligence_value
            confidence = 0.75
            review_required = False
        else:
            final_value = None
            confidence = 0.0
            review_required = True
        
        return ExtractionField(
            name=field_name,
            value=final_value,
            confidence=confidence,
            review_required=review_required,
            source_strategy="dual_service",
            extraction_time_ms=0
        )
