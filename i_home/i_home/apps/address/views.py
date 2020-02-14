from django import http
from django.views import View
from address.models import Area


class AddrView(View):
    """城区列表"""
    def get(self,request):
        try:
           address_model_list = Area.objects.all()

           address_list = []

           for address_model in address_model_list:
               address_list.append({"aid":address_model.id ,"aname": address_model.name})
        except Exception as e:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '省份数据错误'})
        return http.JsonResponse({"errmsg": "OK",
                                  "errno": "0",
                                  "data": address_list
                                  })
