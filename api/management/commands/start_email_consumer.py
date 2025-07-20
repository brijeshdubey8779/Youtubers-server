import signal
import sys
from django.core.management.base import BaseCommand
from services.kafka_services.consumer import start_email_consumer, stop_email_consumer


class Command(BaseCommand):
    """Django management command to start the Kafka email consumer."""
    
    help = 'Start the Kafka email consumer service'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--test-email',
            type=str,
            help='Send a test email to the specified address and exit'
        )
    
    def handle(self, *args, **options):
        # Handle test email option
        if options['test_email']:
            self.send_test_email(options['test_email'])
            return
        
        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            self.stdout.write(
                self.style.WARNING('\nReceived interrupt signal. Shutting down email consumer...')
            )
            stop_email_consumer()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start the email consumer
        self.stdout.write(
            self.style.SUCCESS('Starting Kafka email consumer...')
        )
        
        try:
            success = start_email_consumer()
            if success:
                self.stdout.write(
                    self.style.SUCCESS('Email consumer started successfully. Press Ctrl+C to stop.')
                )
                
                # Keep the main thread alive
                try:
                    while True:
                        import time
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
            else:
                self.stdout.write(
                    self.style.ERROR('Failed to start email consumer. Check logs for details.')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error starting email consumer: {str(e)}')
            )
        finally:
            stop_email_consumer()
            self.stdout.write(
                self.style.SUCCESS('Email consumer stopped.')
            )
    
    def send_test_email(self, recipient):
        """Send a test email and exit."""
        self.stdout.write(f'Sending test email to {recipient}...')
        
        try:
            from services.kafka_services.consumer import get_email_consumer
            consumer = get_email_consumer()
            success = consumer.send_test_email(recipient)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'Test email sent successfully to {recipient}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Failed to send test email to {recipient}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error sending test email: {str(e)}')
            ) 