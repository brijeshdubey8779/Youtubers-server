from rest_framework import serializers
from django.contrib.auth.models import User
from youtubers.models import Youtubers
from webpages.models import Team, Slider, Contact, YouTuberInquiry
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


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ('created_at',)


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