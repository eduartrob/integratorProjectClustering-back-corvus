import io
import logging
import pdfplumber
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from app.core.config import settings

logger = logging.getLogger(__name__)

class DriveService:
    def __init__(self):
        # NOTA: En producción, esto debería inicializarse con las credenciales reales
        # Por ahora lo dejamos preparado para la inyección de token
        self.scopes = ['https://www.googleapis.com/auth/drive.readonly']
        
    def get_drive_service(self, access_token: str):
        """Inicializa el cliente de Google Drive usando un token de acceso."""
        creds = Credentials(token=access_token)
        return build('drive', 'v3', credentials=creds)

    def download_pdf_to_memory(self, file_id: str, access_token: str) -> io.BytesIO:
        """
        Descarga el PDF directamente a la memoria RAM sin tocar el disco duro.
        ¡Zero-trust y ahorro de almacenamiento!
        """
        service = self.get_drive_service(access_token)
        request = service.files().get_media(fileId=file_id)
        
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            if status:
                logger.info(f"Descargando {file_id}: {int(status.progress() * 100)}%")
                
        file_stream.seek(0)
        return file_stream

    def extract_text_from_pdf_stream(self, file_stream: io.BytesIO) -> str:
        """
        Lee el PDF desde la memoria RAM y extrae todo su texto usando pdfplumber.
        """
        full_text = ""
        try:
            with pdfplumber.open(file_stream) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
        except Exception as e:
            logger.error(f"Error extrayendo texto del PDF: {str(e)}")
            
        return full_text

    def process_drive_file(self, file_id: str, access_token: str) -> str:
        """
        Orquestador: Descarga el archivo a RAM y devuelve su texto limpio.
        """
        logger.info(f"Iniciando procesamiento en memoria para el archivo Drive: {file_id}")
        pdf_stream = self.download_pdf_to_memory(file_id, access_token)
        text = self.extract_text_from_pdf_stream(pdf_stream)
        return text

    def get_files_in_folder(self, folder_id: str, access_token: str) -> list:
        """
        Obtiene la lista de archivos PDF dentro de una carpeta específica de Drive.
        Retorna lista de diccionarios: [{"id": "...", "name": "..."}]
        """
        try:
            service = self.get_drive_service(access_token)
            query = f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false"
            
            results = service.files().list(
                q=query,
                fields="nextPageToken, files(id, name)",
                pageSize=100
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Se encontraron {len(files)} PDFs en la carpeta {folder_id}")
            return files
        except Exception as e:
            logger.error(f"Error listando archivos en la carpeta {folder_id}: {str(e)}")
            return []

drive_service = DriveService()
