from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.generic import TemplateView
import requests
import ast
from .models import GitHubProject

def fetch_github_data(request):
    """从HelloGitHub API获取数据并存储到数据库"""
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Authorization': 'Bearer null',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://hellogithub.com',
        'Referer': 'https://hellogithub.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    params = {
        'sort_by': 'featured',
        'page': '1',
        'rank_by': 'newest',
        'tid': 'all',
    }

    try:
        response = requests.get('https://api.hellogithub.com/v1/', params=params, headers=headers)
        json_data = response.json()

        for item in json_data['data']:
            if isinstance(item, str):
                data_dict = ast.literal_eval(item)
            else:
                data_dict = item

            # 更新或创建项目记录
            GitHubProject.objects.update_or_create(
                name=data_dict.get('name', ''),
                defaults={
                    'title': data_dict.get('title', ''),
                    'summary': data_dict.get('summary', ''),
                    'is_hot': data_dict.get('is_hot', False),
                    'is_claimed': data_dict.get('is_claimed', False),
                    'clicks_total': data_dict.get('clicks_total', 0),
                }
            )

        return JsonResponse({'status': 'success', 'message': '数据更新成功'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

class DashboardView(TemplateView):
    """仪表板主视图"""
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context 包含所有GitHub项目数据
        projects = GitHubProject.objects.all()
        context['projects'] = projects
        context['total_projects'] = projects.count()
        context['hot_projects'] = projects.filter(is_hot=True).count()
        context['claimed_projects'] = projects.filter(is_claimed=True).count()
        return context
