from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from blog01 import models


def register(request):
    '''
    用 form 组件 和 auth 认证 来写注册函数
    :param request: 接收对象
    :return:response对象
    '''
    form_obj = Register_Form()
    if request.method == 'POST':
        print(request.POST)
        form_obj = Register_Form(request.POST)
        if form_obj.is_valid():
            form_data = form_obj.cleaned_data
            print(form_data)
            form_data.pop('re_password')
            print(form_data)
            # User.objects.create_user(**form_data)
            models.UserInfo.objects.create_user(**form_data)
            return HttpResponse('注册成功！')
    return render(request, 'register.html', {'form_obj': form_obj})


################ CBV 版的注册02 版本 #######################
from django import views
from blog01.forms import Register_Form
from django.contrib import auth


class Register_new(views.View):

    def get(self, request):
        form_obj = Register_Form()  # form组件写html
        return render(request, 'register_new.html', {'form_obj': form_obj})

    def post(self, request):
        print(222)
        print(request.POST)
        res = {"code": 0}
        # 先进行 验证码的校验
        v_code = request.POST.get('v_code', '')
        # 验证码正确后，使用form组件进行校验
        if v_code.upper() == request.session.get('v_code'):
            print('验证码填写正确！')
            form_obj = Register_Form(request.POST)  # form组件做校验
            print('form_obj---->', form_obj)
            # 用户输入的数据有效
            if form_obj.is_valid():
                # 1、注册用户
                form_cleaned_data = form_obj.cleaned_data
                print('form_cleaned_data----->', form_cleaned_data)
                # 注意移除不需要的re_password
                form_cleaned_data.pop('re_password')
                print(form_cleaned_data)

                # 获取到用户上传的头像文件
                avatar_file = request.FILES.get('avatar')

                # 利用auth 认证去校验注册的用户是否在数据库中已存在
                user = auth.authenticate(username=form_cleaned_data['username'], password=form_cleaned_data['password'])
                if user:
                    #  数据库中有此用户则不需要注册
                    res["code"] = 3
                    res["msg"] = "用户名已占用！"
                else:
                    #  数据库中没有此用户则需要注册
                    models.UserInfo.objects.create_user(**form_cleaned_data, avatar=avatar_file)
                    #  注册成功之后跳转到登录页面
                    res["msg"] = "/login/"
            # 用户填写的数据不符合要求
            else:
                res["code"] = 1
                # 所有字段的错误信息是通过以下form组件的命令获取
                res["msg"] = form_obj.errors
        # 验证码验证失败
        else:
            res["code"] = 2
            res["msg"] = "验证码错误！"
        return JsonResponse(res)


# def login(request):
#     '''
#     用 auth 认证 来写登录函数
#     :param request: 接收对象
#     :return: response对象
#     '''
#     error_msg = ''
#     if request.method == 'POST':
#         username = request.POST.get("user")
#         password = request.POST.get("pwd")
#         # 去数据库校验用户名和密码是否正确
#         user = auth.authenticate(request, username=username, password=password)
#         if user:
#             # 表示用户名密码正确
#             # 让当前用户登录,给cookie和session写入数据
#             auth.login(request,user)
#             return redirect('/index/')
#         else:
#             error_msg = '用户名密码不正确'
#     return  render(request,'login.html',{'error_msg':error_msg})

@login_required
def index(request):
    '''
    登录之后进入主页的函数
    :param request: 接收对象
    :return: response对象
    '''
    # request.user.is_authenticated()   判断当前的request.user是否经过认证，经过认证返回True,没有经过认证返回False
    print(request.user, request.user.is_authenticated())
    return render(request, 'index.html')


###################  bbs博客首页   ################
from utils.mypage import MyPage


class Index(views.View):

    def get(self, request):
        article_list = models.Article.objects.all()
        print('article_list---->', article_list)
        # 分页
        data_amount = article_list.count()  # 文章总数量
        page_num = request.GET.get('page', 1)  # 通过url 的get请求获取到当前页面
        page_obj = MyPage(page_num, data_amount, per_page_data=2, url_prefix='index_new')
        # 按照分页的设置对总数据进行切片
        data = article_list[page_obj.start:page_obj.end]
        page_html = page_obj.ret_html()
        return render(request, 'index_new.html', {"article_list": data, "page_htnl": page_html})

    def post(self, request):
        res = {"code": 0}
        return JsonResponse(res)


def logout(request):
    '''
    用auth 认证 来写注销用户的函数
    :param request: 接收对象
    :return: response对象
    '''
    # 将当前请求的sessoin数据删除
    auth.logout(request)
    return redirect('/login/')


@login_required
def set_password(request):
    '''
    登录之后修改密码：
        1、登录的用户才能修改密码
        2、修改密码之前先校验原密码是否正确
    :param request:接收对象
    :return:response对象
    '''
    user = request.user
    err_msg = ''
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')  # 旧密码
        new_password = request.POST.get('new_password', '')  # 新密码
        repeat_password = request.POST.get('repeat_password', '')  # 确认密码
        # 检查旧密码是否正确
        if user.check_password(old_password):
            if not new_password:
                err_msg = '新密码不能为空！'
            elif new_password != repeat_password:
                err_msg = '两次密码不一致！'
            else:
                user.set_password(new_password)
                user.save()
                return redirect('/login/')
        else:
            err_msg = '原密码输入错误！'
    return render(request, 'set_password.html', {'err_msg': err_msg})


# ################ CBV 版的登录 #######################
# from django import views
# from django.http import JsonResponse
# from blog01.forms02 import Login_Form
#
#
# class Login(views.View):
#
#     def get(self,request):
#         form_obj = Login_Form()
#         return render(request,'login_ajax.html',{'form_obj':form_obj})
#
#     def post(self,request):
#         res = {"code":0}
#         print(request.POST)
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         # 去数据库校验用户名和密码是否正确
#         user = auth.authenticate(request, username=username, password=password)
#         if user:
#             # 表示用户名密码正确
#             # 让当前用户登录,给cookie和session写入数据
#             auth.login(request, user)
#         else:
#             res["code"] = 1
#             res["msg"] = '用户名或密码不正确！'
#         return JsonResponse(res)

################ 登录验证码 版本1 #######################
# def v_code(request):
# # 随机生成图片
#     from PIL import Image
#     import random
#     # 生成随机颜色的方法
#     def random_color():
#         return random.randint(0,255),random.randint(0,255),random.randint(0,255)
#     # 生成图片对象
#     image_obj = Image.new(
#         'RGB',  # 生成图片的模式
#         (250,35), # 生成图片的大小
#         random_color()  # 随机生成图片的颜色
#     )
# # 直接将生成的图片保存在内存中
#     from io import BytesIO
#     f = BytesIO()
#     image_obj.save(f,'png')
#     # 从内存中读取图片数据
#     data = f.getvalue()
#     return HttpResponse(data,content_type='image/png')

################ 登录验证码 版本2 #######################
# def v_code(request):
# # 随机生成图片
#     from PIL import Image
#     import random
#     # 生成随机颜色的方法
#     def random_color():
#         return random.randint(0,255),random.randint(0,255),random.randint(0,255)
#     # 生成图片对象
#     image_obj = Image.new(
#         'RGB',  # 生成图片的模式
#         (250,35), # 生成图片的大小
#         random_color()  # 随机生成图片的颜色
#     )
#
# # 生成一个准备写字的画笔
#     from PIL import ImageDraw , ImageFont
#     draw_obj = ImageDraw.Draw(image_obj)    # 在哪里写
#     font_obj = ImageFont.truetype('static/fonts/kumo.ttf',size=28)   # 加载本地的字体文件
#
# # 生成随机验证码
#     tmp = []
#     for i in range(5):
#         n = str(random.randint(0,9))
#         l = chr(random.randint(65,90))
#         u = chr(random.randint(97,122))
#         r = random.choice([n,l,u])
#         tmp.append(r)
#         # 每一次取到要写的东西之后，往图片上写
#         draw_obj.text(
#             (i * 45 + 25 , 0), # 坐标---->（x,y）
#             r,  # 内容
#             fill=random_color(), # 颜色
#             fonts=font_obj # 字体
#         )
#
# # 得到最终的验证码
#     v_code = ''.join(tmp)
#
# # 由于设置为全局变量，多个浏览器没办法区别验证码，故保存为全局变量是万万不可的！
# # 将盖茨请求生成的验证码保存在该请求对应的session数据中
#     request.session["v_code"] = v_code.upper()
#
#
# # 直接将生成的图片保存在内存中
#     from io import BytesIO
#     f = BytesIO()
#     image_obj.save(f,'png')
#     # 从内存中读取图片数据
#     data = f.getvalue()
#     return HttpResponse(data,content_type='image/png')


################ 登录验证码 版本3 #######################
# def v_code(request):
# # 随机生成图片
#     from PIL import Image
#     import random
#     # 生成随机颜色的方法
#     def random_color():
#         return random.randint(0,255),random.randint(0,255),random.randint(0,255)
#     # 生成图片对象
#     image_obj = Image.new(
#         'RGB',  # 生成图片的模式
#         (250,35), # 生成图片的大小
#         random_color()  # 随机生成图片的颜色
#     )
#
# # 生成一个准备写字的画笔
#     from PIL import ImageDraw , ImageFont
#     draw_obj = ImageDraw.Draw(image_obj)    # 在哪里写
#     font_obj = ImageFont.truetype('static/fonts/kumo.ttf',size=28)   # 加载本地的字体文件
#
# # 生成随机验证码
#     tmp = []
#     for i in range(5):
#         n = str(random.randint(0,9))
#         l = chr(random.randint(65,90))
#         u = chr(random.randint(97,122))
#         r = random.choice([n,l,u])
#         tmp.append(r)
#         # 每一次取到要写的东西之后，往图片上写
#         draw_obj.text(
#             (i * 45 + 25 , 0), # 坐标---->（x,y）
#             r,  # 内容
#             fill=random_color(), # 颜色
#             fonts=font_obj # 字体
#         )
#
# # 加干扰线
#     width = 250 # 图片宽度(防止越界)
#     height = 35 # 图片高度(防止越界)
#     for i in range(5):
#         x1 = random.randint(0,width)
#         x2 = random.randint(0,width)
#         y1 = random.randint(0,height)
#         y2 = random.randint(0,height)
#         draw_obj.line(
#             (x1,y1,x2,y2),
#             fill=random_color(), # 随机生成颜色
#         )
#
# # 得到最终的验证码
#     v_code = ''.join(tmp)
#
# # 由于设置为全局变量，多个浏览器没办法区别验证码，故保存为全局变量是万万不可的！
# # 将盖茨请求生成的验证码保存在该请求对应的session数据中
#     request.session["v_code"] = v_code.upper()
#
#
# # 直接将生成的图片保存在内存中
#     from io import BytesIO
#     f = BytesIO()
#     image_obj.save(f,'png')
#     # 从内存中读取图片数据
#     data = f.getvalue()
#     return HttpResponse(data,content_type='image/png')


################ 登录验证码 版本4 #######################
# 返回响应的时候告诉浏览器不要缓存
from django.views.decorators.cache import never_cache


@never_cache
def v_code(request):
    # 随机生成图片
    from PIL import Image
    import random
    # 生成随机颜色的方法
    def random_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    # 生成图片对象
    image_obj = Image.new(
        'RGB',  # 生成图片的模式
        (240, 30),  # 生成图片的大小
        random_color()  # 随机生成图片的颜色
    )

    # 生成一个准备写字的画笔
    from PIL import ImageDraw, ImageFont
    draw_obj = ImageDraw.Draw(image_obj)  # 在哪里写
    font_obj = ImageFont.truetype('static/fonts/kumo.ttf', size=28)  # 加载本地的字体文件

    # 生成随机验证码
    tmp = []
    for i in range(5):
        n = str(random.randint(0, 9))
        l = chr(random.randint(65, 90))
        u = chr(random.randint(97, 122))
        r = random.choice([n, l, u])
        tmp.append(r)
        # 每一次取到要写的东西之后，往图片上写
        draw_obj.text(
            (i * 45 + 25, 0),  # 坐标---->（x,y）
            r,  # 内容
            fill=random_color(),  # 颜色
            font=font_obj  # 字体
        )

    # 加干扰线
    width = 250  # 图片宽度(防止越界)
    height = 35  # 图片高度(防止越界)
    for i in range(5):
        x1 = random.randint(0, width)
        x2 = random.randint(0, width)
        y1 = random.randint(0, height)
        y2 = random.randint(0, height)
        draw_obj.line(
            (x1, y1, x2, y2),
            fill=random_color(),  # 随机生成颜色
        )

    # 加干扰点
    width = 250  # 图片宽度(防止越界)
    height = 35  # 图片高度(防止越界)
    for i in range(5):
        draw_obj.point(
            [random.randint(0, width), random.randint(0, height)],
            fill=random_color(),
        )
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw_obj.arc(
            (x, y, x + 4, y + 4),
            0,
            90,
            fill=random_color()
        )

    # 得到最终的验证码
    v_code = ''.join(tmp)

    # 由于设置为全局变量，多个浏览器没办法区别验证码，故保存为全局变量是万万不可的！
    # 将盖茨请求生成的验证码保存在该请求对应的session数据中
    request.session["v_code"] = v_code.upper()

    # 直接将生成的图片保存在内存中
    from io import BytesIO
    f = BytesIO()
    image_obj.save(f, 'png')
    # 从内存中读取图片数据
    data = f.getvalue()
    return HttpResponse(data, content_type='image/png')


################ CBV 版的登录02版本 #######################
from django import views
from django.http import JsonResponse
from blog01.forms02 import Login_Form


class Login(views.View):

    def get(self, request):
        form_obj = Login_Form()
        return render(request, 'login_ajax.html', {'form_obj': form_obj})

    def post(self, request):
        res = {"code": 0}
        print(request.POST)
        username = request.POST.get("username")
        password = request.POST.get("password")
        v_code = request.POST.get('v_code')
        print(v_code)
        # 先判断验证码是否正确
        if v_code.upper() != request.session.get('v_code', ''):
            print(111)
            res["code"] = 1
            res["msg"] = "验证码错误！"
        else:
            print(222)
            # 去数据库校验用户名和密码是否正确
            user = auth.authenticate(request, username=username, password=password)
            if user:
                # 表示用户名密码正确
                # 让当前用户登录,给cookie 和 session 写入数据
                auth.login(request, user)
            else:
                # 表示用户名或密码不正确
                res["code"] = 1
                res["msg"] = '用户名或密码不正确！'
        return JsonResponse(res)


###########################  滑动验证码  ##############################
from utils.geetest import GeetestLib

# 请在官网申请ID使用，示例ID不可使用
pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"


def pcgetcaptcha(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


# 滑动验证码版本的登录函数
def login_huadong(request):
    res = {"code": 0}
    if request.method == "POST":
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            # 滑动验证码校验通过
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = auth.authenticate(username=username, password=password)
            if user:
                # 用户名和密码正确
                auth.login(request, user)
            else:
                # 用户名或者密码不正确
                res["code"] = 1
                res["msg"] = "用户名或者密码不正确！"
        else:
            # 滑动验证码校验失败
            res["code"] = 2
            res["msg"] = "验证码错误！"
        return JsonResponse(res)
    form_obj = Login_Form()
    return render(request, 'login_ajax_huadong.html', {"form_obj": form_obj})


######################## BBS项目的个人博客站点 版本01 #######################################
class Blog(views.View):

    def get(self, request, username):
        # 从数据库UserInfo表中找到此用户
        user_objs_list = models.UserInfo.objects.filter(username=username)
        print('user_objs_list---->', user_objs_list)
        user_obj = user_objs_list.first()
        article_category = user_obj.blog.tag_set.all()
        print('article_category---->', article_category)
        article_tag = user_obj.blog.tag_set.all()
        print('article_tag---->', article_tag)
        article_obj = user_obj.article_set.all()
        print('article_obj--->', article_obj)

        # 分页
        data_amount = article_obj.count()  # 文章总数量
        page_num = request.GET.get('page', 1)  # 通过url 的get请求获取到当前页面
        page_obj = MyPage(page_num, data_amount, per_page_data=1, url_prefix='blog')
        # 按照分页的设置对总数据进行切片
        data = article_obj[page_obj.start:page_obj.end]
        page_html = page_obj.ret_html()

        return render(request, 'blog.html', {"user_obj": user_obj, "data": data, "page_html": page_html, })


###################################### BBS项目的个人博客站点 版本02 #######################################
from django.shortcuts import get_object_or_404
from django.db.models import Count

def blog_new(request,username):
    '''
    个人博客站点
    :param request: request对象
    :param username: 所要访问的用户
    :return: response对象
    '''
    """
    # 从数据库UserInfo表中找到所要访问的用户
    user_obj = models.UserInfo.objects.filter(username=username).first()
    print('user_obj1---->', user_obj)
    # 由于用户可能会在url上乱输一气，导致user_obj 为none，此时需要判断
    if not user_obj:
        return HttpResponse('404……')
    """

    user_obj = get_object_or_404(models.UserInfo, username=username)    # 等同于引号中的内容
    print('user_obj2---->', user_obj)

    # 获取当前访问的用户所对应的个人博客站点（blog）
    blog_obj = user_obj.blog

    # 查找当前用户博客站点所对应的文章分类都有哪一些？
    category_list = models.Category.objects.filter(blog = blog_obj)

    # 查找当前用户博客站点所对应的文章标签都有哪一些？
    tag_list = models.Tag.objects.filter(blog = blog_obj)


    """
    新知识点：extra -----> 半ORM半原生sql语句
    对<当前用户博客站点>所对应的<所有文章>
        按照：年月  进行：分组 & 查询
    步骤如下：    
     1、查找当前用户所对应的所有文章都有哪一些？
    article_list = models.Article.objects.filter(user = user_obj)
     2、将当前用户所有文章的创建时间 格式化成 年- 月 的格式，方便后续分组
    create_time_format = article_list.extra(
        select={
            "create_y_m":"DATE_FORMAT(create_time,'%%Y年%%m月')"
        }
    ).values('create_y_m')
    # create_time_format---> <QuerySet [{'create_y_m': '2018年08月'}, {'create_y_m': '2018年08月'}, {'create_y_m': '2017年06月'}, {'create_y_m': '2018年06月'}]>
    print('create_time_format--->',create_time_format)
     3、用上一步时间格式化得到的create_y_m字段做分组，统计出每个分组对应的文章数
    article_count_obj = create_time_format.annotate(article_count = Count('id'))
    # article_count_obj---> <QuerySet [{'create_y_m': '2018年08月', 'article_count': 2}, {'create_y_m': '2017年06月', 'article_count': 1}, {'create_y_m': '2018年06月', 'article_count': 1}]>
    print('article_count_obj--->',article_count_obj)
     4、把页面需要的日期归档和文章数字段取出来
    archive_list = article_count_obj.values('create_y_m','article_count')
    # archive_list---> <QuerySet [{'create_y_m': '2018年08月', 'article_count': 2}, {'create_y_m': '2017年06月', 'article_count': 1}, {'create_y_m': '2018年06月', 'article_count': 1}]>
    print('archive_list--->',archive_list)
    """
    # 查找当前用户所对应的所有文章都有哪一些？
    article_list = models.Article.objects.filter(user = user_obj)
    # 对当前用户博客站点所对应的所有文章按照年月的格式化时间来分组，来进行日期归档和显示文章数量
    archive_list = article_list.extra(
        select={
            "y_m":"DATE_FORMAT(create_time,'%%Y年%%m月')"
        }
    ).values('y_m').annotate(article_count = Count('id')).values('y_m','article_count')
    print('archive_list--->',archive_list)

    return render(request, 'blog_new.html',
                  {"blog": blog_obj,
                   "category_list":category_list,
                   "tag_list":tag_list,
                   "archive_list":archive_list,
                   "article_list":article_list,
                   "user_obj":user_obj
                   })
