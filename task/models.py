from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver



import datetime

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from allauth.socialaccount.models import SocialToken, SocialApp


# instead of start_date there should have been due_date property name.
class Task(models.Model):
    user = models.ForeignKey(User, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    start_date = models.DateTimeField(blank=True, null=True)
    task_id = models.CharField(max_length=225, blank=True, null=True)
    tasklist_id = models.CharField(max_length=225, blank=True, null=True)

    def __str__(self):
        return self.title



# google api create, update and delete task

def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt


@receiver(post_save, sender=Task)
def create_task(sender, **kwargs):

    # request is the HttpRequest object
    token = SocialToken.objects.get(account__user=kwargs['instance'].user, account__provider='google')

    social_app = SocialApp.objects.get(id=token.app.id)

    credentials = Credentials(
        token=token.token,
        refresh_token=token.token_secret,
        token_uri='https://oauth2.googleapis.com/token',
        client_id = social_app.client_id,
        client_secret = social_app.secret)

    service = build('tasks', 'v1', credentials=credentials)

    # Normal date format was not accepting to had to go throught this proces
    # api may give error if we create task from admin because admin take date time as text only.
    due_date = datetime.datetime.strptime(kwargs['instance'].start_date, "%Y-%m-%dT%H:%M")
    # due_date = kwargs['instance'].start_date
    task = {
        "kind": "tasks#task",
        "title": kwargs['instance'].title,
        "updated": str(kwargs['instance'].created_at),
        "notes": kwargs['instance'].text,
        "status": "needsAction",
        "due": convert_to_RFC_datetime(due_date.year, due_date.month, due_date.day)
        }
    # Next three lines just to get tasklist id
    results = service.tasklists().list(maxResults=10).execute()
    items = results.get('items', [])
    tasklist_id = items[0]['id']

    if kwargs['instance'].task_id != None:
        id = kwargs['instance'].task_id
        task["id"] = id
        print('will be updating')
        task = service.tasks().update(tasklist=tasklist_id, task=id, body=task).execute()
        print('task updated')
    else:
        task = service.tasks().insert(tasklist=tasklist_id, body=task).execute()
        Task.objects.filter(id=kwargs['instance'].id).update(task_id=task['id'])
        Task.objects.filter(id=kwargs['instance'].id).update(tasklist_id=tasklist_id)
    print(kwargs['instance'].id)



@receiver(pre_delete, sender=Task)
def delete_task(sender, **kwargs):

        # request is the HttpRequest object
    token = SocialToken.objects.get(account__user=kwargs['instance'].user, account__provider='google')

    social_app = SocialApp.objects.get(id=token.app.id)

    credentials = Credentials(
        token=token.token,
        refresh_token=token.token_secret,
        token_uri='https://oauth2.googleapis.com/token',
        client_id = social_app.client_id,
        client_secret = social_app.secret)

    service = build('tasks', 'v1', credentials=credentials)

    service.tasks().delete(tasklist=kwargs['instance'].tasklist_id,task=kwargs['instance'].task_id).execute()
    print('task deleted')





