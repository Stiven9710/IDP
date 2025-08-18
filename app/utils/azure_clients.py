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
        fields: List[FieldDefinition],
        processing_mode: str = "gpt_vision_only"
    ) -> Dict[str, Any]:
        """
        Procesar documento usando diferentes estrategias según el modo
        
        Args:
            document_b64: Documento en base64 (PDF)
            prompt: Prompt para la extracción
            fields: Campos a extraer
            processing_mode: Modo de procesamiento (gpt_vision_only, dual_service, hybrid_consensus)
            
        Returns:
            Diccionario con los campos extraídos
        """
        logger.info(f"🤖 Iniciando procesamiento con modo: {processing_mode}")
        
        try:
            # Decodificar base64 a bytes
            import base64
            pdf_bytes = base64.b64decode(document_b64)
            
            if processing_mode == "gpt_vision_only":
                return await self._process_gpt_vision_only(pdf_bytes, prompt, fields)
            elif processing_mode == "dual_service":
                return await self._process_dual_service(pdf_bytes, prompt, fields)
            elif processing_mode == "hybrid_consensus":
                return await self._process_hybrid_consensus(pdf_bytes, prompt, fields)
            else:
                raise ValueError(f"Modo de procesamiento no soportado: {processing_mode}")
                
        except Exception as e:
            logger.error(f"❌ Error en procesamiento: {str(e)}")
            raise
    
    async def _process_gpt_vision_only(
        self, 
        pdf_bytes: bytes, 
        prompt: str, 
        fields: List[FieldDefinition]
    ) -> Dict[str, Any]:
        """Procesar con GPT-4o usando imágenes del PDF"""
        logger.info("🖼️ Procesando con GPT-4o (PDF → Imágenes PNG)")
        
        try:
            # Importar el conversor de documentos
            from app.utils.document_converter import DocumentConverter
            
            # Convertir PDF a imágenes PNG optimizadas
            converter = DocumentConverter()
            optimal_dpi = converter.get_optimal_dpi_for_document(pdf_bytes)
            
            logger.info(f"🎯 DPI óptimo determinado: {optimal_dpi}")
            
            # Convertir PDF a imágenes PNG
            images_base64 = converter.pdf_to_images_png(pdf_bytes, dpi=optimal_dpi)
            
            if not images_base64:
                raise ValueError("No se pudieron generar imágenes del PDF")
            
            logger.info(f"🖼️ {len(images_base64)} imágenes generadas para GPT-4o")
            
            # Procesar cada imagen con GPT-4o
            all_extractions = []
            
            for i, image_base64 in enumerate(images_base64):
                logger.info(f"🔄 Procesando imagen {i+1}/{len(images_base64)}")
                
                # Enviar imagen a GPT-4o
                extraction = await self._send_image_to_gpt4o(image_base64, prompt, fields)
                all_extractions.append(extraction)
            
            # Combinar resultados de todas las imágenes
            combined_result = self._combine_image_extractions(all_extractions, fields)
            
            logger.info("✅ Procesamiento GPT-4o completado exitosamente")
            return combined_result
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento GPT-4o: {str(e)}")
            raise
    
    async def _send_image_to_gpt4o(
        self, 
        image_base64: str, 
        prompt: str, 
        fields: List[FieldDefinition]
    ) -> Dict[str, Any]:
        """Enviar imagen individual a GPT-4o"""
        
        # Construir mensaje para GPT-4o con imagen
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
                        "text": f"""
                        {prompt}
                        
                        INSTRUCCIONES:
                        - Analiza la imagen del documento
                        - Extrae los campos solicitados
                        - Responde SOLO con un JSON válido
                        - Si un campo no está presente, usa null
                        - Para fechas, usa formato YYYY-MM-DD
                        - Para montos, extrae solo el valor numérico
                        """
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_base64
                        }
                    }
                ]
            }
        ]
        
        # Configurar parámetros de la API para GPT-4o
        payload = {
            "messages": messages,
            "max_tokens": 4000,
            "temperature": 0.1,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        # URL de la API
        endpoint = self.endpoint.rstrip('/')
        url = f"{endpoint}/openai/deployments/{self.deployment_name}/chat/completions"
        params = {"api-version": self.api_version}
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        logger.info(f"🌐 Enviando imagen a GPT-4o: {url}")
        
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
            logger.info(f"📝 Respuesta de GPT-4o: {content[:200]}...")
            
            # Parsear JSON de la respuesta
            try:
                extracted_data = json.loads(content)
                logger.info("✅ Datos extraídos exitosamente de GPT-4o")
                return extracted_data
            except json.JSONDecodeError as e:
                logger.error(f"❌ Error parseando JSON de GPT-4o: {str(e)}")
                return self._extract_fields_from_text(content, fields)
    
    def _combine_image_extractions(
        self, 
        extractions: List[Dict[str, Any]], 
        fields: List[FieldDefinition]
    ) -> Dict[str, Any]:
        """Combinar extracciones de múltiples imágenes"""
        logger.info(f"🔗 Combinando {len(extractions)} extracciones de imágenes")
        
        if len(extractions) == 1:
            return extractions[0]
        
        # Combinar múltiples extracciones
        combined_result = {}
        
        for field in fields:
            field_name = field.name
            field_values = []
            
            # Recolectar valores del campo de todas las imágenes
            for extraction in extractions:
                if field_name in extraction and extraction[field_name] is not None:
                    field_values.append(extraction[field_name])
            
            # Determinar valor final del campo
            if not field_values:
                combined_result[field_name] = None
            elif len(field_values) == 1:
                combined_result[field_name] = field_values[0]
            else:
                # Múltiples valores, usar el más común o el primero
                combined_result[field_name] = field_values[0]
                logger.info(f"🔄 Campo {field_name}: múltiples valores encontrados, usando el primero")
        
        logger.info("✅ Combinación de extracciones completada")
        return combined_result
    
    async def _process_dual_service(
        self, 
        pdf_bytes: bytes, 
        prompt: str, 
        fields: List[FieldDefinition]
    ) -> Dict[str, Any]:
        """Procesar con Document Intelligence (texto)"""
        logger.info("📄 Procesando con Document Intelligence (texto)")
        
        try:
            # Usar Document Intelligence para extraer texto
            doc_intelligence_client = DocumentIntelligenceClient()
            extracted_text = await doc_intelligence_client.extract_text_from_pdf(pdf_bytes)
            
            if not extracted_text:
                raise ValueError("No se pudo extraer texto del PDF")
            
            logger.info(f"📝 Texto extraído: {len(extracted_text)} caracteres")
            
            # Enviar texto a GPT-4o para análisis
            messages = [
                {
                    "role": "system",
                    "content": "Eres un experto en extracción de datos de documentos. Debes extraer exactamente los campos solicitados y devolver la respuesta en formato JSON válido."
                },
                {
                    "role": "user",
                    "content": f"""
                    {prompt}
                    
                    TEXTO DEL DOCUMENTO:
                    {extracted_text}
                    
                    INSTRUCCIONES:
                    - Analiza el texto del documento
                    - Extrae los campos solicitados
                    - Responde SOLO con un JSON válido
                    - Si un campo no está presente, usa null
                    - Para fechas, usa formato YYYY-MM-DD
                    - Para montos, extrae solo el valor numérico
                    """
                }
            ]
            
            # Configurar parámetros de la API para GPT-4o (solo texto)
            payload = {
                "messages": messages,
                "max_tokens": 4000,
                "temperature": 0.1,
                "top_p": 0.95,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }
            
            # URL de la API
            endpoint = self.endpoint.rstrip('/')
            url = f"{endpoint}/openai/deployments/{self.deployment_name}/chat/completions"
            params = {"api-version": self.api_version}
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            
            logger.info(f"🌐 Enviando texto a GPT-4o: {url}")
            
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
                logger.info(f"📝 Respuesta de GPT-4o: {content[:200]}...")
                
                # Parsear JSON de la respuesta
                try:
                    extracted_data = json.loads(content)
                    logger.info("✅ Datos extraídos exitosamente de GPT-4o")
                    return extracted_data
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Error parseando JSON de GPT-4o: {str(e)}")
                    return self._extract_fields_from_text(content, fields)
                    
        except Exception as e:
            logger.error(f"❌ Error en procesamiento dual_service: {str(e)}")
            raise
    
    async def _process_hybrid_consensus(
        self, 
        pdf_bytes: bytes, 
        prompt: str, 
        fields: List[FieldDefinition]
    ) -> Dict[str, Any]:
        """Procesar con ambas estrategias y validación cruzada"""
        logger.info("🔄 Procesando con estrategia híbrida (consenso)")
        
        try:
            # Ejecutar ambas estrategias en paralelo
            import asyncio
            
            # Crear tareas para ejecutar ambas estrategias
            vision_task = asyncio.create_task(
                self._process_gpt_vision_only(pdf_bytes, prompt, fields)
            )
            text_task = asyncio.create_task(
                self._process_dual_service(pdf_bytes, prompt, fields)
            )
            
            # Esperar que ambas completen
            vision_result, text_result = await asyncio.gather(
                vision_task, text_task, return_exceptions=True
            )
            
            # Verificar si alguna falló
            if isinstance(vision_result, Exception):
                logger.warning(f"⚠️ Estrategia vision falló: {vision_result}")
                vision_result = {}
            
            if isinstance(text_result, Exception):
                logger.warning(f"⚠️ Estrategia texto falló: {text_result}")
                text_result = {}
            
            # Generar consenso entre ambas estrategias
            consensus_result = self._generate_consensus(
                vision_result, text_result, fields
            )
            
            logger.info("✅ Procesamiento híbrido completado exitosamente")
            return consensus_result
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento híbrido: {str(e)}")
            raise
    
    def _generate_consensus(
        self, 
        vision_result: Dict[str, Any], 
        text_result: Dict[str, Any], 
        fields: List[FieldDefinition]
    ) -> Dict[str, Any]:
        """Generar consenso entre resultados de vision y texto"""
        logger.info("🔍 Generando consenso entre estrategias")
        
        consensus_result = {}
        
        for field in fields:
            field_name = field.name
            vision_value = vision_result.get(field_name)
            text_value = text_result.get(field_name)
            
            # Lógica de consenso
            if vision_value == text_value:
                # Ambos coinciden, alta confianza
                consensus_result[field_name] = {
                    "value": vision_value,
                    "confidence": "high",
                    "source": "consensus",
                    "vision_value": vision_value,
                    "text_value": text_value
                }
                logger.info(f"✅ Consenso alto para {field_name}: {vision_value}")
                
            elif vision_value is not None and text_value is not None:
                # Ambos tienen valores diferentes, usar el más detallado
                if isinstance(vision_value, str) and isinstance(text_value, str):
                    if len(vision_value) > len(text_value):
                        selected_value = vision_value
                        selected_source = "vision"
                    else:
                        selected_value = text_value
                        selected_source = "text"
                else:
                    # Usar vision por defecto para campos no-string
                    selected_value = vision_value
                    selected_source = "vision"
                
                consensus_result[field_name] = {
                    "value": selected_value,
                    "confidence": "medium",
                    "source": selected_source,
                    "vision_value": vision_value,
                    "text_value": text_value,
                    "note": "Valores diferentes, usando el más detallado"
                }
                logger.info(f"⚠️ Consenso medio para {field_name}: {selected_value} (fuente: {selected_source})")
                
            elif vision_value is not None:
                # Solo vision tiene valor
                consensus_result[field_name] = {
                    "value": vision_value,
                    "confidence": "medium",
                    "source": "vision_only",
                    "vision_value": vision_value,
                    "text_value": text_value
                }
                logger.info(f"👁️ Solo vision para {field_name}: {vision_value}")
                
            elif text_value is not None:
                # Solo texto tiene valor
                consensus_result[field_name] = {
                    "value": text_value,
                    "confidence": "medium",
                    "source": "text_only",
                    "vision_value": vision_value,
                    "text_value": text_value
                }
                logger.info(f"📄 Solo texto para {field_name}: {text_value}")
                
            else:
                # Ninguno tiene valor
                consensus_result[field_name] = {
                    "value": None,
                    "confidence": "low",
                    "source": "none",
                    "vision_value": vision_value,
                    "text_value": text_value
                }
                logger.info(f"❌ Sin valor para {field_name}")
        
        logger.info("✅ Consenso generado exitosamente")
        return consensus_result
    
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
    
    async def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """
        Extraer texto de un PDF usando Azure Document Intelligence
        
        Args:
            pdf_bytes: Contenido del PDF en bytes
            
        Returns:
            Texto extraído del PDF
        """
        logger.info("📄 Extrayendo texto del PDF con Document Intelligence")
        
        try:
            # URL para el análisis de documentos
            endpoint = self.endpoint.rstrip('/')  # Remover trailing slash si existe
            url = f"{endpoint}/formrecognizer/documentModels/prebuilt-document:analyze"
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
                    content=pdf_bytes,
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
                
                # Extraer texto del resultado
                extracted_text = self._extract_text_from_result(result)
                
                logger.info(f"✅ Texto extraído exitosamente: {len(extracted_text)} caracteres")
                return extracted_text
                
        except Exception as e:
            logger.error(f"❌ Error extrayendo texto del PDF: {str(e)}")
            raise
    
    def _extract_text_from_result(self, result: Dict[str, Any]) -> str:
        """Extraer texto del resultado de Document Intelligence"""
        logger.info("🔍 Extrayendo texto del resultado de Document Intelligence")
        
        try:
            # Obtener contenido del documento
            content = result.get("analyzeResult", {}).get("content", "")
            
            if not content:
                logger.warning("⚠️ No se encontró contenido en el resultado")
                return ""
            
            # Extraer texto de todos los elementos
            text_parts = []
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    text_parts.append(item["text"])
            
            # Unir todo el texto
            full_text = " ".join(text_parts)
            
            logger.info(f"📝 Texto extraído: {len(full_text)} caracteres")
            return full_text
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo texto del resultado: {str(e)}")
            return ""

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
            endpoint = self.endpoint.rstrip('/')  # Remover trailing slash si existe
            url = f"{endpoint}/formrecognizer/documentModels/prebuilt-document:analyze"
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
