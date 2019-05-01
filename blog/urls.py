
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from marketing.views import email_list_signup
from django.contrib.auth import views as auth_views
from posts.views import search,blog,post \
,index,mypage,post_delete,post_update,category,categorydetail,\
instance,instance_detail,city_list,default_map,\
area_list,area_details,register,logout_view,myuser,send_otp_this,otp_match,\
login_view,send_email,filter_dropdown2,PostListView,PostUpdateView,PostCreateView,\
load_cities,load_categories,mypost,profile,MembershipSelectView,\
PaymentView,updateTransactions


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index,name="index"),
    path('sms/', send_otp_this,name="sms"),
    path('otp-match/',otp_match,name='otp-match'),
    path('login/',login_view,name = "login"),
    path('logout/',logout_view,name = "logout"),
    path('blog/', blog, name = 'post-list'),
    path('post/<id>/', post,name='post-detail'),
    path('post/<id>/mypost', mypost,name='mypost'),
    path('post/<id>/update/', post_update ,name='post-update'),
    path('post/<id>/delete/', post_delete ,name='post-delete'),
    path('category/',category,name='category-list'),
    path('city-list/',city_list,name='city-list'),
    # path('district-list/<id>/',district_list,name='district-list'),
    path('area-list/<id>/',area_list,name='area-list'),
    path('area-details/<id>/',area_details,name='area-details'),
    # path('city-details/<id>/',city_details,name='city-details'),
    path('map/',default_map,name='default_map'),
    # path('district-details/<id>/',district_details,name='district-details'),
    # path('category/<id>/',categorydetail,name='category-detail'),
    path('category/<id>/',instance,name='category-detail'),
    # path('instance/<id>/',instance,name='instance'),
    path('instancedetail/<id>/',instance_detail,name='instance-detail'),
    # path('accounts/',include('django.contrib.auth.urls')),
    # path('accounts/password_reset/',password_reset,name='password_reset'),
    # path('accounts/password_reset_done/',password_reset_done,name='password_reset_done'),

    path('profile/',profile,name='profile'),
    path('mypage/',mypage,name='mypage'),
    path('myuser/',myuser,name='myuser'),
    path('register/', register, name='register'),
    # path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('search/', search,name='search'),
    path('subscribe/', email_list_signup, name='subscribe'),
    path('tinymce/', include('tinymce.urls')),
    # path('post/',product_create_view, name = 'product_create_view'),
    path('send/', send_email,name='send_email'),
    path('filter_dropdown2/', filter_dropdown2, name='filter_dropdown2'),

    path('', PostListView.as_view(), name='post_changelist'),
    path('post/', PostCreateView.as_view(), name='post_add'),
    path('<int:pk>/', PostUpdateView.as_view(), name='post_change'),
    path('ajax/load-cities/', load_cities, name='ajax_load_cities'),
    path('ajax/load-categories/', load_categories, name='ajax_load_categories'),
    path('membership/', MembershipSelectView.as_view(), name='select'),
    path('payment/', PaymentView, name='payment' ),
    path('update-transactions/<subscription_id >/', updateTransactions, name = 'update-transactions'),
]



if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
