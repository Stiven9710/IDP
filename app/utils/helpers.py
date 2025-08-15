"""
Funciones de utilidad para el sistema IDP
"""

import asyncio
import logging
import re
from typing import Optional, List
from urllib.parse import urlparse
import httpx

# Configurar logging
logger = logging.getLogger(__name__)


async def get_file_size_from_url(url: str) -> float:
    """
    Obtener el tamaño de un archivo desde su URL
    
    Args:
        url: URL del archivo
        
    Returns:
        Tamaño del archivo en MB
    """
    try:
        logger.info(f"📏 Obteniendo tamaño del archivo: {url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.head(url, timeout=10.0)
            response.raise_for_status()
            
            # Obtener tamaño del header Content-Length
            content_length = response.headers.get("Content-Length")
            if content_length:
                size_bytes = int(content_length)
                size_mb = size_bytes / (1024 * 1024)
                logger.info(f"📏 Tamaño del archivo: {size_mb:.2f} MB")
                return size_mb
            
            # Si no hay Content-Length, intentar descargar parcialmente
            logger.warning("⚠️ No se encontró Content-Length, descargando parcialmente")
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            
            size_bytes = len(response.content)
            size_mb = size_bytes / (1024 * 1024)
            logger.info(f"📏 Tamaño del archivo (descarga parcial): {size_mb:.2f} MB")
            return size_mb
            
    except Exception as e:
        logger.warning(f"⚠️ No se pudo obtener el tamaño del archivo: {str(e)}")
        # Valor por defecto para continuar el procesamiento
        return 5.0


def is_supported_format(file_path: str) -> bool:
    """
    Verificar si el formato del archivo es soportado
    
    Args:
        file_path: Ruta o URL del archivo
        
    Returns:
        True si el formato es soportado, False en caso contrario
    """
    supported_formats = [
        # Documentos PDF
        '.pdf',
        
        # Imágenes
        '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif',
        
        # Documentos de Office
        '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt',
        
        # Texto plano
        '.txt', '.rtf', '.md',
        
        # Otros formatos
        '.html', '.htm'
    ]
    
    file_path_lower = file_path.lower()
    is_supported = any(file_path_lower.endswith(fmt) for fmt in supported_formats)
    
    logger.info(f"🔍 Validación de formato: {file_path} - {'✅ Soportado' if is_supported else '❌ No soportado'}")
    return is_supported


def extract_file_extension(file_path: str) -> str:
    """
    Extraer la extensión del archivo
    
    Args:
        file_path: Ruta o URL del archivo
        
    Returns:
        Extensión del archivo (incluyendo el punto)
    """
    parsed_url = urlparse(file_path)
    file_path = parsed_url.path
    
    # Encontrar la última extensión
    if '.' in file_path:
        return file_path.split('.')[-1].lower()
    return ""


def validate_url(url: str) -> bool:
    """
    Validar si una URL es válida
    
    Args:
        url: URL a validar
        
    Returns:
        True si la URL es válida, False en caso contrario
    """
    try:
        parsed = urlparse(url)
        is_valid = all([parsed.scheme, parsed.netloc])
        
        logger.info(f"🔗 Validación de URL: {url} - {'✅ Válida' if is_valid else '❌ Inválida'}")
        return is_valid
    except Exception as e:
        logger.warning(f"⚠️ Error validando URL {url}: {str(e)}")
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitizar un nombre de archivo para uso seguro
    
    Args:
        filename: Nombre del archivo original
        
    Returns:
        Nombre del archivo sanitizado
    """
    # Remover caracteres peligrosos
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remover espacios múltiples
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Remover espacios al inicio y final
    sanitized = sanitized.strip()
    
    # Limitar longitud
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    logger.info(f"🧹 Nombre sanitizado: '{filename}' -> '{sanitized}'")
    return sanitized


def format_file_size(size_bytes: int) -> str:
    """
    Formatear tamaño de archivo en formato legible
    
    Args:
        size_bytes: Tamaño en bytes
        
    Returns:
        Tamaño formateado (ej: "1.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def extract_metadata_from_url(url: str) -> dict:
    """
    Extraer metadatos básicos de una URL
    
    Args:
        url: URL del documento
        
    Returns:
        Diccionario con metadatos extraídos
    """
    try:
        parsed = urlparse(url)
        
        metadata = {
            "scheme": parsed.scheme,
            "domain": parsed.netloc,
            "path": parsed.path,
            "filename": parsed.path.split('/')[-1] if parsed.path else None,
            "extension": extract_file_extension(parsed.path),
            "query_params": dict(parsed.parse_qsl(parsed.query)) if parsed.query else {}
        }
        
        logger.info(f"📋 Metadatos extraídos de URL: {metadata}")
        return metadata
        
    except Exception as e:
        logger.warning(f"⚠️ Error extrayendo metadatos de URL: {str(e)}")
        return {}


def is_image_format(file_path: str) -> bool:
    """
    Verificar si el archivo es una imagen
    
    Args:
        file_path: Ruta o URL del archivo
        
    Returns:
        True si es una imagen, False en caso contrario
    """
    image_formats = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.webp']
    extension = extract_file_extension(file_path)
    
    is_image = f".{extension}" in image_formats
    logger.info(f"🖼️ Verificación de imagen: {file_path} - {'✅ Imagen' if is_image else '❌ No es imagen'}")
    
    return is_image


def is_document_format(file_path: str) -> bool:
    """
    Verificar si el archivo es un documento
    
    Args:
        file_path: Ruta o URL del archivo
        
    Returns:
        True si es un documento, False en caso contrario
    """
    document_formats = ['.pdf', '.docx', '.doc', '.txt', '.rtf', '.md']
    extension = extract_file_extension(file_path)
    
    is_document = f".{extension}" in document_formats
    logger.info(f"📄 Verificación de documento: {file_path} - {'✅ Documento' if is_document else '❌ No es documento'}")
    
    return is_document


async def retry_operation(
    operation,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0
):
    """
    Reintentar una operación con backoff exponencial
    
    Args:
        operation: Función a ejecutar
        max_retries: Número máximo de reintentos
        delay: Delay inicial en segundos
        backoff_factor: Factor de multiplicación del delay
        
    Returns:
        Resultado de la operación
        
    Raises:
        Exception: Si la operación falla después de todos los reintentos
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(operation):
                return await operation()
            else:
                return operation()
                
        except Exception as e:
            last_exception = e
            logger.warning(f"⚠️ Intento {attempt + 1} falló: {str(e)}")
            
            if attempt < max_retries:
                wait_time = delay * (backoff_factor ** attempt)
                logger.info(f"⏳ Esperando {wait_time:.1f}s antes del siguiente intento...")
                await asyncio.sleep(wait_time)
    
    logger.error(f"❌ Operación falló después de {max_retries + 1} intentos")
    raise last_exception


def generate_correlation_id() -> str:
    """
    Generar un ID de correlación único
    
    Returns:
        ID de correlación único
    """
    import uuid
    import time
    
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]
    correlation_id = f"idp-{timestamp}-{unique_id}"
    
    logger.info(f"🆔 ID de correlación generado: {correlation_id}")
    return correlation_id


def validate_processing_mode(mode: str) -> bool:
    """
    Validar si el modo de procesamiento es válido
    
    Args:
        mode: Modo de procesamiento a validar
        
    Returns:
        True si el modo es válido, False en caso contrario
    """
    valid_modes = ["dual_service", "gpt_vision_only", "hybrid_consensus"]
    is_valid = mode in valid_modes
    
    logger.info(f"🎯 Validación de modo de procesamiento: {mode} - {'✅ Válido' if is_valid else '❌ Inválido'}")
    return is_valid
