#!/bin/bash

echo "🚀 PROBANDO API IDP - FACTURA COLOMBIANA"
echo "=========================================="
echo "📄 Documento: tests/Documentos/Invoice_2082463105.pdf"
echo "🌐 API URL: http://159.203.149.247:8000/api/v1/documents/process-upload"
echo ""

echo "📋 Configuración:"
echo "   🎯 Modo: gpt_vision_only"
echo "   📝 Prompt: Analista financiero experto en facturas colombianas"
echo "   🔍 Campos: 9 campos a extraer"
echo ""

echo "🌐 Ejecutando API..."
echo ""

# Ejecutar curl con la factura
curl -X POST "http://159.203.149.247:8000/api/v1/documents/process-upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@tests/Documentos/Invoice_2082463105.pdf" \
  -F "processing_mode=gpt_vision_only" \
  -F "prompt_general=Actúa como un analista financiero experto especializado en facturas colombianas. Analiza la siguiente factura de un proveedor y extrae los campos detallados a continuación de forma precisa. Si un campo no está presente, devuélvelo como null. Para fechas, usa formato YYYY-MM-DD. Para montos, extrae solo el valor numérico sin símbolos de moneda." \
  -F "fields_config=[{\"name\":\"numero_factura\",\"type\":\"string\",\"description\":\"El identificador único de la factura. Busca en frases que contengan Factura o Invoice Number\"},{\"name\":\"fecha_factura\",\"type\":\"date\",\"description\":\"La fecha de emisión de la factura. Busca invoice date en la parte superior del documento y formatéala como YYYY-MM-DD.\"},{\"name\":\"proveedor_nombre\",\"type\":\"string\",\"description\":\"El nombre completo de la empresa o persona que emite la factura. Busca en la parte superior izquierda del documento.\"},{\"name\":\"cliente_nombre\",\"type\":\"string\",\"description\":\"El nombre de la empresa o persona a quien se factura. Busca en la parte superior derecha del documento.\"},{\"name\":\"total_a_pagar\",\"type\":\"number\",\"description\":\"El valor final y total de la factura después de todos los impuestos. Es el monto más grande y destacado en la sección de totales. o el Total Amount\"},{\"name\":\"items_de_linea\",\"type\":\"array\",\"description\":\"Extrae todos los productos o servicios listados en la tabla de la factura. Cada línea debe ser un objeto JSON separado dentro de este array, con las claves: descripcion, y total_linea.\"},{\"name\":\"condiciones_pago\",\"type\":\"string\",\"description\":\"Las condiciones de pago especificadas en la factura. Por ejemplo: 30 días, contado, etc.\"},{\"name\":\"moneda\",\"type\":\"string\",\"description\":\"La moneda en la que está expresada la factura. Por ejemplo: COP, USD, EUR.\"},{\"name\":\"observaciones\",\"type\":\"string\",\"description\":\"Cualquier observación o nota adicional que aparezca en la factura.\"}]" \
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
