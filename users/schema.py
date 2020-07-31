from users.models import  CustomUser
from graphene_django.types import DjangoObjectType
import graphene


class Users(DjangoObjectType):
    class Meta:
        model = CustomUser


class Query(object):
    all_users = graphene.List(Users)

    def resolve_all_users(self, info, **kwargs):
        return CustomUser.objects.all()
