#!/bin/bash
# Script para probar la API IDP con el documento de Banco Caribe
# Usa la configuración de test_banco_caribe_config.json

echo "🚀 PROBANDO API IDP - DOCUMENTO BANCO CARIBE"
echo "=============================================="

# Configuración del documento
DOCUMENT_PATH="tests/Documentos/Banco Caribe - Propuesta Perfil Transaccional IB Final.pptx"
API_URL="http://159.203.149.247:8000/api/v1/documents/process-upload"

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
    "description": "Un resumen ejecutivo de la propuesta en máximo 30 palabras. Busca en: resúmenes ejecutivos, introducciones, objetivos del proyecto, descripción general. Si no hay un resumen explícito, crea uno basado en el contenido del documento."
  },
  {
    "name": "tecnologia_implementar",
    "type": "string",
    "description": "Las tecnologías principales que se van a implementar. Busca en: secciones técnicas, arquitectura, especificaciones del proyecto, stack tecnológico, herramientas, plataformas, frameworks, bases de datos, APIs, servicios en la nube. Lista todas las tecnologías mencionadas separadas por comas."
  },
  {
    "name": "requisitos_infraestructura_software",
    "type": "array",
    "description": "Lista de requisitos de infraestructura de software. Busca en: secciones de infraestructura, requisitos técnicos, especificaciones del sistema, hardware, software, servidores, bases de datos, redes, seguridad. Cada elemento debe tener 'descripcion' y 'cantidad'. Si no hay cantidades específicas, estima basándote en el contexto del proyecto."
  },
  {
    "name": "total_horas",
    "type": "number",
    "description": "El total de horas estimadas para el proyecto. Busca en: cronogramas, estimaciones de tiempo, resúmenes ejecutivos, planificación del proyecto, recursos humanos, esfuerzo estimado, duración del proyecto. Si no hay un total explícito, suma todas las horas mencionadas en el documento o estima basándote en la complejidad descrita."
  }
]'

# Prompt general
PROMPT_GENERAL="Actúa como un analista de propuestas técnicas experto en banca. Tu tarea es extraer información específica de esta propuesta de Banco Caribe. IMPORTANTE: Debes analizar TODO el documento página por página para encontrar la información solicitada. NO devuelvas null a menos que estés 100% seguro de que el campo no existe en ninguna parte del documento. Para cada campo: 1) Busca en TODAS las páginas, 2) Si encuentras información parcial, extrae lo que puedas, 3) Si no encuentras nada después de revisar todo, entonces devuelve null. Para cantidades, extrae solo el valor numérico. Para arrays, extrae cada elemento con descripción y cantidad. REVISA CADA PÁGINA METICULOSAMENTE."

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
echo "   • Verificar estado: curl http://159.203.149.247:8000/api/v1/health/storage"
echo "   • Verificar jobs: curl http://159.203.149.247:8000/api/v1/jobs/"
