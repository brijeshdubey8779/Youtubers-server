# Kafka Email Notification System Setup

This document explains how to set up and run the Kafka-based email notification system for YouTubers Modern.

## 🚀 Quick Start

### 1. Install Dependencies

The required packages are already in `requirements.txt`:
- kafka-python==2.0.2
- celery==5.4.0
- redis==5.2.1
- django-environ==0.11.2

### 2. Install and Start Kafka

#### Option A: Using Docker (Recommended)
```bash
# Start Kafka with Docker Compose
docker run -p 2181:2181 -p 9092:9092 --env ADVERTISED_HOST=localhost --env ADVERTISED_PORT=9092 spotify/kafka
```

#### Option B: Manual Installation
1. Download Kafka from https://kafka.apache.org/downloads
2. Extract and start Zookeeper: `bin/zookeeper-server-start.sh config/zookeeper.properties`
3. Start Kafka: `bin/kafka-server-start.sh config/server.properties`

### 3. Configure Environment Variables

Create a `.env` file in the backend directory:

```env
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
DEFAULT_FROM_EMAIL=YouTubers Modern <noreply@youtubersmodern.com>

# For testing, use console backend:
# EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_EMAIL_TOPIC=email_notifications
KAFKA_CONSUMER_GROUP=email_service_group
KAFKA_AUTO_OFFSET_RESET=latest
KAFKA_ENABLE_AUTO_COMMIT=True

# Redis (for Celery backup)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 4. Gmail Setup (for SMTP)

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → App passwords
   - Generate password for "Mail"
   - Use this password in `EMAIL_HOST_PASSWORD`

### 5. Start the Email Consumer

Open a new terminal and run:
```bash
cd backend
source venv/bin/activate
python manage.py start_email_consumer
```

Keep this running to process email notifications.

### 6. Test the Email System

```bash
# Send a test email
python manage.py start_email_consumer --test-email your-email@example.com
```

## 📧 How It Works

### Contact Form Flow:
1. User submits contact form → `POST /api/contactpage/`
2. Contact saved to database
3. Kafka producer sends email message to `email_notifications` topic
4. Kafka consumer processes message and sends confirmation email

### YouTuber Inquiry Flow:
1. User submits YouTuber inquiry → `POST /api/youtubers/inquiry/`
2. Inquiry saved to database with YouTuber reference
3. Kafka producer sends email message
4. Consumer sends personalized confirmation email with YouTuber details

## 🛠️ API Endpoints

### Contact Form
```bash
POST /api/contactpage/
{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "subject": "Hello",
    "message": "I'm interested in your services",
    "city": "New York",
    "state": "NY"
}
```

### YouTuber Inquiry
```bash
POST /api/youtubers/inquiry/
{
    "youtuber": 1,
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@example.com",
    "phone": "+1234567890",
    "company_name": "My Company",
    "inquiry_type": "collaboration",
    "budget_range": "5k_10k",
    "subject": "Collaboration Opportunity",
    "message": "We'd like to collaborate with this YouTuber",
    "target_audience": "Tech enthusiasts",
    "deliverables": "2 sponsored videos"
}
```

## 🔧 Troubleshooting

### Email Not Sending
1. Check Kafka is running: `netstat -an | grep 9092`
2. Check consumer is running and processing messages
3. Verify email credentials in `.env`
4. Check Django logs for errors

### Kafka Connection Issues
1. Ensure Kafka is running on `localhost:9092`
2. Check firewall settings
3. Verify `KAFKA_BOOTSTRAP_SERVERS` in settings

### Test Mode
For development, use console email backend:
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```
This will print emails to console instead of sending them.

## 📱 Frontend Integration

Add contact functionality to YouTuber detail pages:

```javascript
// Submit YouTuber inquiry
const submitInquiry = async (inquiryData) => {
    const response = await api.post('/youtubers/inquiry/', inquiryData);
    if (response.status === 201) {
        // Show success message
        alert('Your inquiry has been submitted! Check your email for confirmation.');
    }
};
```

## 🚀 Production Deployment

1. Use managed Kafka service (AWS MSK, Confluent Cloud)
2. Set up proper email service (SendGrid, AWS SES)
3. Configure SSL certificates
4. Set up monitoring and logging
5. Use environment-specific configurations

## 📊 Monitoring

Monitor the email system:
- Kafka topic lag
- Email delivery rates
- Error logs
- Consumer processing time

## 🔒 Security

- Use app passwords for Gmail
- Rotate email credentials regularly
- Monitor for suspicious activity
- Set up rate limiting for API endpoints 