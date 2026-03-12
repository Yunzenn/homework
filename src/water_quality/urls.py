"""
URL configuration for water_quality project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def home_view(request):
    """首页视图，提供API导航"""
    return HttpResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>水质监控系统 - API</title>
            <meta charset="utf-8">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #1890ff;
                    text-align: center;
                }
                .api-list {
                    list-style: none;
                    padding: 0;
                }
                .api-list li {
                    margin: 10px 0;
                    padding: 15px;
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    background: #fafafa;
                }
                .api-list a {
                    color: #1890ff;
                    text-decoration: none;
                    font-weight: bold;
                }
                .api-list a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌊 水质监控系统 API</h1>
                <p>欢迎使用水质监控系统API服务！</p>
                
                <h3>📡 可用的API端点：</h3>
                <ul class="api-list">
                    <li><a href="/api/records/">📊 水质记录 API</a></li>
                    <li><a href="/api/users/">👥 用户管理 API</a></li>
                    <li><a href="/admin/">⚙️ 管理后台</a></li>
                </ul>
                
                <h3>🌐 前端应用：</h3>
                <ul class="api-list">
                    <li><a href="http://localhost:5173/enhanced-login" target="_blank">🎭 动画登录页面</a></li>
                    <li><a href="http://localhost:5173/register" target="_blank">📝 用户注册页面</a></li>
                </ul>
                
                <p style="text-align: center; margin-top: 30px; color: #666;">
                    <small>💡 提示：API使用JWT认证，请先登录获取访问令牌</small>
                </p>
            </div>
        </body>
        </html>
    """)


urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include([
        path('', include('api.urls')),
        path('', include('users.urls')),
    ])),
]

# 开发环境下提供媒体文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
