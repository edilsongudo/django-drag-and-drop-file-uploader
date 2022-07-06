import os

from celery.result import AsyncResult
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .tasks import transcribe
from .utils import (
    generate_aws_s3_object_url,
    generate_presigned_url,
    handle_incoming_file_chunk,
    handle_last_file_chunk,
)


@csrf_exempt
def upload(request):
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
        print(res.traceback)
        return JsonResponse({'status': 'FAILURE'})
    return JsonResponse({'status': res.state})


def pressigned_url(request, key):
    url = generate_presigned_url(key)
    return JsonResponse({'url': url})


def task_start(request, key, filename):
    url = generate_aws_s3_object_url(key)
    task = transcribe.delay(url, filename)
    return JsonResponse({'taskID': task.id})
