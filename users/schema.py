from users.models import *
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
import graphene
from graphene import relay


class AddressType(DjangoObjectType):
    class Meta:
        model = Address


class NotificationType(DjangoObjectType):
    class Meta:
        model = UserNotification
        interfaces = (relay.Node,)


class ScheduleType(DjangoObjectType):
    class Meta:
        model = Schedule
        interfaces = (relay.Node,)

    next_event = graphene.DateTime()

    def resolve_next_event(self, info):
        return Schedule.next(self)


class PickUpType(DjangoObjectType):
    class Meta:
        model = PickUpInfo
        interfaces = (relay.Node,)


class Query(object):
    schedules = graphene.List(ScheduleType)
    notifications = graphene.List(NotificationType)
    pick_up_info = graphene.List(PickUpType)
    address = graphene.List(AddressType)


class PickUpInput(graphene.InputObjectType):
    bin_type = graphene.String()
    lbs = graphene.Float()
    instructions = graphene.String()


class EventInput(graphene.InputObjectType):
    info = graphene.Field(PickUpInput)


class ScheduleInput(graphene.InputObjectType):
    start = graphene.DateTime()
    end = graphene.DateTime()
    repeat = graphene.String()
    repeat_until = graphene.Date()
    event = graphene.Field(EventInput)


class CreateSchedule(graphene.Mutation):
    """Create a schedule for the pick up"""
    class Arguments:
        schedule_data = ScheduleInput(required=True)
    schedule = graphene.Field(ScheduleType)
    success = graphene.Boolean()

    def mutate(root, info, schedule_data=None):
        schedule_data.event.info['user'] = CustomUser.objects.get(pk=info.context.user.id)
        pickup_info = PickUpInfo.objects.create(**schedule_data.event.info)
        schedule = Schedule(
            start=schedule_data.start,
            end=schedule_data.end,
            repeat=schedule_data.repeat,
            repeat_until=schedule_data.repeat_until,
            user=CustomUser.objects.get(pk=info.context.user.id),
            event=Event.objects.create(info=pickup_info)
        )
        schedule.save()
        return CreateSchedule(schedule=schedule, success=True)


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
            user=CustomUser.objects.get(pk=info.context.user.id),
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
