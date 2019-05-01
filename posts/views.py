from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Count,Q
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect,JsonResponse, Http404
from django.urls import reverse
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator , EmptyPage , PageNotAnInteger
from django.shortcuts import render,get_object_or_404,redirect,reverse
from .models import Post,Category,Instance,City,Area,Author,PhoneOTP,User,\
UserMembership,Membership,Subscription
from marketing.models import Signup
from .forms import CommentForm,ProductForm,UserCreationForm,RawProductForm\
,OTPForm,OTPFormMatch,ProfileUpdateForm,customAuthenticationForm,UserLoginForm,\
PostForm,SubscriptionForm

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login , logout
from django.contrib.auth.decorators import login_required
from marketing.forms import EmailSignupForm
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.views.generic import DeleteView
from postmark import PMMail
from django.template.loader import get_template
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.views.generic import TemplateView

# from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from kavenegar import *
import random

# User= get_user_model

#
# def UserMembershipCreateview(request):
#
#     form = UsermemForm(request.POST or None ,request.FILES or None or None)
#     if form.is_valid():
#        key1 = random.randint(999, 9999)
#        # key2 = random.randint(999, 9999)
#        usermembership = UserMembership.objects.create(membership=Membership.objects.filter(membership_type=form.cleaned_data.get("membership")[0]).first())
#
#        up=form.cleaned_data.get("up")
#        show=form.cleaned_data.get("show")
#        if usermembership.membership == up:
#           usermembership.up_key=key1
#        # usermembership=form.save(commit=False)
#
#           usermembership.user = request.user
    #
    #       usermembership.save()
    #       return HttpResponseRedirect('/profile/')
    #
    # context={
    # 'form':form
    # }
    #
    # #
    # # args = {'form':form}
    # return render(request,'user_membership.html',context)

def profile_view(request):
    user_membership = get_user_membership(request)
    user_subscription = get_user_subscription(request)
    context = {
       'user_membership':user_membership,
       'user_subscription':user_subscription
    }
    return render(request,"memberships/profile.html", context)

def get_user_membership(request):
    user_membership_qs = UserMembership.objects.filter(user=request.user)
    if user_membership_qs.exists():
        return user_membership_qs.first()
    return None

def get_user_subscription(request):
    user_subscription_qs = Subscription.objects.filter(user_membership = get_user_membership(request))
    if user_subscription_qs.exists():
        user_subscription = user_subscription_qs.first()
        return user_subscription
    return None

def get_selected_membership(request):
    membership_type = request.session['selected_membership_type']
    selected_membership_qs = Membership.objects.filter(membership_type=membership_type)
    if selected_membership_qs.exists():
        return selected_membership_qs.first()
    return None


class MembershipSelectView(ListView):
    model = Membership

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        current_membership = get_user_membership(self.request)
        context['current_membership'] = str(current_membership.membership)
        return context

    def post(self,request,  **kwrags):
        selected_membership_type = request.POST.get('membership_type')

        user_membership = get_user_membership(request)
        user_subscription = get_user_subscription(request)

        selected_membership_qs = Membership.objects.filter(
        membership_type = selected_membership_type)

        if selected_membership_qs.exists():
            selected_membership = selected_membership_qs.first()


        if user_membership.membership == selected_membership:
            if user_subscription != None :
                messages.info(request,"you already have this membership.your \
                   next payment is due {}".format('get this format from value stripe'))
                return HttpResponseRedirect(reaquest.META.get('HTTP_REFERER'))

        request.session['selected_membership_type']= selected_membership.membership_type

        return HttpResponseRedirect(reverse('payment'))




def PaymentView(request):

    user_membership = get_user_membership(request)
    selected_membership = get_selected_membership(request)


    # publishKey = settings.STRIPE_PUBLISHABLE_KEY

    if request.method == "POST":
        try:
            # token = request.POST['stripeToken']
            key = random.randint(999, 9999)
            subscription = Subscription.objects.create(  subscription_id=key)


            return redirect(reverse('memberships:update-transactions',
               kwargs = {
                   'subscription_id' : subscription.id
               }))

        except stripe.CardError as e:
            messages.info(request, "your card has been declined")
    context = {
      # 'publishKey': publishKey,
      'selected_membership': selected_membership
    }

    return render(request,'membership_payment.html', context)

def updateTransactions(request, subscription_id):

    user_membership = get_user_membership(request)
    selected_membership = get_selected_membership(request)

    user_membership.membership = selected_membership
    user_membership.save()

    sub, created=Subscription.objects.get_or_create(user_membership=user_membership)
    sub.stripe_subscription_id = subscription_id
    sub.active = True
    sub.save()

    try:
        del request.session['selected_membership_type']
    except:
        pass
    messages.info(request,"sucsessfully created{} membership".format(selected_membership))
    return redirect('/mypage')



















def city(request):

    return render(request,'countries.html')

def send_email(request):
    if request.method == "POST":
        # name = request.POST.get("name")
        email = request.POST.get("email")
        # message = request.POST.get("message")
        name= 'name'
        # email = 'misterfh2@gmail.com'
        message = 'hello there'
        subject = 'Contact Form Received'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = ['info@microchip97.ir']

        contact_message = '{0}, from {1} with email {2}'.format(message,name, email)

        # context = {
        #   'user':name,
        #   'email':email,
        #   'message':message
        # }
        # contact_message = get_template('contact_message.txt').render(context)

        send_mail(subject,message,from_email,[email],fail_silently=False,)
        if  send_mail(subject,message,from_email,[email],fail_silently=False,):
        # send_mail( to_email)
         # fail_silently = True
           return redirect("/blog/")
        else:
            return redirect("/send/")


    return render(request,'send_mail.html',{})



#
# def send_email(request):
#     if request.method == "POST":
#         email = request.POST.get("email")
#         message = PMMail(api_key = settings.POSTMARK_API_TOKEN,
#                          subject = "فعال سازی اکانت تودو",
#                          sender = "info@microchip97.ir",
#                          to = email,
#                          text_body = "برای فعال سازی ایمیلی تودویر خود روی لینک روبرو کلیک کنید ",
#                          # {}?email={}&code={}".format(request. build_absolute_uri('/accounts/register/'), email, code),
#                          tag = "account request")
#         message.send()
#         return redirect("/blog/")
#         # else:
#         #     return redirect("/send/")


    return render(request,'send_mail.html',{})







def send_otp_phone(phone):
    # key = random.randint(999, 9999)
    receptor = phone
    API_Key = '684D4A436478463574737361574A714F4B46506C6F6742746E615A6133473932'
    url = 'https://api.kavenegar.com/v1/%s/sms/send.json' % API_Key
    key = random.randint(999, 9999)
    payload = {'receptor': receptor,'message':key}
    requests.post(url, data=payload)
    if phone:
        return key
    else:
        return False


# @login_required
def send_otp_this(request):

    if request.method=="GET":
         form = OTPForm(request.GET)
         phone_number = request.GET.get('phone')
         if phone_number:
             phone = str(phone_number)
             user = User.objects.filter(phone = phone)
             if user.exists():
                 return HttpResponseRedirect('/login')

                    # return JsonResponse({'send': False, 'taken': True, 'detail':'phone number already exist'})
             else:

                 key = send_otp_phone(phone)
                 if key:
                     old = PhoneOTP.objects.filter(phone = phone)
                     if old.exists():
                         old = old.first()
                         count = old.count
                         if count > 2:
                             return Response({
                                    'status':False,
                                    'detail':'Sending otp error.limit exceeded'
                             })
                         old.count = count +1
                         old.save()
                         print("count increase", count)
                         # return JsonResponse({'send': True, 'taken': True})
                         return HttpResponseRedirect('/otp-match/')


                     else:

                         PhoneOTP.objects.create(
                           phone = phone,
                           otp = key,
                         )
                         return HttpResponseRedirect('/otp-match/')

                         # return JsonResponse({'send':True , 'taken': True,'detail' :'OTP sent successfully'})


                 else:
                     return JsonResponse({'send': False, 'taken': True,'detail' :'OTP sent successfully'})


         # else:
         #     return JsonResponse({'send':False , 'taken': True,'detail' :'OTP sent successfully'})


            # return HttpResponseRedirect('/otp-match/')

    else:
        form = OTPForm()
    context = {
     'form':form,
     # 'phone':phone,

     }
    return render(request,'phone.html',context)


        # try:
        #     api = KavenegarAPI('684D4A436478463574737361574A714F4B46506C6F6742746E615A6133473932')
        #     params = {
        #         'receptor': '09357680786',
        #         'template': 'sms.html',
        #         'token': '5131',
        #         'type': 'sms',#sms vs call
        #     }
        #   response = api.verify_lookup(params)
        #   print(response)
        # except APIException as e:
        #   print(e)
        # except HTTPException as e:
        #   print(e)


def otp_match(request):
    if request.method == "GET":
        form =  OTPFormMatch(request.GET)
        phone = request.GET.get('phone',False)
        otp_sent = request.GET.get('otp',False)

        if phone and otp_sent:
            old = PhoneOTP.objects.filter(phone = phone)
            if old.exists():
                old = old.first()
                otp = old.otp
                if str(otp_sent) == str(otp):
                    old.validated = True
                    old.save()

                    return HttpResponseRedirect('/register/')
                    # return JsonResponse({'taken':True , 'detail' :'OTP matched'})

                else:

                    return JsonResponse({'taken':False ,  'detail':'OTP INCOORECT'})

                # return HttpResponseRedirect('/blog/')


    else:
        form = OTPFormMatch()

    context = {
        'form':form,
        # 'phone':phone,
        # 'otp':otp_user,

      }
    return render(request,'phone_match.html',context)



# def register(request, *args, **kwargs):
#     form  = RegisterForm(request.POST or None)
#     if form.is_valid():
#         form.save()
#         return HttpResponseRedirect('/login')
#     context = {
#        'form':form
#     }
#     return render(request, "register.html",context)

# def login_view(request, *args, **kwargs):
#     form = UserLoginForm(request.POST or None)
#     if form.is_valid():
#         user_obj = form.cleaned_data.get('user_obj')
#         login(request, user_obj)
#         return HttpResponseRedirect("/")
#     return render(request, "login.html",{"form":form})

# def logout_view(request):
#     logout(request)
#     return HttpResponseRedirect("/login")

# def get_user_author(request):
#     user_author_qs = Author.objects.filter(user=request.user)
#     if user_author_qs.exists():
#         return user_author_qs.first()
#     return None



# @receiver(post_save, sender=User)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         Author.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def create_profile(sender, instance, **kwargs):
#     # Author.objects.create(user=kwargs.get('instance'))
#     Author.objects.create(user=instance)


# @receiver(post_save, sender=Author)
# def create_author(sender, instance, created, **kwargs):
#     if created:
#          Post.objects.create(author=instance)

# @receiver(post_save, sender=User)
# def create_author(sender, instance, **kwargs):
#     # Author.objects.create(user=kwargs.get('instance'))
#     Post.objects.create(user=instance)




def filter_dropdown2(request):
    context = {}

    state = request.GET.get('state')
    city = request.GET.get('city')
    context['form'] = StateForm( state,city)
    # Filtro
    q = request.GET.get('area')
    # if q:
    #     q = q.replace('.', '')
    #     post = Post.objects.filter(area=str(q))
    #     context['post'] = post
    return render(request, 'filter_dropdown2.html',context)




class PostCreateView(TemplateView):

    template_name= 'post_form.html'

    def get(self,request):
        form = PostForm()
        posts = Post.objects.all()
        return render(request, self.template_name,{'form':form})

    def post(self, request):
        form = PostForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            # text = form.cleaned_data['post']
            form =  PostForm()
            return redirect('profile')

        args = {'form':form,'text':text}
        return render(request, self.template_name,args)






class PostListView(ListView):
    model = Post
    context_object_name = 'people'


# class PostCreateView(CreateView):
#     model = Post
#     form_class = PostForm
#     success_url = reverse_lazy('post_changelist')


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('post_changelist')


def load_cities(request):
    category_id = request.GET.get('category')
    instances = Instance.objects.filter(category_id=category_id).order_by('title')
    city_id = request.GET.get('city')
    areas = Area.objects.filter(city_id=city_id).order_by('title')
    return render(request, 'city_dropdown_list_options.html', {'areas': areas,'instances':instances})


def load_categories(request):
    category_id = request.GET.get('category')
    instances = Instance.objects.filter(category_id=category_id).order_by('title')
    return render(request, 'category_dropdown_list_options.html', {'instances':instances})






# def product_create_view(request):
#     my_form = RawProductForm()
#     if request.method == "POST":
#         my_form = RawProductForm(request.POST)
#         if my_form.is_valid():
#
#             Post.objects.create(**my_form.cleaned_data)
#
#     context = {
#        "form":my_form,
#     }
#     return render(request, "form_detail1.html",context)




# #
# def register(request):
#
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#
#         if form.is_valid():
#             form.save()
#             phone = form.cleaned_data['phone']
#             password = form.cleaned_data['password1']
#             user = authenticate(username=username, password=password,email=email)
#             login(request, user)
#             return redirect('index')
#     else:
#         form = UserCreationForm()
#
#     context = {'form' : form }
#     return render(request, 'register.html', context)


# def register(request, *args, **kwargs):
#     form  = UserCreationForm(request.POST or None)
#     if form.is_valid():
#         user = form.save()
#         login(request,user)
#         return HttpResponseRedirect('/blog/')
#     context = {
#        'form':form
#     }
#     return render(request, "register.html",context)



# def register(request, *args, **kwargs):
#     form  = UserCreationForm(request.POST or None)
#     if form.is_valid() :
#       phone = form.cleaned_data.get('username')
#       password = form.cleaned_data.get('password1')
#       user = authenticate(username=phone,password=password)
#       if user is not None:
#           if PhoneOTP.objects.filter(phone=phone).exists():
#              login(request,user)
#              return HttpResponseRedirect('/blog/')
#           else:
#               print('user not found')
#     context = {
#        'form':form
#     }
#     return render(request, "register.html",context)
#
#


def register(request):

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            # form.save()
            phone = form.cleaned_data['phone']

            password = form.cleaned_data['password1']
            # user = authenticate(username=phone, password=password)
            if PhoneOTP.objects.filter(phone=phone).exists():
              form.save()
              # login(request,user)
              return HttpResponseRedirect('/login/')

            else:
                 print('user not found')
    else:
      form = UserCreationForm()

    context = {'form' : form }
    return render(request, 'register.html', context)















# def login_view(request):
#     if request.method == "POST":
#        form = AuthenticationForm(data=request.POST)
#        if form.is_valid():
#
#           user = form.get_user()
#           login(request,user)
#           return HttpResponseRedirect('/blog/')
#
#     else:
#        form = AuthenticationForm()


    # context={
    #  'form':form
    #  }
    #
    # return render(request,'login.html',context)



# def login_view(request):
#
#     if request.method == "POST":
#        form = customAuthenticationForm(request.POST)
#
#        if form.is_valid() :
#           phone = form.cleaned_data.get('phone')
#           email = form.cleaned_data.get('email')
#           username = form.cleaned_data.get('username')
#           password = form.cleaned_data.get('password')
#           user = authenticate(username=username,phone = phone,email=email,password=password)
#           if user is not None:
#               # if PhoneOTP.objects.filter(phone=phone).exists():
#              login(request,user)
#              return HttpResponseRedirect('/blog/')
#           else:
#               print('user not found')
#     else:
#        form = customAuthenticationForm()
#     context={
#      'form':form
#      }
#     return render(request,'login.html',context)

def login_view(request, *args, **kwargs):
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        phone = form.cleaned_data.get('query3')
        user_obj = form.cleaned_data.get('user_obj')
        if user_obj is not None:
            if PhoneOTP.objects.filter(phone=phone).exists():
               login(request, user_obj)
               return HttpResponseRedirect("/")
            else:
                 print('user not found')

        else:
               print('user not found')
    return render(request, "login.html",{"form":form})






@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return HttpResponseRedirect('/')




def search(request):
    queryset = Post.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
           Q(title__icontains=query) |
           Q(overview__icontains=query)|
           Q(content__icontains=query)

        ).distinct()
    context = {
        'queryset':queryset,
        'query':query
    }
    return render(request, 'search_results.html', context)




def get_category_count():
    queryset = Post \
       .objects\
       .values('category__title')\
       .annotate(Count('category__title'))
    return queryset



def index(request):
    featured = Post.objects.filter(featured=True)
    latest = Post.objects.order_by('-timestamp')[0:3]
    form = EmailSignupForm()
    if request.method == "POST":
       email = request.POST["email"]
       new_signup = Signup()
       new_signup.email = email
       new_signup.save()

    context = {
     'object_list':featured,
     'latest' :latest,
     'form':form
    }
    return render(request,'index.html', context)


def blog(request):
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post_list =Post.objects.all()
    paginator = Paginator(post_list,4)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger :
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {

    'queryset': paginated_queryset,
    'page_request_var':page_request_var,
    'most_recent':most_recent,
    'category_count':category_count
    }

    return render(request,'blog.html',context)



def post(request,id):
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post = get_object_or_404(Post, id=id)

    form = CommentForm(request.POST or None)
    if request.method == 'POST':
       if form.is_valid():
           form.instance.user = request.user
           form.instance.post = post
           form.save()

    context = {
       'post':post,
       'form':form,
       'most_recent':most_recent,
       'category_count':category_count,

    }
    return render(request,'post.html',context)


def mypost(request,id):
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post = get_object_or_404(Post, id=id)

    form = CommentForm(request.POST or None)
    if request.method == 'POST':
       if form.is_valid():
           form.instance.user = request.user
           form.instance.post = post
           form.save()

    context = {
       'post':post,
       'form':form,
       'most_recent':most_recent,
       'category_count':category_count,

    }
    return render(request,'mypost.html',context)


def city_list(request):
    city_qs = City.objects.all()
    area_qs = Area.objects.all()
    context = {
    'city_qs':city_qs,
    'area_qs':area_qs,
    }

    return render(request, 'city_list.html',context)


# def district_list(request,id):
#     city = get_object_or_404(City,id=id)
#
#     district_qs = city.get_districts.all()
#
#     context={
#     'district_qs':district_qs
#     }
#
#     return render(request, 'district_list.html',context)



def area_list(request,id):
    city = get_object_or_404(City,id=id)
    area_qs = city.get_areas.all()

    context = {
    'area_qs':area_qs
    }

    return render(request,'area_list.html',context)


def area_details(request,id):

    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    area= get_object_or_404(Area,id=id)
    post_list =area.get_posts.all()
    paginator = Paginator(post_list,1)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger :
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {

    'queryset': paginated_queryset,
    'page_request_var':page_request_var,
    'most_recent':most_recent,
    'category_count':category_count
    }

    return render(request,'area_details.html',context)




def city_details(request,id):
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    city = get_object_or_404(City, id=id)
    post_list = city.get_posts.all()
    paginator = Paginator(post_list,4)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger :
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {

    'queryset': paginated_queryset,
    'page_request_var':page_request_var,
    'most_recent':most_recent,
    'category_count':category_count
    }



    return render(request, 'city_detail.html', context)





def category(request):
    category = Category.objects.all()
    instance = Instance.objects.all()

    context={
      'category':category,
      'instance':instance,
    }
    return render(request,'category.html',context)




def instance(request,id):
    category = get_object_or_404(Category,id=id)
    instance = category.get_instances.all()
    context ={
    'instance':instance,
    }
    return render(request,'instance.html',context)


def instance_detail(request,id):
    instance = get_object_or_404 (Instance,id=id)
    post = instance.get_posts.all()
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    # post_list =Post.objects.all()
    instance = get_object_or_404 (Instance,id=id)
    post_list = instance.get_posts.all()
    paginator = Paginator(post_list,1)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger :
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {

    'queryset': paginated_queryset,
    'page_request_var':page_request_var,
    'most_recent':most_recent,
    'category_count':category_count
    }

    return render(request,'instance_detail.html',context)





# def categorydetail(request,id):
#     category_count = get_category_count()
#     most_recent = Post.objects.order_by('-timestamp')[:3]
#     category = get_object_or_404(Category, id=id)
#     category_list = Category.objects.get(id=id)
#     category_list =category.objects.all()
#     paginator = Paginator(category_list,1)
#     page_request_var = 'page'
#     page = request.GET.get(page_request_var)
#     try:
#         paginated_queryset = paginator.page(page)
#     except PageNotAnInteger :
#         paginated_queryset = paginator.page(1)
#     except EmptyPage:
#         paginated_queryset = paginator.page(paginator.num_pages)
#     context = {
#          'queryset':category_list,
#         'queryset': paginated_queryset,
#         'page_request_var':page_request_var,
#         'most_recent':most_recent,
#         'category_count':category_count
#     }
#     return render(request,'category_detail1.html',context)




def categorydetail(request, id):
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    categories  = Category.objects.all()
    post = Post.objects.all()

    category = get_object_or_404(Category, id=id)
    # post = post.filter(category=category)
    posts = category.get_posts.all()
    paginator = Paginator(posts,1)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger :
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
     'categories':categories,
     'post':post,
     'queryset': paginated_queryset,
     'page_request_var':page_request_var,
     'most_recent':most_recent,
     'category_count':category_count
    }

    return render(request,'category_detail.html',context)



@login_required
def profile(request):

    phoneotp = PhoneOTP.objects.filter(phone=request.user.phone)

    if request.method == 'POST':

        # author = Author.objects.filter(request.POST,user=request.user)
        # post_qs = Post.objects.filter(author=author)

        # u_form = UserUpdateForm(request.POST, instance= request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES ,
                           instance=request.user)


        # if u_form.is_valid() and
        if p_form.is_valid() :
           phone = p_form.cleaned_data.get('phone')
           phone_otp = PhoneOTP.objects.filter(phone=phone)
           if phone_otp.exists():
           # u_form.save()
              # p_form.save()
           # messages.success(request,'Your account has been updated!')
              return redirect('/profile/')

           else:
              phoneotp.delete()
              key = random.randint(999, 9999)
              p = PhoneOTP.objects.create(phone=phone,otp=key)
              p_form.save()
    else:
        # u_form = UserUpdateForm(instance= request.user)
        p_form = ProfileUpdateForm(instance=request.user)

    context ={
        # 'u_form':u_form,
        'p_form':p_form,
        # 'post_qs':post_qs,


    }
    return render(request,'profile.html',context)




@login_required
def myuser(request):

    author = Author.objects.all()


    context= {
    'author':author
    }

    return render (request,'myuser.html',context)


# def get_user (request):
#     user_qs = Author.objects.filter(user=request.user)
#     if user_qs.exists():
#         return user_qs.first()
#     return None

@login_required()
def mypage(request):

    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post = Post.objects.filter(user=request.user)

    paginator = Paginator(post,4)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger :
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        # 'queryset':post_qs,
        'queryset': paginated_queryset,
        'page_request_var':page_request_var,
        'most_recent':most_recent,
        'category_count':category_count
    }
    return render(request,'mypage.html',context)



@login_required()
def post_update(request, id):
    instance = get_object_or_404(Post, id=id)
    form = PostForm(request.POST or None, request.FILES or None,instance=instance )

    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()

        return HttpResponseRedirect('/profile/')

    context = {
            'form':form,
            'instance':instance,

            }
    return render(request,'form_detail.html',context)





# UserPassesTestMixin
# class PostDeleteView( LoginRequiredMixin,  DeleteView):
#     model = Post
#     success_url='/'
#     template_name = 'post_confirm_delete.html'
#
#     def test_func(self):
#         post = self.get_object()
#         if self.request.user == post.author:
#             return True
#         return False


#
@login_required()
def post_delete(request, id=None):
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect("profile")


def default_map(request):

    mapbox_access_token = 'pk.my_mapbox_access_token'

    return render(request, 'default.html',
     {'mapbox_access_token' : mapbox_access_token} )
