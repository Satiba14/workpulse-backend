from rest_framework import serializers
from apps.workforce.models import User

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'role',
            'full_name',
            'phone',
            'designation',
            'profile_image',
            'created_at',
            'last_login',
        ]

    def get_profile_image(self, obj):
        request = self.context.get('request')

        if obj.profile_image:
            if request:
                return request.build_absolute_uri(
                    obj.profile_image.url
                )
            return obj.profile_image.url

        return None

    def update(self, instance, validated_data):
        instance.full_name = validated_data.get(
            'full_name',
            instance.full_name
        )

        instance.phone = validated_data.get(
            'phone',
            instance.phone
        )

        instance.designation = validated_data.get(
            'designation',
            instance.designation
        )

        if 'profile_image' in validated_data:
            instance.profile_image = validated_data['profile_image']

        instance.save()

        return instance