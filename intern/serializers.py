from rest_framework import serializers

from core.serializers import UserSerializer, CardSerializer, SemesterSerializer, GroupSerializer
from intern.models import AccessLevel, Intern, InternCard, InternRole, Role, Intern, InternLogEntry


class AccessLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessLevel
        fields = (
            'id', 'name', 'uio_name', 'description'
        )


class RoleSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
    access_levels = AccessLevelSerializer(many=True)

    class Meta:
        model = Role
        fields = (
            'id', 'name', 'description', 'groups', 'access_levels'
        )


class InternRoleSerializer(serializers.ModelSerializer):
    role = RoleSerializer()

    class Meta:
        model = InternRole
        fields = (
            'id', 'role', 'date_added'
        )

class InternLogEntrySerializer(serializers.ModelSerializer):
    changed_by = UserSerializer()
    time = serializers.DateTimeField()
    description = serializers.CharField()
    class Meta:
        model = InternLogEntry
        fields = (
            'id', 'changed_by', 'time', 'description'
        )

class InternSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    roles = serializers.SerializerMethodField()
    log = InternLogEntrySerializer(many=True, read_only=True)
    comments = serializers.CharField(max_length=300, allow_blank=True, required=False)
    class Meta:
        model = Intern
        fields = (
            'id', 'user', 'active', 'comments',
            'roles', 'registered', 'left', 'log'
        )
    def update(self, instance, validated_data):
        instance.comments = validated_data.get('comments', instance.comments)
        instance.save()
        return instance

    def get_roles(self, obj):
        roles = InternRole.objects.filter(intern=obj, date_removed__isnull=True)
        serializer = InternRoleSerializer(instance=roles, many=True)
        return serializer.data

class SimpleInternSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Intern
        fields = (
            'id', 'user', 'comments'
        )


class InternRoleFullSerializer(InternRoleSerializer):
    role = RoleSerializer(read_only=True)
    intern = SimpleInternSerializer(read_only=True)
    semesters = SemesterSerializer(many=True)
    created_by = UserSerializer(read_only=True)
    last_editor = UserSerializer(read_only=True)
    removed_by = UserSerializer(read_only=True)
    date_added = serializers.DateField(read_only=True)
    date_edited = serializers.DateField(read_only=True)
    date_removed = serializers.DateField(read_only=True)
    access_given = serializers.BooleanField()
    date_access_given = serializers.DateTimeField(read_only=True)
    date_access_revoked = serializers.DateTimeField(read_only=True)

    class Meta:
        model = InternRole
        fields = (
            'id', 'intern', 'role', 'semesters', 'access_given', 'date_access_given', 'date_access_revoked',
            'date_added', 'date_removed', 'date_edited', 'comments', 'created_by', 'last_editor',
            'removed_by', 'recieved_interncard',
        )


class AddInternRoleSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=15)

    class Meta:
        model = InternRole
        fields = (
            'username', 'role'
        )


class InternCardSerializer(serializers.ModelSerializer):
    intern = InternSerializer()
    internroles = InternRoleSerializer(many=True)
    semester = SemesterSerializer()

    class Meta:
        model = InternCard
        fields = ('intern', 'internroles', 'semester', 'date_made', 'made_by')


class AddInternCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternCard
        fields = ('intern', 'internroles')
