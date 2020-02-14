import json
from django import http
from django.core.paginator import Paginator, EmptyPage
from django.views import View
from house.models import House, Facility, HouseImage
from i_home.libs.response_code import RET
from i_home.utils.fastdfs.fastdfs_storage import FastDFSStorage
from order.models import Order


class MyhouseView(View):
    """我的房源"""
    def get(self,request):
        user = request.user
        houses = House.objects.filter(user=user)

        house_list = []

        for house in houses:
            house_list.append({
                'address':house.address,
                'area_name':house.area.name,
                'ctime':house.create_time,
                'house_id':house.id,
                'img_url':house.index_image_url,
                'order_count':house.order_count,
                'price':house.price,
                'room_count':house.room_count,
                'title':house.title,
                'user_avatar':user.avatar_url
            })

        return http.JsonResponse({'errmsg': 'OK', 'errno': '0', 'data': house_list})

class PublishHouseView(View):
    """发布房源"""
    def post(self,request):
        # 获取参数
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')
        price = json_dict.get('price')
        area_id = json_dict.get('area_id')
        address = json_dict.get('address')
        room_count = json_dict.get('room_count')
        acreage = json_dict.get('acreage')
        unit = json_dict.get('unit')
        capacity = json_dict.get('capacity')
        beds = json_dict.get('beds')
        deposit = json_dict.get('deposit')
        min_days = json_dict.get('min_days')
        max_days = json_dict.get('max_days')
        facility = json_dict.get('facility')
        # 判断参数是否缺失
        if not all([title, price, area_id, address, room_count, acreage,unit,capacity,beds,deposit,min_days,max_days,facility]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 保存房源信息
        try:
            house = House.objects.create(
                user=request.user,
                title=title,
                price = price,
                area_id = area_id,
                address = address,
                room_count = room_count,
                acreage = acreage,
                unit = unit,
                capacity = capacity,
                beds = beds,
                deposit = deposit,
                min_days = min_days,
                max_days = max_days,
            )

            for i in facility:
                fac = Facility.objects.get(id=int(i))
                house.facilities.add(fac)

        except Exception as e:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '新增房源失败'})

        data = {
            "house_id":house.id
        }

        return http.JsonResponse({'errno': RET.OK,
                                  'errmsg': "Ok",
                                  'data': data})

class HouseImageView(View):
    """房源照片上传"""
    def post(self,request,house_id):
        house_image = request.FILES.get('house_image')
        if house_image is None:
            return http.JsonResponse({'code': 400,'errmsg': '图片为空'})
        try:
            ret = FastDFSStorage()  # 得到fast对象

            file_id = ret.save('7.jpg', house_image)  # 文件组路径

            image_path = ret.url(file_id)  # 传进去的文件路径

            house = House.objects.get(user=request.user, id=house_id)
            # 查询有没有主图片
            house_count = house.index_image_url
            print(house_count)

            if not house_count:  # 如果没有主图片
                house.index_image_url = image_path
                house.save()
            else:  # 如果有图片
                HouseImage.objects.create(house=house, url=image_path)

        except Exception as e:
            return http.JsonResponse({'code': 400,'errmsg': '数据库错误'})

        return http.JsonResponse({'errno': RET.OK,
                                  'errmsg': "OK",
                                  'data': {"url":image_path}
                                  })

class HouseInforView(View):
    """房源详情"""
    def get(self,request,house_id):
        user = request.user
        try:
            house_info = House.objects.get(id=house_id)
        except Exception as e:
            return http.JsonResponse({'code': 400,'errmsg': '数据库错误'})

        comments = []  # 评论
        coms = Order.objects.filter(house=house_info)
        for com in coms:
            comments.append({
                "comment": com.comment,
                "ctime": com.update_time,
                "user_name": com.user.username
            })

        facilities = []
        ret = Facility.objects.filter(house=house_info)
        for i in ret:
            facilities.append(int(i.id))

        img_urls = [house_info.index_image_url]  # 房屋图片列表
        house_image = HouseImage.objects.filter(house=house_info)
        for image in house_image:
            img_urls.append(image.url)

        house = {
            "acreage": house_info.acreage,
            "address": house_info.address,
            "beds": house_info.beds,
            "capacity": house_info.capacity,
            "comments": comments,  # 评论
            "deposit": house_info.deposit,
            "facilities": facilities,  # 设施信息id列表，如：[7, 8]
            "hid": house_info.id,
            "img_urls": img_urls,  # 房屋图片列表
            "max_days": house_info.max_days,
            "min_days": house_info.min_days,
            "price": house_info.price,
            "room_count": house_info.room_count,
            "title": house_info.title,
            "unit": house_info.unit,
            "user_avatar": house_info.user.avatar_url,
            "user_id": house_info.user.id,
            "user_name": house_info.user.username,
        }

        # 获取当前用户登入状态
        username = request.user.is_authenticated

        if not username:
            user_id = -1
        else:
            user_id = request.user.id

        data = {
            "house": house,
            "user_id": user_id
        }


        return http.JsonResponse({"errmsg": "OK", "errno": RET.OK, "data": data})

class HouseRecoView(View):
    """首页房源推荐"""
    def get(self,request):
        try:
            houses = House.objects.all()
        except Exception as e:
            return http.JsonResponse({'code': 400,'errmsg': '数据库错误'})

        data = []
        for house in houses:
            data.append({
                'house_id': house.id,
                'img_url': house.index_image_url,
                'title': house.title
            })

        return http.JsonResponse({'data':data,
                                  'errmsg':'OK',
                                  'errno':'0'})

class SearchView(View):
    """房源搜索"""
    def get(self,request):

        # 获取参数
        aid = request.GET.get('aid')
        sd = request.GET.get('sd')
        ed = request.GET.get('ed')
        sk = request.GET.get('sk')
        pages = request.GET.get('p')

        # 排序方法
        if sk == 'booking':
            sk = 'order_count'
        elif sk == 'price-inc':
            sk = 'price'
        elif sk == 'price-des':
            sk = '-price'
        else:
            sk = '-update_time'

        # times = days(ed, sd)
        #页数
        if not pages:
            pages = 1

        if not aid:
            houses = House.objects.all().order_by(sk)
        else:
            houses = House.objects.all().order_by(sk)

        paginator = Paginator(houses, 5)

        try:
            house = paginator.page(pages)
        except EmptyPage:
            # 如果page_num不正确，默认给用户400
            return http.JsonResponse({'code': 400,'errmsg': 'page_num错误'})

        # 获取列表页总页数
        total_page = paginator.num_pages

        hous = []

        for hou in house:
            # if hou.min_days < times and hou.max_days > times:
            hous.append({
                'house_id': hou.id,
                'order_count': hou.order_count,
                'title': hou.title,
                'ctime': hou.update_time,
                'price': hou.price,
                'area_name': hou.area.name,
                'address': hou.address,
                'room_count': hou.room_count,
                'img_url': hou.index_image_url,
                'user_avatar': hou.user.avatar_url
            })

        data = {'houses':hous,
                'total_page':total_page}

        return http.JsonResponse({'data':data,
                                    'errmsg':'请求成功',
                                    'errno':'0'})
