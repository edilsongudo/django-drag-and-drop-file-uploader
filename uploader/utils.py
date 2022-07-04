import os
from django.conf import settings
import uuid


def handle_incoming_file_chunk(file):
    file_id = file.name
    temporary_path = os.path.join(settings.MEDIA_ROOT, file_id)
    with open(temporary_path, 'ab') as f:
        f.write(file.read())
    return temporary_path


def handle_last_file_chunk(temporary_path, filename):
    final_filename = filename
    final_path = os.path.join(settings.MEDIA_ROOT, final_filename)
    if os.path.exists(final_path):
        final_filename = (
            os.path.splitext(filename)[0]
            + ' - '
            + uuid.uuid4().hex[0:3]
            + os.path.splitext(filename)[1]
        )
        final_path = os.path.join(settings.MEDIA_ROOT, final_filename)
    os.rename(temporary_path, final_path)
    return final_path


def milliseconds_to_hours(millis):
    millis = int(millis)
    seconds = (millis / 1000) % 60
    seconds = int(seconds)
    minutes = millis / (1000 * 60)
    minutes = int(minutes)
    return f'{minutes}:{seconds}'
