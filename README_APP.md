# 🎙️ Transcriptor Multimedia con IA Local

Aplicación web que permite extraer diálogos de archivos de audio/video, generar resúmenes y traducir al español usando modelos de IA locales.

## Características

- ✅ **Transcripción automática** de audio/video a texto usando Whisper
- ✅ **Resumen automático** del contenido transcrito
- ✅ **Traducción al español** si el contenido está en otro idioma
- ✅ **Interfaz web amigable** con Gradio
- ✅ **Procesamiento 100% local** - tus datos no salen de tu máquina

## Requisitos

- Python 3.8+
- FFmpeg (para procesamiento de audio/video)

## Instalación

### 1. Instalar dependencias de Python

```bash
pip install openai-whisper gradio torch transformers sentence-transformers
```

### 2. Instalar FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update && sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Descargar desde https://ffmpeg.org/download.html

## Uso

### Ejecutar la aplicación

```bash
python app.py
```

La aplicación se abrirá en `http://localhost:7860`

### Cómo usar

1. Abre tu navegador en `http://localhost:7860`
2. Sube un archivo de audio o video (MP3, WAV, MP4, AVI, MKV, etc.)
3. Selecciona el tamaño del modelo Whisper:
   - `tiny`: Más rápido, menos preciso
   - `base`: Equilibrado (recomendado)
   - `small`: Más preciso, más lento
   - `medium`: Muy preciso, lento
   - `large`: Máxima precisión, muy lento
4. Marca las opciones deseadas:
   - Incluir Resumen
   - Incluir Traducción al Español
5. Haz clic en "Procesar Archivo"
6. Espera a que se complete el procesamiento

## Modelos de IA utilizados

| Función | Modelo | Descripción |
|---------|--------|-------------|
| Transcripción | [Whisper](https://github.com/openai/whisper) | Modelo de OpenAI para reconocimiento de voz |
| Resumen | [BART-large-cnn](https://huggingface.co/facebook/bart-large-cnn) | Modelo de Facebook para resumen de texto |
| Traducción | [OPUS-MT en-es](https://huggingface.co/Helsinki-NLP/opus-mt-en-es) | Modelo de Helsinki-NLP para traducción inglés-español |

## Estructura del proyecto

```
/workspace
├── app.py              # Aplicación principal
├── README.md           # Este archivo
└── requirements.txt    # Dependencias de Python
```

## Notas importantes

- **Primera ejecución**: La primera vez que ejecutes la aplicación, descargará los modelos de IA (puede tardar varios minutos dependiendo de tu conexión).
- **Requisitos de hardware**: 
  - GPU recomendada para procesar archivos largos
  - Mínimo 8GB de RAM para modelos medianos
  - Los modelos se descargan automáticamente (~3GB total)
- **Formatos soportados**: Cualquier formato que FFmpeg pueda procesar (MP3, WAV, FLAC, MP4, AVI, MKV, MOV, etc.)

## Solución de problemas

### Error: "No module named 'ffmpeg'"
```bash
pip install ffmpeg-python
```

### Error: "ffmpeg not found"
Instala FFmpeg según las instrucciones arriba.

### La aplicación es muy lenta
- Usa un modelo Whisper más pequeño (`tiny` o `base`)
- Ejecuta en una máquina con GPU

### Error de memoria
- Cierra otras aplicaciones
- Usa un modelo Whisper más pequeño
- Procesa archivos más cortos

## Licencia

Este proyecto es de código abierto bajo licencia MIT.
