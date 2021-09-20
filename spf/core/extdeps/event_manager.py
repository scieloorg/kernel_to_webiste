from core.models import Event
from datetime import datetime


def register_event(user, name, annotation=None):
    event = Event()
    event.actor = user
    event.annotation = annotation
    event.name = name
    event.status = Event.Status.INITIATED
    event.save()

    return event


def update_event(event, args):
    for k, v in args.items():
        setattr(event, k, v)
    event.datetime = datetime.utcnow()
    event.save()

    return event
