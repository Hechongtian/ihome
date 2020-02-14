import json
from django import http
from django.views import View
from house.models import House
from i_home.utils.data_calculate import days
from order.models import Order


class OrderView(View):
    """订单"""
    def post(self,request):
        """订单创建"""
        # 参数接受
        json_dict = json.loads(request.body.decode())
        house_id = json_dict.get('house_id')  # 房屋id
        start_date = json_dict.get('start_date')  # 开始时间
        end_date = json_dict.get('end_date')  # 结束时间

        house = House.objects.get(id = house_id) # 房间对象

        day = days(end_date, start_date)  # 定住时间
        money = (day * house.price) / 100

        try:
            order = Order.objects.create(user=request.user,
                                         house=house,
                                         begin_date=start_date,
                                         end_date=end_date,
                                         days=day,
                                         house_price=house.price,
                                         amount=money)
        except Exception as e:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '订单创建失败'})

        data = {"order_id": order.id}
        return http.JsonResponse({"data": data,
                                  "errno": "0",
                                  "errmsg": "OK"})

    def get(self,request):
        """订单查询"""
        role = request.GET.get('role')

        list = []

        if role == 'custom':
            try:
                orders = Order.objects.filter(user=request.user)
            except Exception as e:
                return http.JsonResponse({'code': 400,
                                      'errmsg': '订单搜寻失败'})

            for order in orders:
                list.append({
                    "amount": order.amount,
                    "comment": order.comment,
                    "ctime": order.update_time,
                    "days": order.days,
                    "end_date": order.end_date,
                    "img_url": order.house.index_image_url,
                    "order_id": order.id,
                    "start_date": order.begin_date,
                    "status": order.status,
                    "title": order.house.title
                })


        elif role == 'landlord':
            user = request.user

            try:
                houses = House.objects.filter(user=user)
                for house in houses:
                    orders = Order.objects.filter(house=house)
                    for order in orders:
                        list.append({
                            "amount": order.amount,
                            "comment": order.comment,
                            "ctime": order.update_time,
                            "days": order.days,
                            "end_date": order.end_date,
                            "img_url": order.house.index_image_url,
                            "order_id": order.id,
                            "start_date": order.begin_date,
                            "status": order.status,
                            "title": order.house.title
                        })
            except Exception as e:
                return http.JsonResponse({'code': 400,
                                      'errmsg': '订单搜寻失败'})


        return http.JsonResponse({"data": {"orders": list},
                                  "errmsg": "OK",
                                  "errno": "0"})

    def put(self,request):
        """订单修改(接单/拒单)"""
        json_dict = json.loads(request.body.decode())
        action = json_dict.get('action')
        order_id = json_dict.get('order_id')  # 订单号
        reason = json_dict.get('reason')  # 拒单原因

        if not all([action,order_id]):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '缺少必传参数'})

        if action == 'accept':
            try:
                order = Order.objects.get(id=order_id)
            except Exception as e:
                return http.JsonResponse({'code': 400,
                                          'errmsg': '数据库错误'})

            order.status = 'WAIT_COMMENT'
            if reason:
                order.comment = reason
            order.save()

        else:
            try:
                order = Order.objects.get(id = order_id)
            except Exception as e:
                return http.JsonResponse({'code': 400,
                                          'errmsg': '数据库错误'})

            order.status = 'REJECTED'
            if reason:
                order.comment = reason
            order.save()

        return http.JsonResponse({"errno": "0",
                                  "errmsg": "OK"})

class OrderCommentView(View):
    """订单评价"""
    def put(self,request):
        json_dict = json.loads(request.body.decode())
        comment = json_dict.get('comment')
        order_id = json_dict.get('order_id')

        if not all([comment,order_id]):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '缺少必传参数'})

        try:
            order = Order.objects.get(id=order_id)
        except Exception as e:
            return http.JsonResponse({'code': 400,
                                   'errmsg': '数据库错误'})

        try:
            order.comment = comment
            order.status = 'COMPLETE'
            order.save()
        except Exception as e:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '数据库错误'})

        return http.JsonResponse({"errno": "0",
                                  "errmsg": "OK"})
