from django import forms
from tinymce import TinyMCE
from .models import Post, Comment,PhoneOTP,User,Instance,Category,City,Area,\
UserMembership,Membership

from django.db.models import Q
# from django.contrib.auth.models import User
# from django.contrib.auth import get_user_model
from django.contrib.auth.forms import  UserCreationForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import AuthenticationForm
from localflavor.br.br_states import STATE_CHOICES
from django.forms import ModelChoiceField


# User = get_user_model

class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required': False, 'cols': 30, 'rows': 10}
        )
    )

    class Meta:
        model = Post
        fields = ('title', 'content', 'thumbnail',
        'category', 'featured', 'previous_post', 'next_post')

class CommentForm(forms.ModelForm):
    content = forms.CharField(widget =forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Type your comment',
        'id':'usercomment',
        'rows':'4',

    }))

    class Meta:
       model = Comment
       fields = ('content', )






class SubscriptionForm(forms.Form):

    membership = forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=[])




    # class Meta:
    #     model = UserMembership
    #     fields = ('membership',)

    def __init__(self, *args, **kwargs):
        super(UsermemForm, self).__init__(*args, **kwargs)
        unique_memberships = Membership.objects.values_list('membership_type',flat=True).distinct()
        self.fields['membership'].choices = [(membership_type,membership_type) for membership_type in unique_memberships]








class ProductForm(forms.Form):


    city = forms.ModelChoiceField(
        queryset=City.objects.none(),
        required=False
    )
    area = forms.ModelChoiceField(
        queryset=Area.objects.none(),
        required=False
    )

    title = forms.CharField(label= 'title',required=False,
             widget=forms.TextInput(attrs={"placeholder":"your title"}))
    address   = forms.CharField(required=False)
    thumbnail = forms.ImageField(required=False)
    content = forms.CharField(
                       required = False,
                       widget=forms.Textarea(
                              attrs={
                                  'class': 'form-control',
                                  "placeholder": "your content",
                                  "class":"new-class-name tow",
                                  "id":"test",
                                  "row":20,
                                  'cols':45,
                              }
                            )
                      )


    # def __init__(self,category,*args,**kwargs):
          # super(ProductForm,self).__init__(*args,**kwargs)
          # self.fields['instance'].queryset = Instance.objects.filter(category=category)
          # self.fields['post'].queryset = Post.objects.filter(category=category)


    class Meta:
        # model=Post
        fields=(
                'title',
                'content',
                'thumbnail',
                'address'  ,
                # 'instance',
                # 'category',
                # 'city',
                # 'area',
                  )


    def __init__(self,  city=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].queryset = City.objects.all()
        if city:
            self.fields['area'].queryset = Area.objects.filter(
                city=city)




class PostForm(forms.ModelForm):

    title = forms.CharField(label= 'title',required=False,
             widget=forms.TextInput(attrs={"placeholder":"your title"}))
    address   = forms.CharField(required=False)
    thumbnail = forms.ImageField(required=False)
    content = forms.CharField(
                       required = False,
                       widget=forms.Textarea(
                              attrs={
                                  'class': 'form-control',
                                  "placeholder": "your content",
                                  "class":"new-class-name tow",
                                  "id":"test",
                                  "row":20,
                                  'cols':45,
                              }
                            )
                      )



    class Meta:
        model = Post
        fields = ('city','area','category','instance','title', 'address','content','thumbnail'  )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['area'].queryset = Area.objects.none()
        self.fields['instance'].queryset = Instance.objects.none()

        if 'city' in self.data:
            try:
                city_id = int(self.data.get('city'))
                self.fields['area'].queryset = Area.objects.filter(city_id=city_id).order_by('title')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        # elif self.instance.pk:
        #     self.fields['area'].queryset = self.instance.city.area_set.order_by('title')

        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['instance'].queryset = Instance.objects.filter(category_id=category_id).order_by('title')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        # elif self.instance.pk:
        #     self.fields['instance'].queryset = self.instance.category.instance_set.order_by('title')








class RawProductForm(forms.Form):
    title  = forms.CharField()
    instance = forms.CharField()
    content = forms.CharField(
                       required = False,
                       widget=forms.Textarea(
                              attrs={
                                  "placeholder": "your description",
                                  "class":"new-class-name tow",
                                  "id":"test",
                                  "row":20,
                                  'cols':120
                              }
                            )
                       )

    city = forms.CharField()
    area = forms.CharField()
    address = forms.CharField()
    # author  = forms.CharField()
    thumbnail = forms.ImageField(required=False)
    categoreis = forms.CharField()


class UserCreationForm(forms.ModelForm):
    password1  = forms.CharField(label='password',widget=forms.PasswordInput)
    password2  = forms.CharField(label='password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['phone','email','username']

    def clean_password(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and pasword2 and password1  != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2


    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user



# class UserLoginForm(forms.Form):
#         query = forms.CharField(label='Username / Email')
#         password = forms.CharField(label = 'password', widget=forms.PasswordInput)
#
#         def clean(self, *args, **kwargs):
#             query = self.cleaned_data.get('query')
#             password = self.cleaned_data.get('password')
#             user_qs_final = User.objects.filter(
#                       Q(username__iexact=query) |
#                       Q(email__iexact=query)
#                 ).distinct()
#             if not user_qs_final.exists() and user_qs_final.count != 1:
#                 raise forms.ValidationError("Invalid credential - user does note exist")
#             user_obj = user_qs_final.first()
#             if not user_obj.check_password(password):
#                 raise forms.ValidationError("credentials are not correct")
#             self.cleaned_data["user_obj"] = user_obj
#             return super (UserLoginForm, self).clean(*args, **kwargs)




# class UserRegisterForm(UserCreationForm):
#
#
#     class Meta:
#         model = User
#         fields = ['phone', 'password1', 'password2']
# class RegisterForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput)
#     password2 = forms.CharField(label='Confirm password' ,widget = forms.PasswordInput)
#
#     class Meta:
#         model = User
#         fields = ('phone')
#
#     def clean_phone(self):
#         phone = self.cleaned_data.get('phone')
#         qs = User.objects.filter(phone=phone)
#         if qs.exists():
#             raise forms.ValidationError(" phone is taken")
#         return phone
#
#     def clean_password2(self):
#         password1 = self.cleaned_data.get('password1')
#         password2 = self.clean_data.get("password2")
#         if password1 and password2 and password1 != password2:
#            raise forms.ValidationError("Passwords don't match")
#         return password2


#
# class UserUpdateForm(forms.ModelForm):
#      # phone = forms.IntegerField()
#
#     class Meta:
#         model = User
#         fields = ['password', 'phone']

class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model= User
        fields = ['phone']


class OTPFormMatch(forms.Form):

    phone = forms.IntegerField()
    otp = forms.IntegerField()


class OTPForm(forms.ModelForm):

    class Meta:
        model = PhoneOTP
        fields = ['phone']


class UserAdminCreationForm(forms.ModelForm):

    password1 = forms.CharField(label = 'password',widget=forms.PasswordInput)
    password2 = forms.CharField(label = 'password confirmation', widget =forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone','email')


    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
           raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(UserAdminCreationForm,self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('phone', 'password', 'active', 'admin')

    def clean_password(self):

        return self.initial["password"]


class customAuthenticationForm(forms.ModelForm):
    # def confirm_login_allowed(self,user):
    #     if not user.is_active or not user.is_validated:
    #         raise forms.ValidationError('there was a problem with your login', code='invalid_login')

    class Meta:
            model = User
            fields = ('phone', 'username', 'email','password')


class UserLoginForm(forms.Form):
        # query1 = forms.CharField(label='Username ')
        # query2 = forms.CharField(label=' Email')
        query3 = forms.CharField(label='Phone')

        password = forms.CharField(label = 'password', widget=forms.PasswordInput)

        def clean(self, *args, **kwargs):
            # query1 = self.cleaned_data.get('query1')
            # query2 = self.cleaned_data.get('query2')
            query3 = self.cleaned_data.get('query3')
            password = self.cleaned_data.get('password')
            user_qs_final = User.objects.filter(
                      # Q(username__iexact=query1) |
                      # Q(email__iexact=query2)|
                      Q(phone__iexact=query3)
                ).distinct()
            if not user_qs_final.exists() and user_qs_final.count != 1:
                raise forms.ValidationError("Invalid credential - user does note exist")
            user_obj = user_qs_final.first()
            if not user_obj.check_password(password):
                raise forms.ValidationError("credentials are not correct")
            self.cleaned_data["user_obj"] = user_obj
            return super (UserLoginForm, self).clean(*args, **kwargs)
