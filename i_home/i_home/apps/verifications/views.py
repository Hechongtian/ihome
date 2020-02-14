import json
import random
from django import http
from django.views import View
from django_redis import get_redis_connection
from i_home.libs.captcha.captcha import captcha
from i_home.libs.response_code import RET


class ImageCodeView(View):
    '''返回图形验证码的类视图'''

    def get(self, request):
        '''
        生成图形验证码, 保存到redis中, 另外返回图片
        :param request:请求对象
        :param uuid:浏览器端生成的唯一id
        :return:一个图片
        '''

        uuid = request.GET.get('cur')
        pr_uuid = request.GET.get('pre')
        # 1.调用工具类 captcha 生成图形验证码
        text, image = captcha.generate_captcha()

        # 2.链接 redis, 获取链接对象
        redis_conn = get_redis_connection('verify_code')

        if pr_uuid:
            redis_conn.delete('img_%s' % pr_uuid)
        # 3.利用链接对象, 保存数据到 redis, 使用 setex 函数
        # redis_conn.setex('<key>', '<expire>', '<value>')
        redis_conn.setex('img_%s' % uuid, 300, text)

        # 4.返回(图片)
        return http.HttpResponse(image,content_type='image/jpg')


class SMSCodeView(View):
    """短信验证码"""

    def post(self, request):
        """
        :param reqeust: 请求对象
        :param mobile: 手机号
        :return: JSON
        """

        # 1. 接收参数
        dict = json.loads(request.body.decode())
        mobile = dict.get('mobile')
        image_code_client = dict.get('image_code')
        uuid = dict.get('image_code_id')

        # 2. 校验参数
        if not all([image_code_client, uuid]):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '缺少必传参数'})

        # 3. 创建连接到redis的对象
        redis_conn = get_redis_connection('verify_code')

        # 4. 提取图形验证码
        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            # 图形验证码过期或者不存在
            return http.JsonResponse({'code': 400,
                                      'errmsg': '图形验证码失效'})

        # 5. 删除图形验证码，避免恶意测试图形验证码（省去）
        # 6. 对比图形验证码
        # bytes 转字符串
        image_code_server = image_code_server.decode()
        # 转小写后比较
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code': 400,
                                      'errmsg': '输入图形验证码有误'})

        # 7. 生成短信验证码：生成6位数验证码
        sms_code = '%06d' % random.randint(0, 999999)
        print(sms_code)

        # 8. 保存短信验证码
        # 短信验证码有效期，单位：300秒
        redis_conn.setex('sms_%s' % mobile,
                         300,
                         sms_code)

        # 9. 发送短信验证码
        # 短信模板
        # CCP().send_template_sms(mobile,[sms_code, 5], 1)

        # 10. 响应结果
        return http.JsonResponse({'errno': RET.OK,'errmsg': "短信发送成功"})
