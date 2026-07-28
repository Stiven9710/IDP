#!/usr/bin/env python3
"""
Script de configuración para la consolidación de extracciones
Instala dependencias y configura el entorno
"""

import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Instalar dependencias necesarias"""
    try:
        print("📦 Instalando dependencias necesarias...")
        
        dependencies = [
            "pandas",
            "openpyxl",
            "azure-cosmos"
        ]
        
        for dep in dependencies:
            print(f"   Instalando {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"   ✅ {dep} instalado")
        
        print("✅ Todas las dependencias instaladas correctamente")
        
    except Exception as e:
        print(f"❌ Error instalando dependencias: {e}")
        sys.exit(1)

def check_environment():
    """Verificar configuración del entorno"""
    try:
        print("🔍 Verificando configuración del entorno...")
        
        # Verificar archivo .env
        env_file = Path(".env")
        if not env_file.exists():
            print("⚠️ Archivo .env no encontrado")
            print("   Crea un archivo .env con las credenciales de Azure")
            return False
        
        print("✅ Archivo .env encontrado")
        
        # Verificar variables de entorno necesarias
        required_vars = [
            "AZURE_COSMOS_ENDPOINT",
            "AZURE_COSMOS_KEY",
            "AZURE_COSMOS_DATABASE_NAME"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️ Variables de entorno faltantes: {missing_vars}")
            return False
        
        print("✅ Variables de entorno configuradas")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando entorno: {e}")
        return False

def create_output_directory():
    """Crear directorio de salida para archivos Excel"""
    try:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        print(f"✅ Directorio de salida creado: {output_dir.absolute()}")
        return True
        
    except Exception as e:
        print(f"❌ Error creando directorio de salida: {e}")
        return False

def main():
    """Función principal de configuración"""
    try:
        print("🚀 CONFIGURANDO ENTORNO DE CONSOLIDACIÓN")
        print("="*50)
        
        # Instalar dependencias
        install_dependencies()
        
        # Verificar entorno
        if not check_environment():
            print("❌ Configuración del entorno incompleta")
            sys.exit(1)
        
        # Crear directorio de salida
        create_output_directory()
        
        print("\n✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
        print("   Ahora puedes ejecutar: python scripts/consolidate_extractions.py")
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
