from rest_framework import serializers

from django.contrib.auth.models import User
from registrations.models import GroupLeader, TeamCaptain, Participant
from events.models import Event, Participation

class GroupLeaderSerializer(serializers.ModelSerializer):

	class Meta:
		model = GroupLeader
		fields = ('name', 'gender', 'college', 'city', 'state', 'email', 'phone')

class UserSerializer(serializers.ModelSerializer):

	profile = GroupLeaderSerializer(required=True, write_only=True)
	password = serializers.CharField()

	class Meta:
		model = User
		fields = ('username', 'email', 'password', 'profile')

	def create(self, validated_data):

		###print 'Validated data : ', validated_data
		profile_data = validated_data.pop("profile")
		user = User.objects.create_user(**validated_data)
		GroupLeader.objects.create(user=user, **profile_data)
		return user

class EventSerializer(serializers.ModelSerializer):

	class Meta:
		model = Event
		fields = ('id', 'name', 'min_limit', 'max_limit', 'start_date' ,'end_date','venue', 'about')

class TeamCaptainSerializer(serializers.ModelSerializer):

	g_l = GroupLeaderSerializer(required=True, write_only=True)
	event = EventSerializer(required=True, write_only=True)

	class Meta:
		model = TeamCaptain
		fields = ('name', 'email', 'phone', 'event', 'g_l', 'gender', 'total_players')

class ParticipantSerializer(serializers.ModelSerializer):

	captain = TeamCaptainSerializer(required=True, write_only=True)

	class Meta:
		model = Participant
		fields = ('name', 'captain')

class ParticipationSerializer(serializers.ModelSerializer):

	g_l = GroupLeaderSerializer(required=True, write_only=True)
	event = EventSerializer(required=True, write_only=True)

	class Meta:
		model = Participation
		fields = '__all__'