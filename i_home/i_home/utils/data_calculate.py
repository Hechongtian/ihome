import datetime


def days(str1,str2):
    try:
        date1=datetime.datetime.strptime(str1[0:10],"%Y-%m-%d")
        date2=datetime.datetime.strptime(str2[0:10],"%Y-%m-%d")
        nums =(date1-date2).days
        return nums
    except Exception as e:
        return None