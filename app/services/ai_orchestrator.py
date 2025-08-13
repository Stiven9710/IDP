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
from app.utils.azure_clients import AzureOpenAIClient, DocumentIntelligenceClient

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


class AIOrchestratorService:
    """Servicio orquestador de IA para procesamiento de documentos"""
    
    def __init__(self):
        """Inicializar el orquestador de IA"""
        self.openai_client = AzureOpenAIClient()
        self.doc_intelligence_client = DocumentIntelligenceClient()
        
        logger.info("🤖 AIOrchestratorService inicializado correctamente")
    
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
        """Procesar documento usando solo Azure OpenAI GPT-4 Vision"""
        logger.info("👁️ Iniciando procesamiento GPT VISION ONLY")
        
        try:
            result = await self._process_with_openai(document_content, fields, prompt_general)
            
            extraction_data = []
            for field in fields:
                field_value = self._get_field_value(result, field.name)
                field_result = ExtractionField(
                    name=field.name,
                    value=field_value,
                    confidence=0.9,  # Alta confianza para GPT-4 Vision
                    review_required=False,
                    source_strategy="gpt_vision_only",
                    extraction_time_ms=0
                )
                extraction_data.append(field_result)
            
            return ExtractionResult(
                extraction_data=extraction_data,
                pages_processed=1,
                review_flags=[],
                processing_time_ms=0,
                strategy_used="gpt_vision_only"
            )
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento GPT Vision: {str(e)}")
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
