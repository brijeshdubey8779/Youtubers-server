from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from youtubers.models import Youtubers
from webpages.models import YouTuberInquiry, Team, Slider
from contactinfo.models import Contactinfo
from contactpage.models import Contactpage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('id', 'date_joined')


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class YoutubersListSerializer(serializers.ModelSerializer):
    """Serializer for listing YouTubers with basic information"""
    
    class Meta:
        model = Youtubers
        fields = [
            'id', 'name', 'photo', 'category', 'subs_count', 
            'city', 'age', 'price', 'is_featured'
        ]


class YoutubersSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual YouTuber"""
    
    class Meta:
        model = Youtubers
        fields = '__all__'


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ('created_date',)


class SliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slider
        fields = '__all__'
        read_only_fields = ('created_date',)


class ContactinfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contactinfo
        fields = '__all__'
        read_only_fields = ('created_date',)


class ContactpageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contactpage
        fields = '__all__'
        read_only_fields = ('created_date',)


class YouTuberInquirySerializer(serializers.ModelSerializer):
    youtuber_name = serializers.CharField(source='youtuber.name', read_only=True)
    youtuber_category = serializers.CharField(source='youtuber.category', read_only=True)
    
    class Meta:
        model = YouTuberInquiry
        fields = [
            'id', 'youtuber', 'youtuber_name', 'youtuber_category',
            'first_name', 'last_name', 'email', 'phone', 'company_name', 'website',
            'inquiry_type', 'budget_range', 'project_timeline', 'subject', 'message',
            'target_audience', 'deliverables', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'status', 'youtuber_name', 'youtuber_category')
    
    def validate_youtuber(self, value):
        """Ensure the YouTuber exists and is active"""
        if not value:
            raise serializers.ValidationError("YouTuber is required")
        # Add any additional validation if needed
        return value


# ==================== CREATOR AUTHENTICATION SERIALIZERS ====================

class CreatorRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for creator registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    youtuber_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm', 'youtuber_id']
    
    def validate(self, attrs):
        """Validate registration data"""
        # Check password confirmation
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        
        # Check if YouTuber exists and doesn't already have an account
        try:
            youtuber = Youtubers.objects.get(id=attrs['youtuber_id'])
            if youtuber.user:
                raise serializers.ValidationError("This YouTuber profile already has a creator account")
        except Youtubers.DoesNotExist:
            raise serializers.ValidationError("YouTuber profile not found")
        
        # Check if email matches YouTuber's creator_email (if set)
        if youtuber.creator_email and youtuber.creator_email != attrs['email']:
            raise serializers.ValidationError("Email must match the YouTuber profile's registered email")
        
        return attrs
    
    def create(self, validated_data):
        """Create user and link to YouTuber profile"""
        youtuber_id = validated_data.pop('youtuber_id')
        validated_data.pop('password_confirm')
        
        # Create User
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        
        # Link to YouTuber profile
        youtuber = Youtubers.objects.get(id=youtuber_id)
        youtuber.user = user
        youtuber.creator_email = validated_data['email']
        youtuber.creator_username = validated_data['username']
        youtuber.is_creator_verified = True  # Auto-verify for now
        youtuber.save()
        
        return user


class CreatorLoginSerializer(serializers.Serializer):
    """Serializer for creator login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate login credentials"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            # Try to authenticate
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError("Invalid username or password")
            
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
            
            # Check if user has a YouTuber profile
            try:
                youtuber = user.youtuber_profile
                if not youtuber.can_manage_inquiries:
                    raise serializers.ValidationError("You don't have permission to access the creator dashboard")
            except Youtubers.DoesNotExist:
                raise serializers.ValidationError("No YouTuber profile associated with this account")
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError("Must include username and password")


class CreatorProfileSerializer(serializers.ModelSerializer):
    """Serializer for creator profile information"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    pending_inquiries = serializers.IntegerField(source='pending_inquiries_count', read_only=True)
    total_inquiries = serializers.IntegerField(source='total_inquiries_count', read_only=True)
    
    class Meta:
        model = Youtubers
        fields = [
            'id', 'name', 'category', 'city', 'subs_count', 'is_featured',
            'user_username', 'user_email', 'user_first_name', 'user_last_name',
            'creator_email', 'creator_username', 'is_creator_verified', 'can_manage_inquiries',
            'pending_inquiries', 'total_inquiries', 'created_date'
        ]
        read_only_fields = ['id', 'user_username', 'user_email', 'created_date']


class CreatorInquirySerializer(serializers.ModelSerializer):
    """Serializer for creator viewing and managing inquiries"""
    
    class Meta:
        model = YouTuberInquiry
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'company_name', 'website',
            'inquiry_type', 'budget_range', 'project_timeline', 'subject', 'message',
            'target_audience', 'deliverables', 'status', 'created_at', 'updated_at', 'admin_notes'
        ]
        read_only_fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'company_name', 
                           'website', 'inquiry_type', 'budget_range', 'project_timeline', 
                           'subject', 'message', 'target_audience', 'deliverables', 'created_at']


class CreatorInquiryStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating inquiry status by creators"""
    
    class Meta:
        model = YouTuberInquiry
        fields = ['status', 'admin_notes']
    
    def validate_status(self, value):
        """Validate that creators can only set certain statuses"""
        allowed_statuses = ['contacted', 'in_discussion', 'accepted', 'declined']
        if value not in allowed_statuses:
            raise serializers.ValidationError(f"Creators can only set status to: {', '.join(allowed_statuses)}")
        return value 