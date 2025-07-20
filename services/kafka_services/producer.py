import json
import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError
from django.conf import settings
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailKafkaProducer:
    """
    Kafka producer service for sending email notification messages.
    """
    
    def __init__(self):
        self.producer = None
        self.topic = settings.KAFKA_SETTINGS['EMAIL_TOPIC']
        self._connect()
    
    def _connect(self) -> None:
        """Initialize Kafka producer connection."""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_SETTINGS['BOOTSTRAP_SERVERS'],
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                retries=3,
                acks='all',
                batch_size=16384,
                linger_ms=10,
                buffer_memory=33554432,
                max_request_size=1048576
            )
            logger.info("Kafka producer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {str(e)}")
            self.producer = None
    
    def send_contact_confirmation_email(self, contact_data: Dict[str, Any]) -> bool:
        """
        Send contact confirmation email message to Kafka.
        
        Args:
            contact_data: Dictionary containing contact form data
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        try:
            email_message = {
                'type': 'contact_confirmation',
                'template': 'contact_confirmation.html',
                'recipient': contact_data.get('email'),
                'subject': f"Thank You for Contacting Us - YouTubers Modern",
                'context': {
                    'first_name': contact_data.get('first_name', ''),
                    'last_name': contact_data.get('last_name', ''),
                    'email': contact_data.get('email'),
                    'phone': contact_data.get('phone', ''),
                    'city': contact_data.get('city', ''),
                    'state': contact_data.get('state', ''),
                    'subject': contact_data.get('subject'),
                    'message': contact_data.get('message'),
                    'created_date': contact_data.get('created_date', datetime.now()),
                },
                'priority': 'normal',
                'created_at': datetime.now().isoformat(),
                'message_id': f"contact_{contact_data.get('id', '')}_{int(datetime.now().timestamp())}"
            }
            
            return self._send_message(email_message, key=f"contact_{contact_data.get('id', '')}")
            
        except Exception as e:
            logger.error(f"Failed to send contact confirmation email message: {str(e)}")
            return False
    
    def send_youtuber_inquiry_email(self, inquiry_data: Dict[str, Any], youtuber_data: Dict[str, Any]) -> bool:
        """
        Send YouTuber inquiry confirmation email message to Kafka.
        
        Args:
            inquiry_data: Dictionary containing inquiry form data
            youtuber_data: Dictionary containing YouTuber information
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        try:
            email_message = {
                'type': 'youtuber_inquiry_confirmation',
                'template': 'youtuber_contact_confirmation.html',
                'recipient': inquiry_data.get('email'),
                'subject': f"Your Inquiry About {youtuber_data.get('name')} - YouTubers Modern",
                'context': {
                    'first_name': inquiry_data.get('first_name', ''),
                    'last_name': inquiry_data.get('last_name', ''),
                    'email': inquiry_data.get('email'),
                    'phone': inquiry_data.get('phone', ''),
                    'message': inquiry_data.get('message', ''),
                    'youtuber_name': youtuber_data.get('name'),
                    'youtuber_category': youtuber_data.get('category'),
                    'youtuber_id': youtuber_data.get('id'),
                    'created_date': inquiry_data.get('created_date', datetime.now()),
                },
                'priority': 'high',
                'created_at': datetime.now().isoformat(),
                'message_id': f"youtuber_inquiry_{inquiry_data.get('id', '')}_{int(datetime.now().timestamp())}"
            }
            
            return self._send_message(email_message, key=f"youtuber_inquiry_{inquiry_data.get('id', '')}")
            
        except Exception as e:
            logger.error(f"Failed to send YouTuber inquiry email message: {str(e)}")
            return False
    
    def send_custom_email(self, recipient: str, subject: str, template: str, context: Dict[str, Any], priority: str = 'normal') -> bool:
        """
        Send custom email message to Kafka.
        
        Args:
            recipient: Email address of the recipient
            subject: Email subject
            template: Template name to use
            context: Template context data
            priority: Message priority (high, normal, low)
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        try:
            email_message = {
                'type': 'custom_email',
                'template': template,
                'recipient': recipient,
                'subject': subject,
                'context': context,
                'priority': priority,
                'created_at': datetime.now().isoformat(),
                'message_id': f"custom_{int(datetime.now().timestamp())}"
            }
            
            return self._send_message(email_message, key=f"custom_{recipient}")
            
        except Exception as e:
            logger.error(f"Failed to send custom email message: {str(e)}")
            return False
    
    def _send_message(self, message: Dict[str, Any], key: Optional[str] = None) -> bool:
        """
        Send message to Kafka topic.
        
        Args:
            message: Message data to send
            key: Optional message key for partitioning
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.producer:
            logger.error("Kafka producer not initialized")
            return False
        
        try:
            future = self.producer.send(self.topic, value=message, key=key)
            
            # Wait for message to be sent (with timeout)
            record_metadata = future.get(timeout=10)
            
            logger.info(f"Message sent successfully to topic {record_metadata.topic}, "
                       f"partition {record_metadata.partition}, offset {record_metadata.offset}")
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error sending message: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {str(e)}")
            return False
    
    def close(self) -> None:
        """Close the Kafka producer connection."""
        if self.producer:
            try:
                self.producer.flush()
                self.producer.close()
                logger.info("Kafka producer closed successfully")
            except Exception as e:
                logger.error(f"Error closing Kafka producer: {str(e)}")


# Singleton instance
_producer_instance = None

def get_email_producer() -> EmailKafkaProducer:
    """
    Get singleton instance of EmailKafkaProducer.
    
    Returns:
        EmailKafkaProducer: Singleton producer instance
    """
    global _producer_instance
    if _producer_instance is None:
        _producer_instance = EmailKafkaProducer()
    return _producer_instance 