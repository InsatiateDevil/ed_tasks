from django.db import models, transaction


class TaskQueue(models.Model):
    task_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='pending')  # Статус задачи
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.task_name


def fetch_task():
    with transaction.atomic():
        task = TaskQueue.objects.select_for_update().filter(status='pending').first()
        if not task:
            return None
        task.status = 'in_progress'
        task.save()
        return task


@transaction.atomic
def fetch_task_alt():
    task = TaskQueue.objects.select_for_update().filter(status='pending').first()
    if not task:
        return None
    task.status = 'in_progress'
    task.save()
    return task
