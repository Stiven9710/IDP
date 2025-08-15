"""
Clientes de Azure para servicios de IA
"""

import asyncio
import base64
import json
import logging
from typing import Dict, Any, List, Optional
import httpx

from app.core.config import settings
from app.models.request import FieldDefinition

# Configurar logging
logger = logging.getLogger(__name__)


class AzureOpenAIClient:
    """Cliente para Azure OpenAI GPT-4 Vision"""
    
    def __init__(self):
        """Inicializar cliente de Azure OpenAI"""
        self.endpoint = settings.azure_openai_endpoint
        self.api_key = settings.azure_openai_api_key
        self.api_version = settings.azure_openai_api_version
        self.deployment_name = settings.azure_openai_deployment_name
        
        if not self.endpoint or not self.api_key:
            logger.warning("⚠️ Azure OpenAI no configurado completamente")
        else:
            logger.info("🤖 Azure OpenAI Client inicializado correctamente")
    
    async def process_document_vision(
        self,
        document_b64: str,
        prompt: str,
        fields: List[FieldDefinition]
    ) -> Dict[str, Any]:
        """
        Procesar documento usando GPT-4 Vision
        
        Args:
            document_b64: Documento en base64
            prompt: Prompt para la extracción
            fields: Campos a extraer
            
        Returns:
            Diccionario con los campos extraídos
        """
        logger.info("🤖 Iniciando procesamiento con Azure OpenAI GPT-4 Vision")
        
        try:
            # Construir mensaje para GPT-4 Vision
            messages = [
                {
                    "role": "system",
                    "content": "Eres un experto en extracción de datos de documentos. Debes extraer exactamente los campos solicitados y devolver la respuesta en formato JSON válido."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{document_b64}"
                            }
                        }
                    ]
                }
            ]
            
            # Configurar parámetros de la API
            payload = {
                "messages": messages,
                "max_tokens": 4000,
                "temperature": 0.1,
                "top_p": 0.95,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }
            
            # URL de la API
            url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/chat/completions"
            params = {"api-version": self.api_version}
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            
            logger.info(f"🌐 Llamando a Azure OpenAI: {url}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    params=params,
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Extraer contenido de la respuesta
                content = result["choices"][0]["message"]["content"]
                logger.info(f"📝 Respuesta de OpenAI: {content[:200]}...")
                
                # Parsear JSON de la respuesta
                try:
                    extracted_data = json.loads(content)
                    logger.info("✅ Datos extraídos exitosamente de OpenAI")
                    return extracted_data
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Error parseando JSON de OpenAI: {str(e)}")
                    # Intentar extraer datos del texto
                    return self._extract_fields_from_text(content, fields)
                    
        except Exception as e:
            logger.error(f"❌ Error en Azure OpenAI: {str(e)}")
            raise
    
    def _extract_fields_from_text(self, text: str, fields: List[FieldDefinition]) -> Dict[str, Any]:
        """Extraer campos del texto cuando no se puede parsear JSON"""
        logger.warning("⚠️ Intentando extraer campos del texto plano")
        
        extracted_data = {}
        for field in fields:
            # Búsqueda simple por nombre del campo
            field_name_lower = field.name.lower()
            if field_name_lower in text.lower():
                # Extraer valor aproximado
                extracted_data[field.name] = f"Valor extraído para {field.name}"
            else:
                extracted_data[field.name] = None
        
        return extracted_data


class DocumentIntelligenceClient:
    """Cliente para Azure Document Intelligence"""
    
    def __init__(self):
        """Inicializar cliente de Document Intelligence"""
        self.endpoint = settings.azure_document_intelligence_endpoint
        self.api_key = settings.azure_document_intelligence_api_key
        
        if not self.endpoint or not self.api_key:
            logger.warning("⚠️ Azure Document Intelligence no configurado completamente")
        else:
            logger.info("📄 Azure Document Intelligence Client inicializado correctamente")
    
    async def process_document(
        self,
        document_content: bytes,
        fields: List[FieldDefinition],
        prompt_general: str
    ) -> Dict[str, Any]:
        """
        Procesar documento usando Azure Document Intelligence
        
        Args:
            document_content: Contenido del documento en bytes
            fields: Campos a extraer
            prompt_general: Prompt general para la extracción
            
        Returns:
            Diccionario con los campos extraídos
        """
        logger.info("📄 Iniciando procesamiento con Azure Document Intelligence")
        
        try:
            # URL para el análisis de documentos
            url = f"{self.endpoint}/formrecognizer/documentModels/prebuilt-document:analyze"
            headers = {
                "Content-Type": "application/octet-stream",
                "Ocp-Apim-Subscription-Key": self.api_key
            }
            
            logger.info(f"🌐 Llamando a Document Intelligence: {url}")
            
            async with httpx.AsyncClient() as client:
                # Iniciar análisis
                response = await client.post(
                    url,
                    headers=headers,
                    content=document_content,
                    timeout=60.0
                )
                
                response.raise_for_status()
                
                # Obtener ID de operación
                operation_location = response.headers.get("Operation-Location")
                if not operation_location:
                    raise ValueError("No se recibió Operation-Location en la respuesta")
                
                logger.info(f"🔄 Operación iniciada: {operation_location}")
                
                # Esperar resultados
                result = await self._wait_for_completion(operation_location)
                
                # Extraer campos relevantes
                extracted_data = self._extract_fields_from_result(result, fields)
                
                logger.info("✅ Document Intelligence completado exitosamente")
                return extracted_data
                
        except Exception as e:
            logger.error(f"❌ Error en Document Intelligence: {str(e)}")
            raise
    
    async def _wait_for_completion(self, operation_url: str) -> Dict[str, Any]:
        """Esperar a que se complete la operación de análisis"""
        logger.info("⏳ Esperando completación de Document Intelligence...")
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key
        }
        
        max_attempts = 30
        attempt = 0
        
        async with httpx.AsyncClient() as client:
            while attempt < max_attempts:
                try:
                    response = await client.get(operation_url, headers=headers)
                    response.raise_for_status()
                    
                    result = response.json()
                    status = result.get("status")
                    
                    if status == "succeeded":
                        logger.info("✅ Document Intelligence completado")
                        return result
                    elif status == "failed":
                        error = result.get("error", {})
                        raise Exception(f"Document Intelligence falló: {error}")
                    elif status in ["running", "notStarted"]:
                        logger.info(f"🔄 Estado: {status}, esperando...")
                        await asyncio.sleep(2)
                        attempt += 1
                    else:
                        logger.warning(f"⚠️ Estado desconocido: {status}")
                        await asyncio.sleep(2)
                        attempt += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error consultando estado: {str(e)}")
                    raise
        
        raise TimeoutError("Document Intelligence no completó en el tiempo esperado")
    
    def _extract_fields_from_result(
        self, 
        result: Dict[str, Any], 
        fields: List[FieldDefinition]
    ) -> Dict[str, Any]:
        """Extraer campos específicos del resultado de Document Intelligence"""
        logger.info("🔍 Extrayendo campos del resultado de Document Intelligence")
        
        extracted_data = {}
        
        try:
            # Obtener contenido del documento
            content = result.get("analyzeResult", {}).get("content", "")
            
            # Para cada campo solicitado, buscar en el contenido
            for field in fields:
                field_name = field.name
                field_value = self._search_field_in_content(content, field)
                extracted_data[field_name] = field_value
                
                logger.info(f"📝 Campo '{field_name}': {field_value}")
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo campos: {str(e)}")
            # Devolver valores por defecto
            for field in fields:
                extracted_data[field.name] = None
        
        return extracted_data
    
    def _search_field_in_content(self, content: str, field: FieldDefinition) -> Any:
        """Buscar un campo específico en el contenido del documento"""
        try:
            # Búsqueda simple por nombre del campo
            field_name_lower = field.name.lower()
            content_lower = content.lower()
            
            if field_name_lower in content_lower:
                # Encontrar posición del campo
                start_pos = content_lower.find(field_name_lower)
                
                # Extraer texto alrededor del campo
                context_start = max(0, start_pos - 50)
                context_end = min(len(content), start_pos + len(field_name_lower) + 100)
                context = content[context_start:context_end]
                
                # Intentar extraer el valor
                value = self._extract_value_from_context(context, field)
                return value if value else f"Campo '{field.name}' encontrado"
            else:
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ Error buscando campo '{field.name}': {str(e)}")
            return None
    
    def _extract_value_from_context(self, context: str, field: FieldDefinition) -> Any:
        """Extraer valor del contexto basado en el tipo de campo"""
        try:
            # Lógica básica de extracción según el tipo
            if field.type == "number":
                # Buscar números en el contexto
                import re
                numbers = re.findall(r'\d+(?:\.\d+)?', context)
                return float(numbers[0]) if numbers else None
            elif field.type == "date":
                # Buscar fechas en el contexto
                import re
                dates = re.findall(r'\d{4}-\d{2}-\d{2}', context)
                return dates[0] if dates else None
            elif field.type == "boolean":
                # Buscar valores booleanos
                if "true" in context.lower() or "si" in context.lower():
                    return True
                elif "false" in context.lower() or "no" in context.lower():
                    return False
                return None
            else:
                # Para strings y arrays, devolver el contexto
                return context.strip()
                
        except Exception as e:
            logger.warning(f"⚠️ Error extrayendo valor para '{field.name}': {str(e)}")
            return None
