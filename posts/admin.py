from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserCreationForm,UserAdminCreationForm,UserAdminChangeForm
from .models import Post,Category,Comment,Instance,\
Area,City,Author,PhoneOTP,User,UserMembership,Membership,Subscription

class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = ('username','phone','email','admin',)
    list_filter = ('staff','active','admin',)
    fieldsets = (
       (None,{'fields':('phone','email','password',)}),
       ('Personal info',{'fields':('username',)}),
       ('permissions',{'fields': ('admin','staff','active')}),
    )

    add_fieldsets = (
         (None, {
              'classes':('wide',),
              'fields':('phone','username','email', 'password1','password2')}

         ),
    )

    search_fields = ('phone','email','username')
    ordering = ('phone','email','username')
    filter_horizontal = ()

    def get_inline_instances(self, request,obj=None):
        if not obj:
            return list()
        return super(UserAdmin,self).get_inline_instances(request, obj)

admin.site.register(User,UserAdmin)

admin.site.register(Post)
admin.site.register(PhoneOTP)
admin.site.register(City)
admin.site.register(Author)
admin.site.register(Area)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Instance)
admin.site.register(UserMembership)
admin.site.register(Membership)
admin.site.register(Subscription)






# @admin.register(City)
# class CityAdmin(admin.ModelAdmin):
#     list_display = ('__str__', 'title')
#     search_fields = ('title', )
#     list_filter = ('title',)
#
#
# @admin.register(Area)
# class AreaAdmin(admin.ModelAdmin):
#     list_display = ('__str__', 'city')
#     search_fields = ('title', 'city__name')
#     list_filter = ('city',)
