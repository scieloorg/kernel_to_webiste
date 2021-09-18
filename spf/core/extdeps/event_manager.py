from core.models import Event
from datetime import datetime
from enum import Enum


class EventName(Enum):
    # nomes de eventos associados à busca e ao envio de pacotes
    RETRIEVE_PACKAGE_DATA = "RETRIVE_PACKAGE_DATA"
    UPLOAD_PACKAGE = "UPLOAD_PACKAGE"

    # nomes de eventos associados à validação
    START_VALIDATION = "START_VALIDATION"
    FINALIZE_VALIDATION = "FINALIZE_VALIDATION"

    # nomes de eventos associados à alteração de usuários
    CHANGE_USER_GROUPS = 'CHANGE_USER_GROUPS'


class EventStatus(Enum):
    # estado de um evento
    INITIATED = "INITIATED"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


def register_event(user, name, annotation=None):
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
    event.datetime = datetime.utcnow()
    event.save()

    return event
