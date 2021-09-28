from celery import shared_task, current_task

import dsm.ingress as dsm_ingress


@shared_task
def task_get_package_uri_by_pid(pid):
    result = dsm_ingress.get_package_uri_by_pid(pid)

    current_task.update_state(
        state='PROGRESS',
        meta={
            'status': 'LOADING...',
        })

    return result



