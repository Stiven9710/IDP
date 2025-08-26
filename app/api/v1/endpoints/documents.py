"""
Endpoints para el procesamiento de documentos IDP
"""

import json
import logging
from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.models.request import DocumentProcessingRequest, DocumentStatusRequest, DocumentSearchRequest
from app.models.response import (
    DocumentProcessingResponse, 
    DocumentStatusResponse, 
    DocumentSearchResponse,
    ErrorResponse
)
from app.services.document_service import DocumentService
from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter()

# Instanciar servicios
document_service = DocumentService()


@router.post("/process", response_model=DocumentProcessingResponse)
async def process_document(
    request: DocumentProcessingRequest,
    background_tasks: BackgroundTasks
) -> DocumentProcessingResponse:
    """
    Procesar un documento de forma síncrona o asíncrona según su tamaño
    
    Args:
        request: Request con la información del documento a procesar
        background_tasks: Tareas en segundo plano de FastAPI
        
    Returns:
        Response con el resultado del procesamiento o ID del job
    """
    logger.info("🚀 Endpoint /process llamado")
    logger.info(f"📄 Documento: {request.document_path}")
    logger.info(f"🎯 Modo: {request.processing_mode}")
    logger.info(f"📝 Campos: {len(request.fields)}")
    
    try:
        # Validar configuración
        if not _validate_azure_config():
            raise HTTPException(
                status_code=500,
                detail="Servicios de Azure no configurados correctamente"
            )
        
        # Procesar documento
        result = await document_service.process_document(request)
        
        logger.info(f"✅ Documento procesado exitosamente: {result.job_id}")
        return result
        
    except ValueError as e:
        logger.error(f"❌ Error de validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Error interno: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/process-upload", response_model=DocumentProcessingResponse)
async def process_document_upload(
    file: UploadFile = File(...),
    fields_config: str = Form(None),
    prompt_general: str = Form("Extrae información de este documento"),
    processing_mode: str = Form("gpt_vision_only"),
    background_tasks: BackgroundTasks = None
) -> DocumentProcessingResponse:
    """
    Procesar un documento subido directamente (archivo local)
    
    Args:
        file: Archivo subido por el usuario
        fields_config: JSON string con la configuración de campos (opcional)
        prompt_general: Prompt general para la extracción
        processing_mode: Modo de procesamiento
        background_tasks: Tareas en segundo plano de FastAPI
        
    Returns:
        Response con el resultado del procesamiento
    """
    logger.info("🚀 Endpoint /process-upload llamado")
    logger.info(f"📄 Archivo: {file.filename}")
    logger.info(f"📏 Tamaño: {file.size} bytes")
    logger.info(f"🎯 Modo: {processing_mode}")
    
    try:
        # Validar configuración
        if not _validate_azure_config():
            raise HTTPException(
                status_code=500,
                detail="Servicios de Azure no configurados correctamente"
            )
        
        # Leer contenido del archivo
        file_content = await file.read()
        logger.info(f"📥 Archivo leído: {len(file_content)} bytes")
        
        # Convertir a base64 para Azure OpenAI
        import base64
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        logger.info(f"🔄 Archivo convertido a base64: {len(file_base64)} caracteres")
        
        # Procesar configuración de campos
        fields = []
        if fields_config:
            logger.info(f"🔍 Tipo de fields_config: {type(fields_config)}")
            logger.info(f"🔍 Contenido de fields_config: {str(fields_config)[:200]}...")
            
            try:
                # Si ya es un diccionario, usarlo directamente
                if isinstance(fields_config, dict):
                    fields_raw = fields_config
                    logger.info("📋 fields_config ya es un diccionario")
                else:
                    # Si es un string, parsearlo
                    fields_raw = json.loads(str(fields_config))
                    logger.info("📋 fields_config parseado desde string JSON")
                
                # Convertir diccionarios a objetos FieldDefinition
                from app.models.request import FieldDefinition
                fields = [
                    FieldDefinition(
                        name=field.get('name', ''),
                        type=field.get('type', 'string'),
                        description=field.get('description', '')
                    )
                    for field in fields_raw
                ]
                logger.info(f"📋 Configuración personalizada cargada: {len(fields)} campos")
            except Exception as e:
                logger.error(f"❌ Error procesando configuración de campos: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Error procesando configuración de campos: {str(e)}")
        else:
            # Campos por defecto si no se proporciona configuración
            from app.models.request import FieldDefinition
            fields = [
                FieldDefinition(name="contenido", type="string", description="Contenido principal del documento"),
                FieldDefinition(name="tipo_documento", type="string", description="Tipo de documento identificado"),
                FieldDefinition(name="fecha", type="date", description="Fecha encontrada en el documento si existe"),
                FieldDefinition(name="emisor", type="string", description="Persona o entidad que emite el documento"),
                FieldDefinition(name="destinatario", type="string", description="Persona o entidad a quien va dirigido"),
                FieldDefinition(name="referencias", type="array", description="Referencias o números de identificación")
            ]
            logger.info(f"📋 Usando configuración por defecto: {len(fields)} campos")
        
        # Verificar si el documento es muy grande para procesamiento síncrono
        file_size_mb = len(file_content) / (1024 * 1024)
        logger.info(f"📏 Tamaño del archivo: {file_size_mb:.2f} MB")
        
        # Si el documento es muy grande (>10MB), usar DocumentService para procesamiento asíncrono
        if file_size_mb > 10.0:
            logger.info("🔄 DOCUMENTO GRANDE DETECTADO - ACTIVANDO PROCESAMIENTO ASÍNCRONO")
            logger.info(f"   📏 Tamaño: {file_size_mb:.2f} MB (> 10 MB)")
            logger.info(f"   📄 Filename: {file.filename}")
            logger.info(f"   🎯 Processing Mode: {processing_mode}")
            logger.info(f"   🔍 Fields Count: {len(fields) if isinstance(fields, list) else len(fields_config) if isinstance(fields_config, dict) else 'N/A'}")
            logger.info(f"   📝 Prompt Length: {len(prompt_general) if prompt_general else 0} chars")
            logger.info(f"   " + "="*80)
            
            # Crear request para DocumentService
            from app.models.request import DocumentProcessingRequest
            from app.services.document_service import DocumentService
            
            # Crear campos FieldDefinition
            from app.models.request import FieldDefinition
            field_definitions = []
            
            if isinstance(fields_config, dict):
                # Si fields_config es un diccionario, usarlo directamente
                field_definitions = [
                    FieldDefinition(
                        name=field.get('name', ''),
                        type=field.get('type', 'string'),
                        description=field.get('description', '')
                    )
                    for field in fields_config
                ]
            else:
                # Si no, usar los campos ya procesados
                field_definitions = fields
            
            # Guardar archivo temporalmente para DocumentService
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name
                logger.info(f"📁 Archivo temporal creado: {temp_path}")
            
            # Crear request para DocumentService con la ruta temporal real
            doc_request = DocumentProcessingRequest(
                document_path=temp_path,  # Ruta temporal real
                processing_mode=processing_mode,
                prompt_general=prompt_general,
                fields=field_definitions,
                metadata={
                    "source": "file_upload",
                    "filename": file.filename,
                    "file_size_mb": file_size_mb,
                    "upload_timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Usar DocumentService para procesamiento asíncrono
            logger.info(f"🚀 INICIANDO DOCUMENTSERVICE.PROCESS_DOCUMENT")
            logger.info(f"   📁 Temp Path: {temp_path}")
            logger.info(f"   📄 Filename: {file.filename}")
            logger.info(f"   🎯 Processing Mode: {processing_mode}")
            logger.info(f"   🔍 Fields: {len(field_definitions)}")
            logger.info(f"   📝 Prompt: {len(prompt_general) if prompt_general else 0} chars")
            
            doc_service = DocumentService()
            
            try:
                logger.info(f"   🔄 Llamando a doc_service.process_document...")
                response = await doc_service.process_document(doc_request)
                logger.info(f"   ✅ DocumentService.process_document completado exitosamente")
                logger.info(f"   🆔 Job ID: {response.job_id}")
                logger.info(f"   📊 Response Status: {response.processing_summary.processing_status}")
                logger.info(f"   📝 Message: {response.message}")
                
                # Limpiar archivo temporal
                os.unlink(temp_path)
                logger.info(f"   🗑️ Archivo temporal eliminado: {temp_path}")
                
                logger.info(f"   " + "="*80)
                logger.info(f"🎉 PROCESAMIENTO ASÍNCRONO INICIADO EXITOSAMENTE")
                logger.info(f"   🆔 Job ID: {response.job_id}")
                logger.info(f"   📄 Documento: {file.filename}")
                logger.info(f"   📏 Tamaño: {file_size_mb:.2f} MB")
                logger.info(f"   🎯 Modo: {processing_mode}")
                logger.info(f"   " + "="*80)
                
                return response
                
            except Exception as e:
                logger.error(f"❌ Error en DocumentService: {str(e)}")
                # Limpiar archivo temporal en caso de error
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise HTTPException(status_code=500, detail=f"Error en procesamiento asíncrono: {str(e)}")
        
        # Si el documento es pequeño, continuar con procesamiento síncrono original
        logger.info("⚡ Documento pequeño, usando procesamiento síncrono directo")
        
        # Generar descripción de campos dinámicamente
        fields_description = "Extrae los siguientes campos del documento:\n\n"
        for i, field in enumerate(fields, 1):
            field_name = field.name
            field_type = field.type
            field_desc = field.description
            fields_description += f"{i}. {field_name} ({field_type}): {field_desc}\n"
        
        # Agregar reglas del sistema basadas en el código de referencia
        system_rules = f"""
        
        REGLAS DEL SISTEMA:
        1. Respuesta DEBE SER EXCLUSIVAMENTE JSON válido. Sin texto ANTES/DESPUÉS.
        2. NO uses formato markdown (```json o ```). Devuelve SOLO el JSON puro.
        3. JSON debe contener campos: {[field.name for field in fields]}.
        4. {prompt_general} No uses conocimiento externo.
        5. Si campo no está en el documento, valor DEBE ser "N/A" o null. No inventes.
        6. Analiza el documento y PREGUNTA para valores.
        7. Para fechas, usa formato YYYY-MM-DD.
        8. Para montos, extrae solo el valor numérico sin símbolos de moneda.
        9. Para arrays, estructura correctamente con objetos JSON.
        
        CRÍTICO: Responde ÚNICAMENTE con el JSON puro, sin ```json, sin ```, sin texto adicional.
        Ejemplo de respuesta correcta:
        {{"campo1": "valor1", "campo2": "valor2"}}
        """
        
        # Prompt completo para Azure OpenAI
        full_prompt = f"""
        {prompt_general}
        
        {fields_description}
        
        {system_rules}
        
        Analiza el documento y extrae la información solicitada siguiendo estrictamente las reglas del sistema.
        """
        
        logger.info("🤖 Enviando documento a Azure OpenAI...")
        logger.info(f"📝 Prompt: {full_prompt[:300]}...")
        logger.info(f"🎯 Campos a extraer: {[field.name for field in fields]}")
        
        # Llamar a Azure OpenAI
        from app.utils.azure_clients import AzureOpenAIClient
        openai_client = AzureOpenAIClient()
        
        # Procesar con Azure OpenAI
        openai_response = await openai_client.process_document_vision(
            document_b64=file_base64,
            prompt=full_prompt,
            fields=fields,
            processing_mode=processing_mode
        )
        
        logger.info(f"✅ Respuesta de Azure OpenAI recibida: {len(str(openai_response))} caracteres")
        logger.info(f"🤖 Contenido de la respuesta: {openai_response}")
        
        # Generar job_id
        import uuid
        job_id = str(uuid.uuid4())
        
        # ===== NUEVA INTEGRACIÓN: Guardar en Cosmos DB =====
        logger.info("🗄️ Iniciando guardado en Azure Cosmos DB...")
        
        try:
            # Crear información del documento para Cosmos DB
            document_info = {
                "filename": file.filename,
                "file_size_mb": len(file_content) / (1024 * 1024),
                "file_type": file.filename.split(".")[-1] if "." in file.filename else "unknown",
                "status": "processed",
                "processing_mode": processing_mode,
                "correlation_id": f"upload-{job_id}",
                "job_id": job_id,
                "created_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"📄 Guardando información del documento en Cosmos DB...")
            logger.info(f"   📁 Nombre: {document_info['filename']}")
            logger.info(f"   📏 Tamaño: {document_info['file_size_mb']:.2f} MB")
            logger.info(f"   🎯 Modo: {document_info['processing_mode']}")
            
            # Guardar documento en Cosmos DB
            doc_id = await document_service.cosmos_service.save_document(document_info)
            if doc_id:
                logger.info(f"✅ Documento guardado exitosamente en Cosmos DB")
                logger.info(f"   🆔 Document ID: {doc_id}")
                logger.info(f"   📍 Container: documents")
                
                # Crear resultado de extracción para Cosmos DB
                extraction_data = {
                    "document_id": doc_id,
                    "extraction_date": datetime.utcnow().isoformat(),
                    "processing_time_ms": 2000,  # Estimado
                    "strategy_used": processing_mode,
                    "job_id": job_id,
                    "filename": file.filename,
                    "fields_extracted": len(fields)
                }
                
                # Intentar parsear la respuesta de OpenAI para extraer campos
                try:
                    if isinstance(openai_response, dict):
                        parsed_response = openai_response
                    else:
                        # Limpiar formato markdown si existe
                        response_text = str(openai_response).strip()
                        if response_text.startswith('```json'):
                            response_text = response_text[7:]
                        if response_text.endswith('```'):
                            response_text = response_text[:-3]
                        response_text = response_text.strip()
                        parsed_response = json.loads(response_text)
                    
                    # Agregar campos extraídos
                    extraction_data["extraction_data"] = [
                        {
                            "name": field_name,
                            "value": str(field_value),
                            "confidence": 0.9,
                            "source_strategy": processing_mode
                        }
                        for field_name, field_value in parsed_response.items()
                        if field_value is not None
                    ]
                    
                    logger.info(f"🔍 Guardando resultado de extracción en Cosmos DB...")
                    logger.info(f"   📊 Campos extraídos: {len(extraction_data['extraction_data'])}")
                    
                    ext_id = await document_service.cosmos_service.save_extraction_result(extraction_data)
                    if ext_id:
                        logger.info(f"✅ Extracción guardada exitosamente en Cosmos DB")
                        logger.info(f"   🆔 Extraction ID: {ext_id}")
                        logger.info(f"   📍 Container: extractions")
                        logger.info(f"   🔗 Vinculada al documento: {doc_id}")
                    else:
                        logger.error(f"❌ ERROR: No se pudo guardar la extracción en Cosmos DB")
                        
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo procesar respuesta de OpenAI para Cosmos DB: {e}")
                    # Guardar extracción básica
                    extraction_data["extraction_data"] = []
                    ext_id = await document_service.cosmos_service.save_extraction_result(extraction_data)
                    
            else:
                logger.error(f"❌ ERROR: No se pudo guardar el documento en Cosmos DB")
                
        except Exception as e:
            logger.warning(f"⚠️ Error guardando en Cosmos DB: {e}")
            logger.warning(f"⚠️ Continuando con el procesamiento normal...")
        
        # ===== FIN DE INTEGRACIÓN COSMOS DB =====
        
        # Crear response con los datos reales extraídos
        from app.models.response import (
            DocumentProcessingResponse, 
            ProcessingSummary, 
            ProcessingStatus,
            ProcessingMode,
            ExtractionField
        )
        
        # Crear campos de extracción basados en la respuesta de OpenAI
        extraction_fields = []
        
        # Intentar parsear la respuesta JSON de OpenAI
        try:
            # Manejo robusto: verificar si la respuesta ya es un dict
            if isinstance(openai_response, dict):
                parsed_response = openai_response
                logger.info("📋 Respuesta de OpenAI ya es un diccionario")
            else:
                # Limpiar formato markdown si existe
                response_text = str(openai_response).strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]  # Remover ```json
                if response_text.endswith('```'):
                    response_text = response_text[:-3]  # Remover ```
                response_text = response_text.strip()
                
                logger.info(f"🧹 Respuesta limpiada: {response_text[:100]}...")
                parsed_response = json.loads(response_text)
                logger.info("📋 Respuesta de OpenAI parseada desde string JSON")
            
            # Crear campos de extracción para cada campo encontrado
            for field_name, field_value in parsed_response.items():
                if field_value is not None:
                    extraction_fields.append(
                        ExtractionField(
                            name=field_name,
                            value=str(field_value),
                            confidence=0.9,  # Alta confianza para OpenAI
                            review_required=False,
                            source_strategy=processing_mode,
                            extraction_time_ms=1000
                        )
                    )
            
            logger.info(f"📊 Campos extraídos exitosamente: {len(extraction_fields)}")
            
            # Verificar campos faltantes según la configuración
            extracted_field_names = [field.name for field in extraction_fields]
            missing_fields = [field.name for field in fields if field.name not in extracted_field_names]
            
            if missing_fields:
                logger.info(f"⚠️ Campos no encontrados en la respuesta: {missing_fields}")
                
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ No se pudo parsear JSON de OpenAI: {e}")
            logger.info(f"📝 Respuesta cruda de OpenAI: {openai_response}")
            
            # Si no se puede parsear, crear un campo con la respuesta completa
            extraction_fields.append(
                ExtractionField(
                    name="respuesta_completa",
                    value=str(openai_response),
                    confidence=0.7,
                    review_required=True,  # Requiere revisión manual
                    source_strategy=processing_mode,
                    extraction_time_ms=1000
                )
            )
        
        response = DocumentProcessingResponse(
            job_id=job_id,
            extraction_data=extraction_fields,
            processing_summary=ProcessingSummary(
                processing_status=ProcessingStatus.COMPLETED,
                processing_time_ms=2000,
                file_size_mb=len(file_content) / (1024 * 1024),
                strategy_used=ProcessingMode(processing_mode),
                timestamp=datetime.utcnow(),
                pages_processed=1,
                review_flags=[]
            ),
            message=f"Documento {file.filename} procesado exitosamente con Azure OpenAI",
            correlation_id=f"upload-{job_id}"
        )
        
        logger.info(f"✅ Documento procesado exitosamente: {job_id}")
        logger.info(f"🗄️ Datos guardados en Cosmos DB: Document={doc_id if 'doc_id' in locals() else 'N/A'}, Extraction={ext_id if 'ext_id' in locals() else 'N/A'}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error procesando archivo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")


@router.post("/process-upload-custom", response_model=DocumentProcessingResponse)
async def process_document_upload_custom(
    file: UploadFile = File(...),
    fields_config: str = None,
    prompt_general: str = "Extrae información de este documento",
    processing_mode: str = "gpt_vision_only",
    background_tasks: BackgroundTasks = None
) -> DocumentProcessingResponse:
    """
    Procesar un documento con configuración personalizada de campos
    
    Args:
        file: Archivo subido por el usuario
        fields_config: JSON string con la configuración de campos
        prompt_general: Prompt general para la extracción
        processing_mode: Modo de procesamiento
        background_tasks: Tareas en segundo plano de FastAPI
        
    Returns:
        Response con el resultado del procesamiento
    """
    logger.info("🚀 Endpoint /process-upload-custom llamado")
    logger.info(f"📄 Archivo: {file.filename}")
    logger.info(f"📏 Tamaño: {file.size} bytes")
    logger.info(f"🎯 Modo: {processing_mode}")
    
    try:
        # Validar configuración
        if not _validate_azure_config():
            raise HTTPException(
                status_code=500,
                detail="Servicios de Azure no configurados correctamente"
            )
        
        # Leer contenido del archivo
        file_content = await file.read()
        logger.info(f"📥 Archivo leído: {len(file_content)} bytes")
        
        # Convertir a base64 para Azure OpenAI
        import base64
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        logger.info(f"🔄 Archivo convertido a base64: {len(file_base64)} caracteres")
        
        # --- SECCIÓN CORREGIDA ---
        fields = []
        from app.models.request import FieldDefinition

        if fields_config:
            try:
                fields_raw = None
                # 1. CORRECCIÓN: Verificar si fields_config ya es un diccionario
                if isinstance(fields_config, dict):
                    fields_raw = fields_config
                    logger.info("📋 fields_config ya es un diccionario")
                else:
                    # Si es un string, parsearlo
                    fields_raw = json.loads(fields_config)
                    logger.info("📋 fields_config parseado desde string JSON")
                
                # 2. CORRECCIÓN: Convertir los diccionarios a objetos FieldDefinition
                # Esto soluciona el error latente de `AttributeError: 'dict' object has no attribute 'name'`
                if isinstance(fields_raw, list):
                    fields = [
                        FieldDefinition(
                            name=field.get('name', ''),
                            type=field.get('type', 'string'),
                            description=field.get('description', '')
                        )
                        for field in fields_raw
                    ]
                    logger.info(f"📋 Configuración personalizada cargada: {len(fields)} campos")
                else:
                    raise ValueError("La configuración de campos debe ser una lista de objetos.")

            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"⚠️ Error procesando configuración personalizada: {e}")
                raise HTTPException(status_code=400, detail=f"Configuración de campos inválida: {e}")
        else:
            # Lógica para cargar configuración por defecto si no se proporciona
            # (Se mantiene igual que tu código original)
            try:
                with open('test_request_example.json', 'r', encoding='utf-8') as config_file:
                    config_data = json.load(config_file)
                    fields_raw = config_data.get('fields', [])
                    prompt_general = config_data.get('prompt_general', prompt_general)
                    processing_mode = config_data.get('processing_mode', processing_mode)
                    
                    fields = [
                        FieldDefinition(**field) for field in fields_raw
                    ]
                logger.info(f"📋 Configuración por defecto cargada: {len(fields)} campos")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo cargar configuración por defecto: {e}")
                fields = [
                    FieldDefinition(name="contenido", type="string", description="Contenido principal del documento"),
                    FieldDefinition(name="tipo_documento", type="string", description="Tipo de documento identificado")
                ]
        # --- FIN DE LA SECCIÓN CORREGIDA ---
        
        # Generar descripción de campos dinámicamente
        fields_description = "Extrae los siguientes campos del documento:\n\n"
        for i, field in enumerate(fields, 1):
            field_name = field.name
            field_type = field.type
            field_desc = field.description
            fields_description += f"{i}. {field_name} ({field_type}): {field_desc}\n"
        
        # Agregar reglas del sistema
        system_rules = f"""
        
        REGLAS DEL SISTEMA:
        1. Respuesta DEBE SER EXCLUSIVAMENTE JSON válido. Sin texto ANTES/DESPUÉS.
        2. NO uses formato markdown (```json o ```). Devuelve SOLO el JSON puro.
        3. JSON debe contener campos: {[field.name for field in fields]}.
        4. {prompt_general} No uses conocimiento externo.
        5. Si campo no está en el documento, valor DEBE ser "N/A" o null. No inventes.
        6. Analiza el documento y PREGUNTA para valores.
        7. Para fechas, usa formato YYYY-MM-DD.
        8. Para montos, extrae solo el valor numérico sin símbolos de moneda.
        9. Para arrays, estructura correctamente con objetos JSON.
        
        CRÍTICO: Responde ÚNICAMENTE con el JSON puro, sin ```json, sin ```, sin texto adicional.
        Ejemplo de respuesta correcta:
        {{"campo1": "valor1", "campo2": "valor2"}}
        """
        
        # Prompt completo para Azure OpenAI
        full_prompt = f"""
        {prompt_general}
        
        {fields_description}
        
        {system_rules}
        
        Analiza el documento y extrae la información solicitada siguiendo estrictamente las reglas del sistema.
        """
        
        logger.info("🤖 Enviando documento a Azure OpenAI...")
        logger.info(f"📝 Prompt: {full_prompt[:300]}...")
        logger.info(f"🎯 Campos a extraer: {[field.name for field in fields]}")
        
        # Llamar a Azure OpenAI
        from app.utils.azure_clients import AzureOpenAIClient
        openai_client = AzureOpenAIClient()
        
        # Procesar con Azure OpenAI
        openai_response = await openai_client.process_document_vision(
            document_b64=file_base64,
            prompt=full_prompt,
            fields=fields,
            processing_mode=processing_mode
        )
        
        logger.info(f"✅ Respuesta de Azure OpenAI recibida: {len(str(openai_response))} caracteres")
        logger.info(f"🤖 Contenido de la respuesta: {openai_response}")
        
        # Generar job_id
        import uuid
        job_id = str(uuid.uuid4())
        
        # Crear response con los datos reales extraídos
        from app.models.response import (
            DocumentProcessingResponse, 
            ProcessingSummary, 
            ProcessingStatus,
            ProcessingMode,
            ExtractionField
        )
        
        # Crear campos de extracción basados en la respuesta de OpenAI
        extraction_fields = []
        
        # Intentar parsear la respuesta JSON de OpenAI
        try:
            # Manejo robusto: verificar si la respuesta ya es un dict
            if isinstance(openai_response, dict):
                parsed_response = openai_response
            else:
                # Limpiar formato markdown si existe
                response_text = str(openai_response).strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]  # Remover ```json
                if response_text.endswith('```'):
                    response_text = response_text[:-3]  # Remover ```
                response_text = response_text.strip()
                
                logger.info(f"🧹 Respuesta limpiada: {response_text[:100]}...")
                parsed_response = json.loads(response_text)
            
            # Crear campos de extracción para cada campo encontrado
            for field_name, field_value in parsed_response.items():
                if field_value is not None:
                    extraction_fields.append(
                        ExtractionField(
                            name=field_name,
                            value=str(field_value),
                            confidence=0.9,  # Alta confianza para OpenAI
                            review_required=False,
                            source_strategy=processing_mode,
                            extraction_time_ms=1000
                        )
                    )
            
            logger.info(f"📊 Campos extraídos exitosamente: {len(extraction_fields)}")
            
            # Verificar campos faltantes según la configuración
            extracted_field_names = [field.name for field in extraction_fields]
            missing_fields = [field.name for field in fields if field.name not in extracted_field_names]
            
            if missing_fields:
                logger.info(f"⚠️ Campos no encontrados en la respuesta: {missing_fields}")
                
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ No se pudo parsear JSON de OpenAI: {e}")
            logger.info(f"📝 Respuesta cruda de OpenAI: {openai_response}")
            
            # Si no se puede parsear, crear un campo con la respuesta completa
            extraction_fields.append(
                ExtractionField(
                    name="respuesta_completa",
                    value=str(openai_response),
                    confidence=0.7,
                    review_required=True,  # Requiere revisión manual
                    source_strategy=processing_mode,
                    extraction_time_ms=1000
                )
            )
        
        response = DocumentProcessingResponse(
            job_id=job_id,
            extraction_data=extraction_fields,
            processing_summary=ProcessingSummary(
                processing_status=ProcessingStatus.COMPLETED,
                processing_time_ms=2000,
                file_size_mb=len(file_content) / (1024 * 1024),
                strategy_used=ProcessingMode(processing_mode),
                timestamp=datetime.utcnow(),
                pages_processed=1,
                review_flags=[]
            ),
            message=f"Documento {file.filename} procesado exitosamente con Azure OpenAI",
            correlation_id=f"upload-custom-{job_id}"
        )
        
        logger.info(f"✅ Documento procesado exitosamente: {job_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error procesando archivo: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")


@router.get("/{job_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(job_id: str) -> DocumentStatusResponse:
    """
    Obtener el estado de un documento en procesamiento
    
    Args:
        job_id: ID del trabajo de procesamiento
        
    Returns:
        Estado actual del documento
    """
    logger.info(f"🔍 Consultando estado del job: {job_id}")
    
    try:
        status_data = await document_service.get_document_status(job_id)
        
        # Convertir a response model
        response = DocumentStatusResponse(
            job_id=job_id,
            status=status_data.get("status", "unknown"),
            progress_percentage=status_data.get("progress_percentage", 0.0),
            estimated_completion=status_data.get("estimated_completion"),
            current_step=status_data.get("current_step", "Desconocido"),
            message=status_data.get("message", "Estado consultado exitosamente")
        )
        
        logger.info(f"📊 Estado del job {job_id}: {response.status}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error consultando estado del job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error consultando estado del documento")


@router.get("/{job_id}/result", response_model=DocumentProcessingResponse)
async def get_document_result(job_id: str) -> DocumentProcessingResponse:
    """
    Obtener el resultado de un documento procesado
    
    Args:
        job_id: ID del trabajo de procesamiento
        
    Returns:
        Resultado completo del procesamiento
    """
    logger.info(f"🔍 Consultando resultado del job: {job_id}")
    
    try:
        result_data = await document_service.get_document_result(job_id)
        
        # Verificar si el documento está procesado
        if not result_data or result_data.get("status") != "completed":
            raise HTTPException(
                status_code=404, 
                detail="Documento no encontrado o aún en procesamiento"
            )
        
        # Convertir a response model
        response = DocumentProcessingResponse(
            job_id=job_id,
            extraction_data=result_data.get("extraction_data", []),
            processing_summary=result_data.get("processing_summary", {}),
            message=result_data.get("message", "Resultado obtenido exitosamente"),
            correlation_id=result_data.get("correlation_id")
        )
        
        logger.info(f"📊 Resultado del job {job_id} obtenido exitosamente")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error consultando resultado del job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error consultando resultado del documento")


@router.get("/search", response_model=DocumentSearchResponse)
async def search_documents(
    correlation_id: str = None,
    processing_mode: str = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 100
) -> DocumentSearchResponse:
    """
    Buscar documentos procesados con filtros opcionales
    
    Args:
        correlation_id: ID de correlación para buscar documentos específicos
        processing_mode: Filtrar por modo de procesamiento
        start_date: Fecha de inicio para la búsqueda (YYYY-MM-DD)
        end_date: Fecha de fin para la búsqueda (YYYY-MM-DD)
        limit: Número máximo de resultados
        
    Returns:
        Lista de documentos encontrados
    """
    logger.info("🔍 Endpoint de búsqueda de documentos llamado")
    logger.info(f"🔍 Filtros: correlation_id={correlation_id}, mode={processing_mode}")
    
    try:
        # Construir filtros de búsqueda
        search_filters = {}
        if correlation_id:
            search_filters["correlation_id"] = correlation_id
        if processing_mode:
            search_filters["processing_mode"] = processing_mode
        if start_date:
            search_filters["start_date"] = start_date
        if end_date:
            search_filters["end_date"] = end_date
        
        # Realizar búsqueda (implementar en storage service)
        # Por ahora, devolver respuesta de ejemplo
        documents = [
            {
                "job_id": "example-job-123",
                "document_path": "https://example.com/document.pdf",
                "processing_mode": "hybrid_consensus",
                "status": "completed",
                "created_at": "2025-01-12T10:00:00Z"
            }
        ]
        
        response = DocumentSearchResponse(
            documents=documents,
            total_count=len(documents),
            page=1,
            page_size=limit,
            has_more=False
        )
        
        logger.info(f"📊 Búsqueda completada: {len(documents)} documentos encontrados")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error en búsqueda de documentos: {str(e)}")
        raise HTTPException(status_code=500, detail="Error en la búsqueda de documentos")


@router.delete("/{job_id}")
async def cancel_document_processing(job_id: str) -> Dict[str, str]:
    """
    Cancelar el procesamiento de un documento
    
    Args:
        job_id: ID del trabajo de procesamiento
        
    Returns:
        Confirmación de la cancelación
    """
    logger.info(f"❌ Cancelando procesamiento del job: {job_id}")
    
    try:
        # Implementar lógica de cancelación
        # Por ahora, devolver confirmación
        logger.info(f"✅ Procesamiento del job {job_id} cancelado")
        return {"message": f"Procesamiento del job {job_id} cancelado exitosamente"}
        
    except Exception as e:
        logger.error(f"❌ Error cancelando job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error cancelando el procesamiento")


@router.get("/extractions/history/{document_id}")
async def get_extraction_history(document_id: str):
    """
    Obtener historial de extracciones de un documento
    
    Args:
        document_id: ID del documento
        
    Returns:
        Lista de extracciones del documento
    """
    logger.info(f"📚 Consultando historial de extracciones para documento: {document_id}")
    
    try:
        from app.services.cosmos_service import CosmosService
        
        cosmos_service = CosmosService()
        extractions = await cosmos_service.get_extraction_history(document_id)
        
        return {
            "document_id": document_id,
            "extractions_count": len(extractions),
            "extractions": extractions,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error consultando historial: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error consultando historial: {str(e)}"
        )

@router.get("/extractions/search")
async def search_extractions(query: str, field_name: str = None):
    """
    Buscar extracciones por texto
    
    Args:
        query: Texto a buscar
        field_name: Campo específico donde buscar (opcional)
        
    Returns:
        Lista de extracciones que coinciden
    """
    logger.info(f"🔍 Buscando extracciones con query: '{query}'")
    
    try:
        from app.services.cosmos_service import CosmosService
        
        cosmos_service = CosmosService()
        results = await cosmos_service.search_extractions(query, field_name)
        
        return {
            "query": query,
            "field_name": field_name,
            "results_count": len(results),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error en búsqueda: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error en búsqueda: {str(e)}"
        )


def _validate_azure_config() -> bool:
    """Validar que la configuración de Azure esté completa"""
    required_configs = [
        settings.azure_openai_endpoint,
        settings.azure_openai_api_key,
        settings.azure_document_intelligence_endpoint,
        settings.azure_document_intelligence_api_key
    ]
    
    return all(config for config in required_configs)
