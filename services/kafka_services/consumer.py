import json
import logging
import threading
import time
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailKafkaConsumer:
    """
    Kafka consumer service for processing email notification messages.
    """
    
    def __init__(self):
        self.consumer = None
        self.topic = settings.KAFKA_SETTINGS['EMAIL_TOPIC']
        self.running = False
        self.consumer_thread = None
        self._connect()
    
    def _connect(self) -> None:
        """Initialize Kafka consumer connection."""
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=settings.KAFKA_SETTINGS['BOOTSTRAP_SERVERS'],
                group_id=settings.KAFKA_SETTINGS['CONSUMER_GROUP'],
                auto_offset_reset=settings.KAFKA_SETTINGS['AUTO_OFFSET_RESET'],
                enable_auto_commit=settings.KAFKA_SETTINGS['ENABLE_AUTO_COMMIT'],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                consumer_timeout_ms=5000,
                max_poll_interval_ms=300000,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000
            )
            logger.info("Kafka consumer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka consumer: {str(e)}")
            self.consumer = None
    
    def start(self) -> bool:
        """
        Start the Kafka consumer in a separate thread.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        if self.running:
            logger.warning("Consumer is already running")
            return True
            
        if not self.consumer:
            logger.error("Kafka consumer not initialized")
            return False
        
        try:
            self.running = True
            self.consumer_thread = threading.Thread(target=self._consume_messages)
            self.consumer_thread.daemon = True
            self.consumer_thread.start()
            logger.info("Kafka consumer started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {str(e)}")
            self.running = False
            return False
    
    def stop(self) -> None:
        """Stop the Kafka consumer."""
        self.running = False
        if self.consumer:
            try:
                self.consumer.close()
                logger.info("Kafka consumer stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping Kafka consumer: {str(e)}")
        
        if self.consumer_thread and self.consumer_thread.is_alive():
            self.consumer_thread.join(timeout=10)
    
    def _consume_messages(self) -> None:
        """Main consumer loop to process email messages."""
        logger.info("Starting email message consumption...")
        
        while self.running:
            try:
                for message in self.consumer:
                    if not self.running:
                        break
                    
                    try:
                        email_data = message.value
                        logger.info(f"Processing email message: {email_data.get('message_id', 'unknown')}")
                        
                        # Process the email message
                        success = self._process_email_message(email_data)
                        
                        if success:
                            logger.info(f"Email sent successfully: {email_data.get('message_id', 'unknown')}")
                        else:
                            logger.error(f"Failed to send email: {email_data.get('message_id', 'unknown')}")
                            # TODO: Implement retry logic or dead letter queue
                        
                    except Exception as e:
                        logger.error(f"Error processing message: {str(e)}")
                        continue
                        
            except KafkaError as e:
                logger.error(f"Kafka error in consumer: {str(e)}")
                if self.running:
                    time.sleep(5)  # Wait before retrying
                    
            except Exception as e:
                logger.error(f"Unexpected error in consumer: {str(e)}")
                if self.running:
                    time.sleep(5)  # Wait before retrying
    
    def _process_email_message(self, email_data: Dict[str, Any]) -> bool:
        """
        Process and send email message.
        
        Args:
            email_data: Email message data from Kafka
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Extract email data
            recipient = email_data.get('recipient')
            subject = email_data.get('subject')
            template = email_data.get('template')
            context = email_data.get('context', {})
            email_type = email_data.get('type')
            
            if not all([recipient, subject, template]):
                logger.error(f"Missing required email data: recipient={recipient}, subject={subject}, template={template}")
                return False
            
            # Render email template
            html_content = render_to_string(f'emails/{template}', context)
            text_content = strip_tags(html_content)
            
            # Create and send email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient]
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send()
            
            logger.info(f"Email sent successfully to {recipient} with subject '{subject}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process email message: {str(e)}")
            return False
    
    def send_test_email(self, recipient: str) -> bool:
        """
        Send a test email to verify email configuration.
        
        Args:
            recipient: Email address to send test email to
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            test_message = {
                'type': 'test_email',
                'template': 'contact_confirmation.html',
                'recipient': recipient,
                'subject': 'Test Email - YouTubers Modern Email Service',
                'context': {
                    'first_name': 'Test',
                    'last_name': 'User',
                    'email': recipient,
                    'phone': '+1 (234) 567-8900',
                    'city': 'Test City',
                    'state': 'Test State',
                    'subject': 'Test Email Subject',
                    'message': 'This is a test email to verify the email service is working correctly.',
                    'created_date': datetime.now(),
                }
            }
            
            return self._process_email_message(test_message)
            
        except Exception as e:
            logger.error(f"Failed to send test email: {str(e)}")
            return False


# Singleton instance
_consumer_instance = None

def get_email_consumer() -> EmailKafkaConsumer:
    """
    Get singleton instance of EmailKafkaConsumer.
    
    Returns:
        EmailKafkaConsumer: Singleton consumer instance
    """
    global _consumer_instance
    if _consumer_instance is None:
        _consumer_instance = EmailKafkaConsumer()
    return _consumer_instance


def start_email_consumer() -> bool:
    """
    Start the email consumer service.
    
    Returns:
        bool: True if started successfully, False otherwise
    """
    consumer = get_email_consumer()
    return consumer.start()


def stop_email_consumer() -> None:
    """Stop the email consumer service."""
    global _consumer_instance
    if _consumer_instance:
        _consumer_instance.stop()
        _consumer_instance = None 