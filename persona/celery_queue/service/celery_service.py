from celery import Celery
from celery.utils.log import get_task_logger

celeryApp = Celery('persona',
                broker="amqp://stephenbaione:zThG$a$&75f720@localhost/stephen_vhost",
                backend="mongodb://127.0.0.1:27017",
                task_track_started=True,
                include=[
                    "persona.core.tasks",
                    "persona.external_services.spotify.internal.tasks"
                    ])

# logger = get_task_logger()
