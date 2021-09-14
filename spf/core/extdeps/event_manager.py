from core.models import Event
from datetime import datetime
from enum import Enum


class EventName(Enum):
    # nomes de eventos associados à busca e ao envio de pacotes
    RETRIEVE_PACKAGE_DATA = "RETRIVE_PACKAGE_DATA"
    UPLOAD_PACKAGE = "UPLOAD_PACKAGE"

    # nomes de eventos associados a validação
    START_VALIDATION = "START_VALIDATION"
    FINALIZE_VALIDATION = "FINALIZE_VALIDATION"


class EventStatus(Enum):
    # estado de um evento
    INITIATED = "INITIATED"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


def register_event(user, name, annotation):
    event = Event()
    event.actor = user
    event.annotation = annotation
    event.name = name
    event.status = EventStatus.INITIATED
    event.save()

    return event


def update_event(event, args):
    for k, v in args.items():
        setattr(event, k, v)
    event.datetime = datetime.now()
    event.save()

    return event
