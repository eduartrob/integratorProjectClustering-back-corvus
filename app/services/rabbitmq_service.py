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
                credentials=credentials
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.channel.exchange_declare(exchange=self.exchange, exchange_type='topic')
            logger.info("✅ Conectado a RabbitMQ (Clustering Publisher)")
        except Exception as e:
            logger.error(f"❌ Error conectando a RabbitMQ: {str(e)}")

    def publish_progress(self, user_id: str, type_event: str, progress: int, total: int, message: str):
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
                
                # El microservicio de notificaciones escuchará 'sync.progress'
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

rabbitmq_service = RabbitMQService()
