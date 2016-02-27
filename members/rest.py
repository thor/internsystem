import datetime
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import DjangoModelPermissions
from rest_framework import status
from django.db.models import Q
from rest_framework import filters

from members.serializers import *
from members.filters import MemberFilter
from core.models import User
from core.utils import get_semester_of_date

class MemberViewSet(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissions,)
    filter_class = MemberFilter
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name',)
    ordering_fields = ('date_joined', 'name')


    def get_serializer_class(self):
        if self.action in ['create']:
            return AddMemberSerializer
        return MemberSerializer

    def get_queryset(self):
        return Member.objects.filter(Q(semester=get_semester_of_date(datetime.datetime.now())) |
                                     Q(lifetime=True) | Q(honorary=True))

    def create(self, request, **kwargs):
        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        id = request.user
        adder = User.objects.get(username=id)
        semester = get_semester_of_date(datetime.datetime.now())
        lifetime = serializer.data['lifetime']
        try:
            user = User.objects.get(email=serializer.data['email'])
        except:
            user = None
        member = Member(
            seller=adder,
            last_edited_by=adder,
            semester=semester,
            name=serializer.data['name'],
            lifetime=serializer.data['lifetime'],
            email=serializer.data['email'],
            honorary=False,
        )
        if 'uio_username' in serializer.data:
            member.uio_username = serializer.data['uio_username']
        if user is not None:
            member.user = user
        if lifetime:
            member.date_lifetime = timezone.now()

        member.save()

        return Response(MemberSerializer(member).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        member = self.get_object()

        member.name = request.data['name']
        member.email = request.data['email']
        member.last_edited_by = User.objects.get(username=request.user)
        lifetime = (request.data['lifetime'] is 'true')
        if lifetime and not member.lifetime:
            member.date_lifetime = timezone.now()
            member.lifetime = True
        elif (not lifetime) and member.lifetime:
            member.date_lifetime = None
            member.lifetime = False

        if 'honorary' in request.data:
            member.honorary = (request.data['honorary'] is 'true')
        if 'comments' in request.data:
            member.comments = request.data['comments']

        member.save()

        return Response(MemberSerializer(member).data, status=status.HTTP_200_OK)