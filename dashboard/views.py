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
                data_dict = item            # 更新或创建项目记录
            GitHubProject.objects.update_or_create(
                name=data_dict.get('name', ''),
                defaults={
                    'title': data_dict.get('title', ''),
                    'summary': data_dict.get('summary', ''),
                    'is_hot': data_dict.get('is_hot', False),
                    'is_claimed': data_dict.get('is_claimed', False),
                    'clicks_total': data_dict.get('clicks_total', 0),
                    'item_id': data_dict.get('item_id', ''),
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
        top3_projects = GitHubProject.objects.order_by('-clicks_total')[:3]
        
        # 处理前三名项目的评论，将评论字符串分割成列表
        top3_with_comments = []
        for project in top3_projects:
            project_data = {
                'title': project.title,
                'clicks_total': project.clicks_total,
                'summary': project.summary,
                'item_id': project.item_id,
                'comments_list': []
            }
            
            if project.comments and project.comments != '暂无评论':
                # 如果评论包含错误信息，直接显示
                if '获取评论失败' in project.comments or 'API返回错误' in project.comments:
                    project_data['comments_list'] = [project.comments]
                else:
                    # 按 | 分割评论
                    project_data['comments_list'] = [comment.strip() for comment in project.comments.split(' | ') if comment.strip()]
            
            if not project_data['comments_list']:
                project_data['comments_list'] = ['暂无评论']
                
            top3_with_comments.append(project_data)
        
        context['projects'] = projects
        context['top3_projects'] = top3_projects
        context['top3_with_comments'] = top3_with_comments
        context['total_projects'] = projects.count()
        context['hot_projects'] = projects.filter(is_hot=True).count()
        context['claimed_projects'] = projects.filter(is_claimed=True).count()
        return context

def fetch_top3_comments(request):
    """获取前三名点击量项目的评论"""
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Authorization': 'Bearer null',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://hellogithub.com',
        'Referer': 'https://hellogithub.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'page': '1',
        'sort_by': 'last',
    }

    try:
        # 获取前三名点击量最高的项目
        top_projects = GitHubProject.objects.order_by('-clicks_total')[:3]
        updated_count = 0
        
        for project in top_projects:
            if not project.item_id:
                continue
                
            try:
                # 获取项目评论
                response = requests.get(
                    f'https://api.hellogithub.com/v1/comment/repository/{project.item_id}',
                    params=params,
                    headers=headers,
                )
                
                if response.status_code == 200:
                    json_data = response.json()
                    comments_list = []
                    
                    # 提取评论信息
                    if 'data' in json_data and json_data['data']:
                        for item in json_data['data']:
                            if isinstance(item, str):
                                try:
                                    data_dict = ast.literal_eval(item)
                                    if 'comment' in data_dict:
                                        comments_list.append(data_dict['comment'])
                                except:
                                    pass
                            else:
                                if 'comment' in item:
                                    comments_list.append(item['comment'])
                    
                    # 将评论列表转换为字符串并保存
                    comments_text = ' | '.join(comments_list) if comments_list else '暂无评论'
                    project.comments = comments_text
                    project.save()
                    updated_count += 1
                    
                else:
                    project.comments = f'API返回错误状态码: {response.status_code}'
                    project.save()
                    
            except Exception as e:
                project.comments = f'获取评论失败: {str(e)}'
                project.save()
        
        return JsonResponse({
            'status': 'success', 
            'message': f'成功更新了 {updated_count} 个项目的评论信息',
            'updated_count': updated_count
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
