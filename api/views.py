from django.shortcuts import render
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
import logging

from .serializers import (
    UserSerializer, UserRegistrationSerializer, YoutubersSerializer, 
    YoutubersListSerializer, TeamSerializer, SliderSerializer, 
    ContactinfoSerializer, ContactpageSerializer,
    YouTuberInquirySerializer,
    # Creator Authentication Serializers
    CreatorRegistrationSerializer, CreatorLoginSerializer, CreatorProfileSerializer,
    CreatorInquirySerializer, CreatorInquiryStatusUpdateSerializer
)
from youtubers.models import Youtubers
from webpages.models import Team, Slider, YouTuberInquiry
from contactinfo.models import Contactinfo
from contactpage.models import Contactpage

logger = logging.getLogger(__name__)


# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Create authentication token
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(token),
            'access': str(token.key),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User login endpoint"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            auth_login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(token),
                'access': str(token.key),
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get current user profile"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """User dashboard data"""
    user_data = UserSerializer(request.user).data
    featured_youtubers = Youtubers.objects.filter(is_featured=True)[:6]
    recent_youtubers = Youtubers.objects.all().order_by('-created_date')[:6]
    
    return Response({
        'user': user_data,
        'featured_youtubers': YoutubersListSerializer(featured_youtubers, many=True, context={'request': request}).data,
        'recent_youtubers': YoutubersListSerializer(recent_youtubers, many=True, context={'request': request}).data,
        'total_youtubers': Youtubers.objects.count(),
    })


# YouTubers Views
class YoutubersListView(generics.ListAPIView):
    """List all YouTubers with filtering and search"""
    queryset = Youtubers.objects.all()
    serializer_class = YoutubersListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'crew', 'camera_type', 'is_featured']
    search_fields = ['name', 'city', 'category', 'description']
    ordering_fields = ['price', 'created_date', 'subs_count']
    ordering = ['-created_date']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Additional filtering
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        return queryset


class YoutubersDetailView(generics.RetrieveAPIView):
    """Get detailed YouTuber information"""
    queryset = Youtubers.objects.all()
    serializer_class = YoutubersSerializer
    permission_classes = [AllowAny]


class FeaturedYoutubersView(generics.ListAPIView):
    """List featured YouTubers"""
    queryset = Youtubers.objects.filter(is_featured=True)
    serializer_class = YoutubersListSerializer
    permission_classes = [AllowAny]


# Search Views
@api_view(['GET'])
@permission_classes([AllowAny])
def search_youtubers(request):
    """Advanced search for YouTubers"""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    city = request.GET.get('city', '')
    
    youtubers = Youtubers.objects.all()
    
    if query:
        youtubers = youtubers.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(city__icontains=query)
        )
    
    if category:
        youtubers = youtubers.filter(category=category)
    
    if city:
        youtubers = youtubers.filter(city__icontains=city)
    
    serializer = YoutubersListSerializer(youtubers, many=True, context={'request': request})
    return Response({
        'results': serializer.data,
        'count': youtubers.count()
    })


# Team Views
class TeamListView(generics.ListAPIView):
    """List all team members"""
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [AllowAny]


# Slider Views
class SliderListView(generics.ListAPIView):
    """List all slider items"""
    queryset = Slider.objects.all()
    serializer_class = SliderSerializer
    permission_classes = [AllowAny]


# Contact Views
class ContactpageCreateView(generics.CreateAPIView):
    """Create contact page form submission"""
    queryset = Contactpage.objects.all()
    serializer_class = ContactpageSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        """Save contact and send confirmation email via Kafka or direct email"""
        # Save the contact
        contact = serializer.save()
        
        # Try Kafka first, fallback to direct email if Kafka is not available
        try:
            from services.kafka_services.producer import get_email_producer
            
            # Prepare contact data for email
            contact_data = {
                'id': contact.id,
                'first_name': contact.first_name,
                'last_name': contact.last_name,
                'email': contact.email,
                'phone': contact.phone,
                'city': contact.city,
                'state': contact.state,
                'subject': contact.subject,
                'message': contact.message,
                'created_date': contact.created_date,
            }
            
            # Send email notification via Kafka
            producer = get_email_producer()
            success = producer.send_contact_confirmation_email(contact_data)
            
            if success:
                logger.info(f"Contact confirmation email queued for {contact.email}")
            else:
                logger.error(f"Failed to queue confirmation email for {contact.email}")
                raise Exception("Kafka producer failed")
                
        except Exception as e:
            logger.warning(f"Kafka unavailable, sending email directly: {str(e)}")
            # Fallback to direct email sending
            try:
                from django.core.mail import EmailMultiAlternatives
                from django.template.loader import render_to_string
                from django.utils.html import strip_tags
                from django.conf import settings
                
                # Prepare email context
                context = {
                    'first_name': contact.first_name,
                    'last_name': contact.last_name,
                    'email': contact.email,
                    'phone': contact.phone,
                    'city': contact.city,
                    'state': contact.state,
                    'subject': contact.subject,
                    'message': contact.message,
                    'created_date': contact.created_date,
                }
                
                # Render email template
                html_content = render_to_string('emails/contact_confirmation.html', context)
                text_content = strip_tags(html_content)
                
                # Create and send email
                email = EmailMultiAlternatives(
                    subject=f"Thank You for Contacting Us - YouTubers Modern",
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[contact.email]
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
                
                logger.info(f"Contact confirmation email sent directly to {contact.email}")
                
            except Exception as email_error:
                logger.error(f"Failed to send confirmation email directly: {str(email_error)}")
                # Don't fail the request if email fails
                pass


# Contact Info Views
class ContactinfoListView(generics.ListAPIView):
    """Get contact information"""
    queryset = Contactinfo.objects.all()
    serializer_class = ContactinfoSerializer
    permission_classes = [AllowAny]


# YouTuber Inquiry Views
class YouTuberInquiryCreateView(generics.CreateAPIView):
    """Create YouTuber inquiry/contact form submission"""
    queryset = YouTuberInquiry.objects.all()
    serializer_class = YouTuberInquirySerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        """Save inquiry and send confirmation email via Kafka or direct email"""
        # Save the inquiry
        inquiry = serializer.save()
        
        # Try Kafka first, fallback to direct email if Kafka is not available
        try:
            from services.kafka_services.producer import get_email_producer
            
            # Prepare inquiry data for email
            inquiry_data = {
                'id': inquiry.id,
                'first_name': inquiry.first_name,
                'last_name': inquiry.last_name,
                'email': inquiry.email,
                'phone': inquiry.phone,
                'company_name': inquiry.company_name,
                'inquiry_type': inquiry.inquiry_type,
                'budget_range': inquiry.budget_range,
                'subject': inquiry.subject,
                'message': inquiry.message,
                'created_date': inquiry.created_at,
            }
            
            # Prepare YouTuber data for email
            youtuber_data = {
                'id': inquiry.youtuber.id,
                'name': inquiry.youtuber.name,
                'category': inquiry.youtuber.category,
            }
            
            # Send email notification via Kafka
            producer = get_email_producer()
            success = producer.send_youtuber_inquiry_email(inquiry_data, youtuber_data)
            
            if success:
                logger.info(f"YouTuber inquiry confirmation email queued for {inquiry.email}")
            else:
                logger.error(f"Failed to queue YouTuber inquiry email for {inquiry.email}")
                raise Exception("Kafka producer failed")
                
        except Exception as e:
            logger.warning(f"Kafka unavailable, sending YouTuber inquiry email directly: {str(e)}")
            # Fallback to direct email sending
            try:
                from django.core.mail import EmailMultiAlternatives
                from django.template.loader import render_to_string
                from django.utils.html import strip_tags
                
                # Prepare email context
                context = {
                    'first_name': inquiry.first_name,
                    'last_name': inquiry.last_name,
                    'email': inquiry.email,
                    'phone': inquiry.phone,
                    'company_name': inquiry.company_name,
                    'inquiry_type': inquiry.inquiry_type,
                    'budget_range': inquiry.budget_range,
                    'subject': inquiry.subject,
                    'message': inquiry.message,
                    'youtuber_name': inquiry.youtuber.name,
                    'youtuber_category': inquiry.youtuber.category,
                    'youtuber_id': inquiry.youtuber.id,
                    'created_date': inquiry.created_at,
                }
                
                # Render email template
                html_content = render_to_string('emails/youtuber_contact_confirmation.html', context)
                text_content = strip_tags(html_content)
                
                # Create and send email
                email = EmailMultiAlternatives(
                    subject=f"Your Inquiry About {inquiry.youtuber.name} - YouTubers Modern",
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[inquiry.email]
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
                
                logger.info(f"YouTuber inquiry confirmation email sent directly to {inquiry.email}")
                
            except Exception as email_error:
                logger.error(f"Failed to send YouTuber inquiry email directly: {str(email_error)}")
                # Don't fail the request if email fails
                pass


# ==================== CREATOR AUTHENTICATION VIEWS ====================

class CreatorRegistrationView(generics.CreateAPIView):
    """Creator registration endpoint"""
    serializer_class = CreatorRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create authentication token
        token, created = Token.objects.get_or_create(user=user)
        
        # Get creator profile
        creator_profile = user.youtuber_profile
        profile_serializer = CreatorProfileSerializer(creator_profile)
        
        return Response({
            'message': 'Creator account created successfully',
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'creator_profile': profile_serializer.data
        }, status=status.HTTP_201_CREATED)


class CreatorLoginView(generics.GenericAPIView):
    """Creator login endpoint"""
    serializer_class = CreatorLoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Create or get authentication token
        token, created = Token.objects.get_or_create(user=user)
        
        # Get creator profile
        creator_profile = user.youtuber_profile
        profile_serializer = CreatorProfileSerializer(creator_profile)
        
        return Response({
            'message': 'Login successful',
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'creator_profile': profile_serializer.data
        }, status=status.HTTP_200_OK)


class CreatorLogoutView(generics.GenericAPIView):
    """Creator logout endpoint"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            # Delete the user's token
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({
                'message': 'Successfully logged out'
            }, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({
                'message': 'You were not logged in'
            }, status=status.HTTP_400_BAD_REQUEST)


# ==================== CREATOR DASHBOARD VIEWS ====================

class CreatorDashboardView(generics.RetrieveAPIView):
    """Creator dashboard overview"""
    permission_classes = [IsAuthenticated]
    serializer_class = CreatorProfileSerializer
    
    def get_object(self):
        try:
            return self.request.user.youtuber_profile
        except Youtubers.DoesNotExist:
            return None
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response({
                'error': 'No YouTuber profile associated with this account'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        
        # Get recent inquiries
        recent_inquiries = instance.inquiries.all()[:5]
        inquiry_serializer = CreatorInquirySerializer(recent_inquiries, many=True)
        
        # Get status counts
        status_counts = {
            'pending': instance.inquiries.filter(status='pending').count(),
            'contacted': instance.inquiries.filter(status='contacted').count(),
            'in_discussion': instance.inquiries.filter(status='in_discussion').count(),
            'accepted': instance.inquiries.filter(status='accepted').count(),
            'declined': instance.inquiries.filter(status='declined').count(),
            'completed': instance.inquiries.filter(status='completed').count(),
        }
        
        return Response({
            'creator_profile': serializer.data,
            'recent_inquiries': inquiry_serializer.data,
            'status_counts': status_counts,
            'dashboard_stats': {
                'total_inquiries': instance.total_inquiries_count,
                'pending_inquiries': instance.pending_inquiries_count,
                'success_rate': round((status_counts['accepted'] / max(instance.total_inquiries_count, 1)) * 100, 1)
            }
        })


class CreatorInquiriesListView(generics.ListAPIView):
    """List all inquiries for the logged-in creator"""
    serializer_class = CreatorInquirySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            creator_profile = self.request.user.youtuber_profile
            queryset = creator_profile.inquiries.all()
            
            # Filter by status if provided
            status_filter = self.request.query_params.get('status', None)
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            # Search functionality
            search = self.request.query_params.get('search', None)
            if search:
                queryset = queryset.filter(
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search) |
                    Q(email__icontains=search) |
                    Q(company_name__icontains=search) |
                    Q(subject__icontains=search) |
                    Q(message__icontains=search)
                )
            
            return queryset.order_by('-created_at')
        except Youtubers.DoesNotExist:
            return YouTuberInquiry.objects.none()


class CreatorInquiryDetailView(generics.RetrieveUpdateAPIView):
    """View and update a specific inquiry"""
    serializer_class = CreatorInquirySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            creator_profile = self.request.user.youtuber_profile
            return creator_profile.inquiries.all()
        except Youtubers.DoesNotExist:
            return YouTuberInquiry.objects.none()
    
    def get_serializer_class(self):
        if self.request.method == 'PATCH' or self.request.method == 'PUT':
            return CreatorInquiryStatusUpdateSerializer
        return CreatorInquirySerializer


class CreatorInquiryStatusUpdateView(generics.UpdateAPIView):
    """Update inquiry status"""
    serializer_class = CreatorInquiryStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            creator_profile = self.request.user.youtuber_profile
            return creator_profile.inquiries.all()
        except Youtubers.DoesNotExist:
            return YouTuberInquiry.objects.none()
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        old_status = instance.status
        self.perform_update(serializer)
        new_status = serializer.instance.status
        
        # Log status change
        logger.info(f"Creator {request.user.username} changed inquiry {instance.id} status from {old_status} to {new_status}")
        
        return Response({
            'message': f'Inquiry status updated to {new_status}',
            'inquiry': CreatorInquirySerializer(serializer.instance).data
        })


# ==================== CREATOR PROFILE VIEWS ====================

class CreatorProfileUpdateView(generics.UpdateAPIView):
    """Update creator profile"""
    serializer_class = CreatorProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        try:
            return self.request.user.youtuber_profile
        except Youtubers.DoesNotExist:
            return None
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response({
                'error': 'No YouTuber profile associated with this account'
            }, status=status.HTTP_404_NOT_FOUND)
        
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'message': 'Profile updated successfully',
            'creator_profile': serializer.data
        })


# Stats and Data Views
@api_view(['GET'])
@permission_classes([AllowAny])
def home_data(request):
    """Get data for home page"""
    sliders = Slider.objects.all().order_by('-created_date')[:5]
    featured_youtubers = Youtubers.objects.filter(is_featured=True)[:6]
    team_members = Team.objects.all().order_by('-created_date')
    
    return Response({
        'sliders': SliderSerializer(sliders, many=True, context={'request': request}).data,
        'featured_youtubers': YoutubersListSerializer(featured_youtubers, many=True, context={'request': request}).data,
        'team_members': TeamSerializer(team_members, many=True, context={'request': request}).data,
        'stats': {
            'total_youtubers': Youtubers.objects.count(),
            'featured_count': Youtubers.objects.filter(is_featured=True).count(),
            'categories': list(Youtubers.objects.values_list('category', flat=True).distinct()),
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def categories(request):
    """Get all available categories"""
    categories = [{'value': choice[0], 'label': choice[1]} for choice in Youtubers.category_choices]
    return Response(categories)


@api_view(['GET'])
@permission_classes([AllowAny])
def crew_types(request):
    """Get all crew types"""
    crew_types = [{'value': choice[0], 'label': choice[1]} for choice in Youtubers.crew_choices]
    return Response(crew_types)


@api_view(['GET'])
@permission_classes([AllowAny])
def camera_types(request):
    """Get all camera types"""
    camera_types = [{'value': choice[0], 'label': choice[1]} for choice in Youtubers.camera_choices]
    return Response(camera_types)
