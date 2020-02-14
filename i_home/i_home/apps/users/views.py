import json
import re
from django import http
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.db import DatabaseError
from django.views import View
from django_redis import get_redis_connection
from fdfs_client.client import Fdfs_client
from i_home.libs.response_code import RET
from i_home.settings.dev import BASE_DIR
from i_home.utils.fastdfs.fastdfs_storage import FastDFSStorage
from users.models import User


# class MobileCountView(View):
#
#     def get(self, request, mobile):
#         '''
#         判断电话是否重复, 返回对应的个数
#         :param request:
#         :param mobile:
#         :return:
#         '''
#         # 1.从数据库中查询 mobile 对应的个数
#         count = User.objects.filter(mobile=mobile).count()
#
#         # 2.拼接参数, 返回
#         return http.JsonResponse({'code':0,
#                                   'errmsg':'ok',
#                                   'count':count})

class RegisterView(View):

    def post(self, request):
        # 1.接收参数(json类型的参数)
        dict = json.loads(request.body.decode())
        mobile = dict.get('mobile')
        sms_code_client = dict.get('phonecode')
        password = dict.get('password')
        password2 = dict.get('password2')

        # 2.校验参数(总体 + 单个)
        # 2.1总体检验,查看是否有为空的参数:
        if not all([password, password2, mobile, sms_code_client]):
            return http.HttpResponseForbidden('缺少必传参数')

        # 单个检验,查看是否能够正确匹配正则
        if not re.match(r'^1[345789]\d{9}$', mobile):
            return http.HttpResponseForbidden('手机号格式不正确')

        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('密码为8-20位的字符串')

        if password != password2:
            return http.HttpResponseForbidden('密码不一致')

        # 链接 redis, 获取链接对象
        redis_conn = get_redis_connection('verify_code')

        # 从 redis 取保存的短信验证码
        sms_code_server = redis_conn.get('sms_%s' % mobile)

        if sms_code_server is None:
            return http.HttpResponse(status=400)

        # 对比
        if sms_code_client != sms_code_server.decode():
            return http.HttpResponse(status=400)

        # 3.往 mysql 保存数据
        # 对数据库进行操作, 需要 try... except...
        try:
            user = User.objects.create_user(username=mobile,password=password,mobile=mobile)

        except DatabaseError:
            # 如果出错, 返回400
            return http.HttpResponse(status=400)

        # 实现状态保持
        login(request, user)

        # 返回响应结果
        response = http.JsonResponse({'errno': RET.OK, 'errmsg': "注册成功"})

        # 在响应对象中设置用户名信息.
        # 将用户名写入到 cookie，有效期 14 天
        response.set_cookie('username',
                            user.username,
                            max_age=3600 * 24 * 14)

        # 返回响应结果
        return response

class LoginView(View):

    def post(self, request):
        '''实现登录接口'''
        # 1.接收参数
        dict = json.loads(request.body.decode())
        mobile = dict.get('mobile')
        password = dict.get('password')

        # 2.校验(整体 + 单个)
        if not all([mobile, password]):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '缺少必传参数'})

        # 3.验证是否能够登录
        user = authenticate(username=mobile,
                            password=password)
        # # 判断是否为空,如果为空,返回
        if user is None:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '用户名或者密码错误'})

        # 4.状态保持
        login(request, user)

        # 5.判断是否记住用户
        # if remembered != True:
            # 7.如果没有记住: 关闭立刻失效
        #     request.session.set_expiry(0)
        # else:
        #     # 6.如果记住:  设置为两周有效
        #     request.session.set_expiry(None)

        # 8.返回json
        response = http.JsonResponse({'errno': RET.OK,'errmsg': "登录成功"})

        # 在响应对象中设置用户名信息.
        # 将用户名写入到 cookie，有效期 14 天
        response.set_cookie('username',
                            user.username,
                            max_age=3600 * 24 * 14)

        # 返回响应结果
        return response

class GetSessionView(View):
    """获取登录状态"""
    def get(self, request):
        user_id = request.user.id
        name = request.user.username
        if not all([user_id,name]):
            return http.JsonResponse({"errno": "4101", "errmsg": "未登录"})
        return http.JsonResponse({"errno": "0", "errmsg": "OK", "data": {"user_id": user_id, "name": name}})

class LogoutView(View):
    """定义退出登录的接口"""

    def delete(self, request):
        """实现退出登录逻辑"""

        # 清理 session
        logout(request)

        # 创建 response 对象.
        response = http.JsonResponse({'errno': RET.OK, 'errmsg': "用户已退出"})

        # 调用对象的 delete_cookie 方法, 清除cookie
        response.delete_cookie('username')

        # 返回响应
        return response

class UserInfoView(View):
    """用户中心"""

    def get(self, request):
        """提供个人信息界面"""

        # 获取界面需要的数据,进行拼接
        username = request.user.username
        mobile = request.user.mobile

        # 返回响应
        return http.JsonResponse({ "errno": "0",
                                   "errmsg": "OK",
                                   "data": {"name": username,
                                            "avatar_url": request.user.avatar_url,
                                            "mobile": mobile } })

    def post(self, request):
        dict = json.loads(request.body.decode())
        newname = dict.get('name')
        try:
            request.user.username = newname
            request.user.save()
        except Exception as e:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '数据库保存失败'})

        return http.JsonResponse({'errno': RET.OK, 'errmsg': "OK"})

class UserPortraitView(View):
    """上传头像"""
    def post(self, request):
        # 1. 获取到上传的文件
        content = request.FILES.get('avatar')
        if content is None:
            return http.JsonResponse({'errno': RET.PARAMERR, 'errmsg': "参数错误"})

        # 2. 再将文件上传到FastDFs
        # 创建客户端对象
        # 调用上传函数
        try:
            client = Fdfs_client(settings.FDFS_CLIENT_CONF)
            result = client.upload_by_buffer(content.read())
        except Exception as e:
            return http.JsonResponse({'errno': RET.THIRDERR, 'errmsg': "上传图片错误"})

        # 上传成功：返回file_id,拼接图片访问URL
        file_id = result.get('Remote file_id')
        url = settings.FDFS_URL + file_id

        # 3. 将头像信息保存到用户模型
        user = request.user
        user.avatar_url = url
        user.save()

        # 4. 返回上传的结果<avatar_url>
        return http.JsonResponse({'errno': RET.OK, 'errmsg': "OK", 'data': {"avatar_url": url}})

class UserAuthenticationView(View):
    """实名认证"""
    def get(self, request):
        """获取用户实名信息"""
        user = User.objects.get(username = request.user.username)
        real_name = user.real_name
        id_card = user.id_card

        return http.JsonResponse({"errno": 0,
                                  "errmsg": "success",
                                  "data": {'real_name':real_name,
                                           'id_card':id_card}})

    def post(self, request):
        """设置用户实名信息"""
        dict = json.loads(request.body.decode())
        real_name = dict.get('real_name')
        id_card = dict.get('id_card')
        try:
            request.user.real_name = real_name
            request.user.id_card = id_card
            request.user.save()
        except Exception as e:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '数据库保存失败'})

        return http.JsonResponse({'errno': RET.OK, 'errmsg': "OK"})
