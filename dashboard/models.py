from django.db import models

# Create your models here.

class GitHubProject(models.Model):
    title = models.CharField(max_length=200, verbose_name='项目标题')
    name = models.CharField(max_length=200, verbose_name='项目名称')
    summary = models.TextField(verbose_name='项目描述')
    is_hot = models.BooleanField(default=False, verbose_name='是否热门')
    is_claimed = models.BooleanField(default=False, verbose_name='是否认领')
    clicks_total = models.IntegerField(default=0, verbose_name='点击总数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = 'GitHub项目'
        verbose_name_plural = verbose_name
        ordering = ['-clicks_total']

    def __str__(self):
        return self.title
