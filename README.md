# 🏫 Sistema de Monitoreo de Aulas - ISAE Primaria

Sistema web en tiempo real para monitorear la asistencia de los 7 grados de educación primaria del **Instituto Superior Albert Einstein (ISAE)**.

## 📋 Descripción

Este sistema permite visualizar el estado (OK/FALTA/SIN DATOS) de cada aula de primaria en tiempo real, con un registro histórico de todos los cambios y capacidad de exportar datos para análisis posterior.

### Características principales

- ✅ **Monitoreo en tiempo real** - Actualización automática cada 2 segundos
- 📊 **Visualización de 7 grados** - Desde 1ro hasta 7mo de primaria
- 🎨 **Diseño responsive** - Optimizado para celulares, tablets y computadoras
- 🎮 **Panel de control** - Interfaz táctil para cambiar estados fácilmente
- 📈 **Estadísticas en vivo** - Contador de aulas OK/FALTA y métricas de uso
- 📜 **Historial completo** - Registro de todos los cambios con fecha, hora e IP
- 🔄 **Auto-refresco configurable** - en historial (5s, 10s, 30s, 60s o pausa)
- 📄 **Exportación a CSV** - Datos en 6 columnas para filtrar por aula
- 🗄️ **Auto-limpieza** - Mantiene solo 7 días de historial automáticamente
- 🖼️ **Doble identidad visual** - Logos institucional y del cluster tecnológico
- 📱 **Botón flotante** - Acceso rápido al panel de control desde móviles

## 🚀 Instalación

### Requisitos previos
- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. **Clonar o descargar el proyecto**
```bash
git clone https://github.com/TU_USUARIO/monitoreo-isae-primaria.git
cd monitoreo-isae-primaria