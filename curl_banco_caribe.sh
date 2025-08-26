#!/bin/bash
# Script para probar la API IDP con el documento de Banco Caribe
# Usa la configuración de test_banco_caribe_config.json

echo "🚀 PROBANDO API IDP - DOCUMENTO BANCO CARIBE"
echo "=============================================="

# Configuración del documento
DOCUMENT_PATH="tests/Documentos/Banco Caribe - Propuesta Perfil Transaccional IB Final.pptx"
API_URL="http://localhost:8000/api/v1/documents/process-upload"

# Verificar que el documento existe
if [ ! -f "$DOCUMENT_PATH" ]; then
    echo "❌ Error: Documento no encontrado en $DOCUMENT_PATH"
    exit 1
fi

echo "📄 Documento: $DOCUMENT_PATH"
echo "🌐 API URL: $API_URL"
echo ""

# Campos a extraer (convertidos a JSON string)
FIELDS_CONFIG='[
  {
    "name": "nombre_propuesta",
    "type": "string",
    "description": "El nombre completo de la propuesta o proyecto. Busca en el título principal y encabezados del documento."
  },
  {
    "name": "resumen_propuesta",
    "type": "string",
    "description": "Un resumen ejecutivo de la propuesta en máximo 30 palabras. Extrae la esencia del proyecto de manera concisa."
  },
  {
    "name": "tecnologia_implementar",
    "type": "string",
    "description": "Las tecnologías principales que se van a implementar. Busca en secciones técnicas, arquitectura o especificaciones del proyecto."
  },
  {
    "name": "requisitos_infraestructura_software",
    "type": "array",
    "description": "Lista de requisitos de infraestructura de software. Cada elemento debe tener descripcion y cantidad. Busca en secciones de infraestructura, requisitos técnicos o especificaciones del sistema."
  },
  {
    "name": "total_horas",
    "type": "number",
    "description": "El total de horas estimadas para el proyecto. Busca en cronogramas, estimaciones de tiempo o resúmenes ejecutivos."
  }
]'

# Prompt general
PROMPT_GENERAL="Actúa como un analista de propuestas técnicas experto en banca. Analiza esta propuesta de Banco Caribe y extrae información técnica específica de manera precisa. Si un campo no está presente, devuélvelo como null. Para cantidades, extrae solo el valor numérico sin texto adicional. IMPORTANTE: Este es un documento grande, enfócate en extraer la información más relevante de las primeras páginas y secciones principales."

# Modo de procesamiento
PROCESSING_MODE="gpt_vision_only"

echo "📋 Configuración:"
echo "   🎯 Modo: $PROCESSING_MODE"
echo "   📝 Prompt: ${PROMPT_GENERAL:0:100}..."
echo "   🔍 Campos: 5"
echo ""

# Ejecutar curl
echo "🌐 Ejecutando API..."
echo ""

curl -X POST "$API_URL" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$DOCUMENT_PATH" \
  -F "fields_config=$FIELDS_CONFIG" \
  -F "prompt_general=$PROMPT_GENERAL" \
  -F "processing_mode=$PROCESSING_MODE" \
  -w "\n\n📊 Resumen de la respuesta:\n   Status: %{http_code}\n   Tiempo: %{time_total}s\n   Tamaño: %{size_download} bytes\n" \
  -s

echo ""
echo "✅ Comando curl ejecutado"
echo ""
echo "💡 Para monitorear el procesamiento:"
echo "   • Ver logs del worker: tail -f worker.log"
echo "   • Ver logs de la API: tail -f api.log"
echo "   • Verificar estado: curl http://localhost:8000/api/v1/health/storage"
echo "   • Verificar jobs: curl http://localhost:8000/api/v1/jobs/"
