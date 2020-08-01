from users.models import *
from graphene_django.types import DjangoObjectType
import graphene
from graphene import relay


class UserType(DjangoObjectType):
    class Meta:
        model = CustomUser


class NotificationType(DjangoObjectType):
    class Meta:
        model = UserNotification
        interfaces = (relay.Node,)


class NotificationConnection(relay.Connection):
    class Meta:
        node = NotificationType


class ScheduleType(DjangoObjectType):
    class Meta:
        model = Schedule

    next_event = graphene.DateTime()

    def resolve_next_event(self, info):
        return Schedule.next(self)


class PickUpType(DjangoObjectType):
    class Meta:
        model = PickUpInfo


class Query(object):
    schedules = graphene.List(ScheduleType)
    notifications = relay.ConnectionField(NotificationConnection)
    pick_up_info = graphene.List(PickUpType)


class CreateSchedule(graphene.Mutation):
    """Create a schedule for the pick up"""
    success = graphene.Boolean()

    class Arguments:
        start = graphene.DateTime(required=True)
        end = graphene.DateTime(required=False, default_value=None)
        repeat = graphene.String(required=False, default_value='')
        repeat_until = graphene.Date(required=False, default_value=None)
        customer_id = graphene.ID(required=True)
        event_id = graphene.ID(required=True)  # id of pickup
    schedule = graphene.Field(ScheduleType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        customer_instance = CustomUser.objects.get(id=kwargs['customer_id'])
        pickup_instance = PickUpInfo.objects.get(id=kwargs['event_id'])
        end = kwargs.get('end', None)
        get_repeat = kwargs.get('repeat', None)
        repeat = 'RRULE:FREQ=%s' % get_repeat if get_repeat else ""
        repeat_until = kwargs.get('repeat_until', None)
        schedule = Schedule(start=kwargs['start'], end=end, customer_id=customer_instance,
                            event=pickup_instance, repeat=repeat, repeat_until=repeat_until)
        schedule.save()
        return cls(success=True, schedule=schedule)


class CreatePickUp(graphene.Mutation):
    """Create a pick up information"""
    success = graphene.Boolean()  # success message

    class Arguments:
        bin_type = graphene.String(required=True)
        lbs = graphene.Float(required=True)
        instructions = graphene.String(required=False, default_value=None)

    # The class attributes define the response of the mutation
    pick_up = graphene.Field(PickUpType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        instructions = kwargs.get('instructions', '')
        pick_up = PickUpInfo(
            bin_type=kwargs['bin_type'],
            lbs=kwargs['lbs'],
            instructions=instructions)
        pick_up.save()
        return cls(success=True, pick_up=pick_up)


class DeleteNotification(graphene.Mutation):
    """ Delete the notification of a user"""
    success = graphene.Boolean()

    class Arguments:
        id = graphene.UUID(required=True)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        obj = UserNotification.objects.get(id=kwargs['id'])
        obj.delete()
        return cls(success=True)


class SeenNotification(graphene.Mutation):
    """ Set notification to seen """
    success = graphene.Boolean()

    class Arguments:
        id = graphene.UUID(required=True)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        obj = UserNotification.objects.get(id=kwargs['id'])
        setattr(obj, 'seen', True)
        return cls(success=True)


class Mutation(object):
    delete_notification = DeleteNotification.Field()
    create_pickup = CreatePickUp.Field()
    create_schedule = CreateSchedule.Field()
