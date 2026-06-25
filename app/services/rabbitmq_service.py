import pika
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class RabbitMQService:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = "corvus_events"
        self._connect()

    def _connect(self):
        try:
            # En docker-compose el broker es 'rabbitmq' y las credenciales son corvus_admin:corvus_secret
            import os
            credentials = pika.PlainCredentials(
                os.getenv('RABBITMQ_USER', 'corvus_admin'), 
                os.getenv('RABBITMQ_PASS', 'corvus_secret')
            )
            parameters = pika.ConnectionParameters(
                host=os.getenv('RABBITMQ_HOST', 'rabbitmq'),
                credentials=credentials,
                heartbeat=0  # Deshabilitamos heartbeats para que RabbitMQ no cierre la conexión si el backend está inactivo
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.channel.exchange_declare(exchange=self.exchange, exchange_type='topic', durable=True)
            logger.info("✅ Conectado a RabbitMQ (Clustering Publisher)")
        except Exception as e:
            logger.error(f"❌ Error conectando a RabbitMQ: {str(e)}")

    def publish_progress(self, user_id: str, type_event: str, progress: int, total: int, message: str, retry: bool = True):
        if not self.channel or self.connection.is_closed:
            self._connect()
            
        if self.channel:
            try:
                payload = {
                    "user_id": user_id,
                    "type": type_event,
                    "progress": progress,
                    "total": total,
                    "message": message
                }
                
                routing_key = 'sync.progress'
                self.channel.basic_publish(
                    exchange=self.exchange,
                    routing_key=routing_key,
                    body=json.dumps(payload),
                    properties=pika.BasicProperties(
                        delivery_mode=2, # hacer mensaje persistente
                    )
                )
            except Exception as e:
                logger.error(f"Error publicando mensaje en RabbitMQ: {str(e)}")
                # Si la conexión se perdió sin que Pika se diera cuenta, reconectamos y reintentamos 1 vez
                if retry:
                    logger.info("Intentando reconectar a RabbitMQ y reenviar mensaje...")
                    self._connect()
                    self.publish_progress(user_id, type_event, progress, total, message, retry=False)

rabbitmq_service = RabbitMQService()
