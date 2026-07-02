import io
import logging
import fitz
import pymupdf4llm
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os
from app.core.config import settings
from app.core.config_manager import config_manager

logger = logging.getLogger(__name__)

class DriveService:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/drive.readonly']
        self.credentials_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'google_service_account.json')
        
    def get_drive_service(self, access_token: str = None):
        if not os.path.exists(self.credentials_path):
            logger.error(f"Falta el archivo de credenciales de Google Drive en: {self.credentials_path}")
            raise Exception("Archivo google_service_account.json no encontrado.")
            
        creds = service_account.Credentials.from_service_account_file(
            self.credentials_path, scopes=self.scopes
        )
        return build('drive', 'v3', credentials=creds)

    def download_pdf_to_memory(self, file_id: str, access_token: str) -> io.BytesIO:
        
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

    def extract_text_from_stream(self, file_stream: io.BytesIO, file_name: str) -> str:
        
        full_text = ""
        try:
            name_lower = file_name.lower()
            if name_lower.endswith('.pdf'):
                file_bytes = file_stream.read()
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                full_text = pymupdf4llm.to_markdown(doc)
            elif name_lower.endswith('.md') or name_lower.endswith('.txt'):
                full_text = file_stream.read().decode('utf-8')
            else:
                logger.warning(f"Formato no soportado para el archivo: {file_name}")
        except Exception as e:
            logger.error(f"Error extrayendo texto del archivo {file_name}: {str(e)}")
            
        return full_text

    def process_drive_file(self, file_id: str, file_name: str, access_token: str) -> str:
        
        logger.info(f"Iniciando procesamiento en memoria para el archivo Drive: {file_name}")
        file_stream = self.download_pdf_to_memory(file_id, access_token)
        text = self.extract_text_from_stream(file_stream, file_name)
        return text

    def get_files_in_folder(self, folder_id: str, access_token: str) -> list:
        
        try:
            print(f"Iniciando búsqueda en Drive para la carpeta: {folder_id}", flush=True)
            service = self.get_drive_service(access_token)
            query = f"'{folder_id}' in parents and trashed=false"
            
            results = service.files().list(
                q=query,
                fields="nextPageToken, files(id, name)",
                pageSize=100
            ).execute()
            
            allowed_exts = config_manager.get_allowed_extensions()
            all_files = results.get('files', [])
            files = [f for f in all_files if f.get('name', '').lower().endswith(allowed_exts)]
            print(f"Se encontraron {len(files)} PDFs en la carpeta {folder_id}", flush=True)
            return files
        except Exception as e:
            print(f"Error crítico en Google Drive listando archivos: {str(e)}", flush=True)
            import traceback
            traceback.print_exc()
            return []

drive_service = DriveService()
