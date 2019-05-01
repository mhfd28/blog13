from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.urls import reverse
from tinymce import HTMLField
from PIL import Image
from localflavor.br.br_states import STATE_CHOICES
import random
# User = get_user_model()
from django.contrib.auth.models import (
    AbstractBaseUser,BaseUserManager
   )
USERNAME_REGEX = '^[a-zA-Z0-9.+-]*$'

class UserManager(BaseUserManager):
    def create_user(self,username,email, phone, password=None, is_staff = False, is_active=True, is_admin=False):

        if not username:
            raise ValueError('Users must have an email address')
        if not email:
            raise ValueError('Users must have an email address')

        if not phone:
            raise ValueError('users must have a phone number')

        user  = self.model(
             username = username,
             email = self.normalize_email(email),
             phone=phone
        )
        user.set_password(password)
        user.staff = is_staff
        user.admin = is_admin
        user.active = is_active
        user.save(using = self._db)
        return user

    # def create_staffuser(self, phone,username, email, password=None):
    #     user = self.create_user(
    #      phone,
    #      username,
    #      email,
    #      password=password,
    #      is_staff = True,
    #     )
    #     return user

    # def create_superuser(self,username,email,password=None):
    #     user = self.create_user(username,email,password=password)
    #     user.is_admin = True
    #     user.is_staff = True
    #     user.save(using=self._db)
    #     return user

    def create_superuser(self,username, password=None, is_staff = True, is_active=True, is_admin=True):

        # if not email:
        #     raise ValueError('Users must have an email address')

        # if not phone:
        #     raise ValueError('users must have a phone number')

        user  = self.model(
             username = username,
             # email = self.normalize_email(email),
             # phone=phone
        )
        user.set_password(password)
        user.staff = is_staff
        user.admin = is_admin
        user.active = is_active
        user.save(using = self._db)
        return user

class User(AbstractBaseUser):
    username = models.CharField(
                     max_length=300,
                     validators =[
                        RegexValidator(regex = USERNAME_REGEX,
                                         message = 'Username must be alphanumeric or contain numbers',
                                         code = 'invalid_username'
                              )],
                     unique = True
                )
    email = models.EmailField(
            max_length=255,
            unique=True,
            verbose_name='email address'
       )
    phone_regex = RegexValidator(regex  =r'^\+?1?\d{9,14}$',
      message = "phone number must be in format: '+9999999'")
    phone = models.CharField(validators=[phone_regex], max_length = 15,unique = True)
    # name   = models.CharField(max_length=20, blank=True,null=True)
    first_login = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    staff  =models.BooleanField(default =False)
    admin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELD = ['email']

    objects = UserManager()

    def __str__(self):
        return self.username

    # def get_username():
    #     return self.username


    def get_full_name(self):

           return self.username


    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active

    # def get_absolute_url(self):
    #
    #     return reverse("mypage",
    #         kwargs={
    #         'id':self.id
    #     })
    #
    # @property
    # def get_posts(self):
    #     return self.posts.all()




MEMBERSHIP_CHOICES = (
('Enterprise','ent'),
('Professional','pro'),
('Free','free')
)



class Membership(models.Model):

   slug = models.SlugField()
   membership_type = models.CharField(
   choices=MEMBERSHIP_CHOICES,
   default='Free',
   max_length=30)
   price = models.IntegerField(default=15)
   plan_id = models.CharField(max_length=40)

   def __str__(self):
       return self.membership_type

class UserMembership(models.Model):

   user = models.ForeignKey(User,on_delete=models.SET_NULL ,blank=True,null=True)
   customer_id = models.CharField(max_length=40)
   membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True)

   def __str__(self):
       return self.user.username

def post_save_usermembership_create(sender,instance,created, *args, **kwargs):
       if created:

          UserMembership.objects.get_or_create(user = instance)
          user_membership, created = UserMembership.objects.get_or_create(user = instance)
          if user_membership.customer_id is None or user_membership.customer_id == '':

             new_customer_id =random.randint(999, 9999)

             user_membership.customer_id = new_customer_id
             user_membership.save()

post_save.connect(post_save_usermembership_create, sender=settings.AUTH_USER_MODEL)

class Subscription (models.Model):

   user_membership = models.ForeignKey(UserMembership,on_delete=models.CASCADE)
   subscription_id = models.CharField(max_length=40)
   active = models.BooleanField(default=True)

   def __str__(self):
       return self.user_membership.user.username





class PhoneOTP(models.Model):
    phone_regex = RegexValidator(regex = r'^\+?1?\d{9,14}$',message="Phone number must be enter")
    phone       = models.CharField(validators=[phone_regex], max_length=17,unique=True)
    otp         = models.CharField(max_length= 9 ,blank=True,null=True)
    count       = models.IntegerField(default =0,help_text = 'Number of otp sent')
    # logged      = models.BooleanField(default = False,help_text = 'if otp verification got successful')
    # forgot      = models.BooleanField(default = False,help_text = 'only true for forgot password ')
    # forgot_logged      = models.BooleanField(default = False,help_text = 'only true if validdate otp forgot get ')

    def __str__(self):
        return str(self.phone) + 'is sent' + str(self.otp)







class Author(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,default=1, on_delete=models.SET_NULL ,blank=True,null=True)
    profile_picture = models.ImageField()
    email = models.EmailField()
    # user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    # user = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):

        return reverse("mypage",
        kwargs={
        'id':self.id
        })

    @property
    def get_posts(self):
        return self.posts.all()


# @receiver(post_save, sender=User)
# def author_qs(sender,**kwargs):
#     if kwargs.get('created',False):
#         Author.objects.create(user=kwargs.get('instance'))


class Category(models.Model):
    title = models.CharField(max_length = 50)

    def __str__(self):
        return self.title


    def get_absolute_url(self):

        return reverse("category-detail",
        kwargs={
        'id':self.id
        })

    # def get_absolute_url(self):
    #
    #     return reverse("product_create_view",
    #     kwargs={
    #     'id':self.id
    #     })


    @property
    def get_posts(self):
        return self.posts.all()

    @property
    def get_instances(self):
        return self.instances.all()



class Instance(models.Model):
    title = models.CharField(max_length=100)
    # category = models.ManyToManyField(Category)
    category = models.ForeignKey(Category, related_name='instances', on_delete= models.CASCADE)

    def __str__(self):
        return self.title


    def get_absolute_url(self):

        return reverse("instance-detail",
        kwargs={
        'id':self.id
        })

    @property
    def get_posts(self):
        return self.posts.all()



class City(models.Model):
    title = models.CharField(max_length=50)
    # uf = models.CharField('UF', max_length=2, choices=STATE_CHOICES)

    def __str__(self):
        return self.title

# class Meta:
#     ordering = ('title',)
#     verbose_name = 'city'
#     verbose_name_plural = 'cities'





    @property
    def get_posts(self):
        return self.posts.all()


    @property
    def get_areas(self):
        return self.areas.all()



    def get_absolute_url(self):

        return reverse('area-list', kwargs={

         'id':self.id })





class Area(models.Model):
    title = models.CharField(max_length=50)
    city = models.ForeignKey(City, related_name='areas', on_delete= models.CASCADE)


    def __str__(self):
        return self.title

    @property
    def get_posts(self):
        return self.posts.all()


    def get_absolute_url(self):

        return reverse('area-details', kwargs={

         'id':self.id })





class Post(models.Model):
    # user = models.ForeignKey(settings.AUTH_USER_MODEL,default=1 ,on_delete=models.SET_NULL ,blank=True,null=True)
    user = models.ForeignKey(User,on_delete=models.SET_NULL ,blank=True,null=True)

    title = models.CharField(max_length=30)
    # instance = models.ManyToManyField(Instance)
    instance = models.ForeignKey(Instance, related_name='posts',on_delete=models.SET_NULL , null=True, blank=True)
    # overview = models.TextField()
    # city = models.ForeignKey(City, on_delete=models.CASCADE)
    city = models.ForeignKey(City, related_name='posts',on_delete=models.SET_NULL , null=True, blank=True)
    # district = models.ForeignKey(District,on_delete=models.CASCADE)
    # district = models.ForeignKey(District, related_name='posts', on_delete= models.CASCADE)
    # area = models.ForeignKey(Area,on_delete=models.CASCADE)
    area = models.ForeignKey(Area, related_name='posts',on_delete=models.SET_NULL , null=True, blank=True)
    address = models.TextField(max_length = 300)
    comment_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default = 0)
    content = HTMLField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # author = models.ForeignKey(Author,on_delete=models.CASCADE)
    # author = models.ManyToManyField (Author)
    # author = models.ForeignKey(Author,related_name='posts', on_delete=models.SET_NULL , null=True, blank=True)
    # phone = models.IntegerField(max_length=11,null=True)
    email = models.EmailField()
    thumbnail = models.ImageField(null=True, blank=True)
    # categoreis = models.ManyToManyField(Category)
    category = models.ForeignKey(Category, related_name='posts', on_delete=models.SET_NULL , null=True, blank=True)
    featured = models.BooleanField(default=False)
    previous_post = models.ForeignKey('self',related_name = 'Previous' ,on_delete=models.SET_NULL , null=True, blank=True)
    next_post = models.ForeignKey('self',related_name = 'next' ,on_delete=models.SET_NULL , null=True, blank=True)



    def __str__(self):

        return self.title


    def get_absolute_url(self):

        return reverse("post-detail", kwargs ={
        'id':self.id
        # 'pk':self.pk
        })

    @property
    def get_comments(self):
        return self.comments.all()






# def post_qs(sender, instance, created, *args, **kwargs):
#     if created:
#         Post.objects.get_or_create(user=instance)
#
#     post, created = Post.objects.get_or_create(user=instance)
#     post.save()
#
# post_save.connect(post_qs, sender=settings.AUTH_USER_MODEL)


class Comment(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    post = models.ForeignKey(Post, related_name='comments', on_delete= models.CASCADE)

    def __str__(self):
        return self.user.username
