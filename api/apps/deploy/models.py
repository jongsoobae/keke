from django.db import models


class Deployment(models.Model):
    class Status(models.TextChoices):
        WAIT = 0
        NOTIFIED = 1
        SUCCESS = 2
        FAIL = 3

    repo = models.CharField(verbose_name="git repo", max_length=64)
    title = models.CharField(verbose_name="배포 이름", max_length=64)
    release_branch = models.CharField(verbose_name="release 브랜치", max_length=32)
    base_branch = models.CharField(verbose_name="배포 대상 브랜치", default="main", max_length=32)
    status = models.CharField(verbose_name="배포 상태", choices=Status.choices, default=Status.WAIT, max_length=16)
    release_sha = models.CharField(verbose_name="release sha", max_length=32)
    base_sha = models.CharField(verbose_name="배포 대상 sha", max_length=32)
    sha = models.CharField(verbose_name="PR sha", max_length=32)


class DeploymentItem(models.Model):
    deployment = models.ForeignKey(to="Deployment", on_delete=models.CASCADE)

    key = models.CharField(verbose_name="JIRA Key", max_length=16)
    url = models.CharField(verbose_name="JIRA Ticket Url")
    summary = models.CharField(verbose_name="Summary")
