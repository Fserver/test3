#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación de Transcripción y Resumen con IA Local

Esta aplicación permite:
1. Subir archivos de audio o video
2. Extraer diálogos usando Whisper (modelo local)
3. Generar un resumen de los diálogos
4. Traducir al español si el contenido está en otro idioma

Requisitos:
- pip install openai-whisper gradio torch transformers sentence-transformers
"""

import gradio as gr
import whisper
import torch
from transformers import pipeline
import os
import tempfile
from datetime import datetime


class MultimediaTranscriber:
    """Clase principal para manejar la transcripción, resumen y traducción."""
    
    def __init__(self):
        self.transcription_model = None
        self.summarization_pipeline = None
        self.translation_pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Usando dispositivo: {self.device}")
        
    def load_models(self, model_size="base"):
        """Carga los modelos de IA."""
        print(f"Cargando modelo Whisper {model_size}...")
        self.transcription_model = whisper.load_model(model_size, device=self.device)
        
        print("Cargando modelo para resumen...")
        # Usar un modelo más ligero para CPU
        self.summarization_pipeline = pipeline(
            "summarization",
            model="sshleifer/distilbart-cnn-12-6",
            device=-1  # Forzar CPU
        )
        
        print("Cargando modelo para traducción...")
        # Usar un modelo más ligero para traducción
        self.translation_pipeline = pipeline(
            "translation",
            model="Helsinki-NLP/opus-mt-en-es",
            device=-1  # Forzar CPU
        )
        
        return "Modelos cargados exitosamente"
    
    def detect_language(self, text):
        """Detecta si el texto está en español o no."""
        # Palabras comunes en español para detección simple
        spanish_words = ['el', 'la', 'los', 'las', 'de', 'que', 'y', 'en', 'un', 'una', 
                        'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'tu', 'su', 'al', 'por',
                        'con', 'para', 'como', 'del', 'los', 'las', 'me', 'mi', 'mis',
                        'tú', 'yo', 'él', 'ella', 'nos', 'son', 'ser', 'estar']
        
        words = text.lower().split()
        spanish_count = sum(1 for word in words if word in spanish_words)
        
        # Si más del 10% de las palabras son españolas, asumimos que está en español
        if len(words) > 0 and (spanish_count / len(words)) > 0.1:
            return "español"
        return "otro"
    
    def transcribe(self, audio_path, model_size="base"):
        """Transcribe el archivo de audio/video a texto."""
        if self.transcription_model is None:
            self.load_models(model_size)
        elif model_size != "base":
            self.transcription_model = whisper.load_model(model_size, device=self.device)
        
        result = self.transcription_model.transcribe(audio_path)
        return result["text"], result.get("language", "unknown")
    
    def summarize(self, text, max_length=150, min_length=50):
        """Genera un resumen del texto transcrito."""
        if self.summarization_pipeline is None:
            self.load_models()
        
        # Dividir el texto si es muy largo (BART tiene límite de tokens)
        max_input_length = 1024
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_input_length:
                current_chunk += sentence + '. '
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + '. '
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        summaries = []
        for chunk in chunks:
            if len(chunk) > 50:  # Solo resumir si hay suficiente texto
                summary = self.summarization_pipeline(
                    chunk,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )[0]['summary_text']
                summaries.append(summary)
        
        return ' '.join(summaries) if summaries else text[:500] + "..."
    
    def translate_to_spanish(self, text):
        """Traduce el texto al español."""
        if self.translation_pipeline is None:
            self.load_models()
        
        # Dividir el texto si es muy largo
        max_length = 512
        sentences = text.split('. ')
        translations = []
        
        for sentence in sentences:
            if len(sentence) > 10:  # Solo traducir oraciones significativas
                translation = self.translation_pipeline(
                    sentence,
                    max_length=max_length
                )[0]['translation_text']
                translations.append(translation)
        
        return '. '.join(translations)
    
    def process_file(self, file_path, model_size="base", include_summary=True, 
                     include_translation=True):
        """Procesa el archivo completo: transcripción, resumen y traducción."""
        if file_path is None:
            return "Error: No se proporcionó ningún archivo", "", "", ""
        
        try:
            # Transcripción
            transcription, detected_lang = self.transcribe(file_path, model_size)
            
            # Detectar si necesita traducción
            lang_status = self.detect_language(transcription)
            needs_translation = lang_status == "otro" and include_translation
            
            # Resumen
            summary = ""
            if include_summary and len(transcription) > 100:
                summary = self.summarize(transcription)
            
            # Traducción
            translation = ""
            if needs_translation:
                translation = self.translate_to_spanish(transcription)
            elif lang_status == "español":
                translation = "El contenido ya está en español, no se requiere traducción."
            
            # Formatear resultados
            result_text = f"""
=== TRANSCRIPCIÓN ===
Idioma detectado: {detected_lang}
{transcription}
"""
            
            if summary:
                result_text += f"\n\n=== RESUMEN ===\n{summary}"
            
            if translation:
                result_text += f"\n\n=== TRADUCCIÓN AL ESPAÑOL ===\n{translation}"
            
            return result_text, transcription, summary, translation
            
        except Exception as e:
            return f"Error al procesar el archivo: {str(e)}", "", "", ""


def create_interface():
    """Crea la interfaz de Gradio."""
    transcriber = MultimediaTranscriber()
    
    with gr.Blocks(title="Transcriptor Multimedia con IA", theme=gr.themes.Soft()) as app:
        gr.Markdown("""
        # 🎙️ Transcriptor Multimedia con IA Local
        
        Sube un archivo de **audio** o **video** para:
        - 📝 Extraer los diálogos automáticamente
        - 📋 Obtener un resumen del contenido
        - 🌐 Traducir al español si está en otro idioma
        
        *Todo se procesa localmente con modelos de IA*
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                file_input = gr.File(
                    label="📁 Archivo de Audio/Video",
                    file_types=["audio", "video"],
                    type="filepath"
                )
                
                model_choice = gr.Dropdown(
                    choices=["tiny", "base", "small", "medium", "large"],
                    value="base",
                    label="Tamaño del Modelo Whisper",
                    info="Modelos más grandes = mejor precisión pero más lento"
                )
                
                include_summary = gr.Checkbox(
                    value=True,
                    label="Incluir Resumen"
                )
                
                include_translation = gr.Checkbox(
                    value=True,
                    label="Incluir Traducción al Español (si es necesario)"
                )
                
                process_btn = gr.Button("🚀 Procesar Archivo", variant="primary", size="lg")
                
            with gr.Column(scale=2):
                output_full = gr.Textbox(
                    label="Resultado Completo",
                    lines=15,
                    show_copy_button=True
                )
                
                with gr.Accordion("📄 Ver solo Transcripción", open=False):
                    output_transcription = gr.Textbox(
                        label="Transcripción",
                        lines=8,
                        show_copy_button=True
                    )
                
                with gr.Accordion("📋 Ver solo Resumen", open=False):
                    output_summary = gr.Textbox(
                        label="Resumen",
                        lines=6,
                        show_copy_button=True
                    )
                
                with gr.Accordion("🌐 Ver solo Traducción", open=False):
                    output_translation = gr.Textbox(
                        label="Traducción al Español",
                        lines=8,
                        show_copy_button=True
                    )
        
        gr.Markdown("""
        ---
        ### ℹ️ Información:
        - **Modelos disponibles**: tiny, base, small, medium, large
        - **Formatos soportados**: MP3, WAV, MP4, AVI, MKV, etc.
        - **Procesamiento**: Todo se ejecuta localmente en tu máquina
        - **Tiempo estimado**: Depende del tamaño del archivo y modelo seleccionado
        """)
        
        # Conectar el botón de procesamiento
        process_btn.click(
            fn=transcriber.process_file,
            inputs=[file_input, model_choice, include_summary, include_translation],
            outputs=[output_full, output_transcription, output_summary, output_translation]
        )
    
    return app


if __name__ == "__main__":
    app = create_interface()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)
