import os

from celery.result import AsyncResult
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .tasks import transcribe
from .utils import handle_incoming_file_chunk, handle_last_file_chunk


@csrf_exempt
def index(request):
    if request.method == 'POST':
        file = request.FILES['file']
        is_last_chunk = request.POST['is_last']
        filename = request.POST['filename']

        temporary_path = handle_incoming_file_chunk(file)

        if is_last_chunk == 'true':
            final_path = handle_last_file_chunk(temporary_path, filename)

            # Add Celery Task to Queue
            task = transcribe.delay(final_path)
            return JsonResponse({'taskID': task.id})

        return JsonResponse({'status': 'received'})


def results(request, task_id):
    try:
        res = AsyncResult(task_id)
    except Exception as e:
        return JsonResponse({'status': str(e)})

    if res.state == 'SUCCESS':
        return JsonResponse(
            {'transcription_url': res.get(), 'status': 'SUCCESS'}
        )
    if res.state in ('FAILURE', 'REVOKED'):
        return JsonResponse({'status': 'FAILURE'})
    return JsonResponse({'status': res.state})
