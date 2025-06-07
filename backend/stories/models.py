from django.db import models
from django_jalali.db import models as jmodels
from collections import Counter
from django.core.validators import MinLengthValidator
import jdatetime
from django.utils import timezone

GENDER_CHOICES = [
    ('male', 'آقا'),
    ('female', 'خانم'),
    ('other', 'نامشخص'),
]

POLITICAL_ORIENTATION_CHOICES = [
    ('osolgara', 'اصولگرا'),
    ('eslahtalab', 'اصلاح طلب'),
    ('moanedam', 'معاند عام'),
    ('saltanattalab', 'سلطنت طلب'),
    ('monafegh', 'منافق'),
    ('taghribanhamso', 'تقریبا همسو'),
    ('taghribannahamso', 'تقریبا ناهمسو'),
]

ORIENTATION_CHOICES = [
    ('ekhlalgar', 'اخلالگر'),
    ('khakestari', 'خاکستری'),
    ('hamso', 'همسو (ارزشی)'),
]

LOCATION = [
    ('in', 'داخل'),
    ('out', 'خارج'),
    ('other', 'نامشخص'),

]


class Category(models.Model):
    name = models.CharField(max_length=20, verbose_name='نام دسته')
    category_image = models.ImageField(upload_to='category_images/', blank=True, null=True, verbose_name='تصویر دسته')

    class Meta:
        verbose_name = 'دسته'
        verbose_name_plural = 'دسته ها'

    def __str__(self):
        return self.name


class Feeling(models.TextChoices):
    HAPPY = 'شاد', 'شاد'
    SAD = 'غمگین', 'غمگین'
    ANGRY = 'عصبانی', 'عصبانی'
    CALM = 'آرام', 'آرام'
    EXCITED = 'هیجان‌زده', 'هیجان‌زده'


class Tone(models.TextChoices):
    FORMAL = 'رسمی', 'رسمی'
    INFORMAL = 'غیررسمی', 'غیررسمی'
    FRIENDLY = 'دوستانه', 'دوستانه'
    AUTHORITATIVE = 'مقتدرانه', 'مقتدرانه'
    SARCASM = 'کنایی', 'کنایی'


class Ironic(models.TextChoices):
    YES = 'همسو', 'همسو'
    NO = 'ناهمسو', 'ناهمسو'
    SOMEWHAT = 'نامشخص', 'نامشخص'


class StoryType(models.TextChoices):
    Image = 'عکس', 'عکس'
    Video = 'ویدئو', 'ویدئو'
    Text = 'متن', 'متن'


class SubTopic(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام زیرموضوع')

    class Meta:
        verbose_name = 'زیر موضوع'
        verbose_name_plural = 'زیر موضوع'

    def __str__(self):
        return self.name


class Topic(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام موضوع')
    sub_topics = models.ManyToManyField(SubTopic, blank=True, verbose_name='زیرموضوع‌ها')
    icon = models.ImageField(upload_to='topic/', verbose_name='آیکون')

    class Meta:
        verbose_name = 'موضوع'
        verbose_name_plural = 'موضوعات'

    def __str__(self):
        return self.name


class InstagramPage(models.Model):
    # اطلاعات پایه
    page = models.CharField(max_length=100, verbose_name='نام صفحه')
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[MinLengthValidator(3)],
        verbose_name='نام کاربری'
    )
    bio = models.TextField(max_length=500, blank=True, verbose_name='بیوگرافی')
    profile_image = models.ImageField(upload_to='instagram_pages/', blank=True, null=True, verbose_name='تصویر پروفایل')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='موضوع',
                              related_name='instagrampage')
    sub_topic = models.ForeignKey(SubTopic, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='زیرموضوع')
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='unknown',
        verbose_name='جنسیت',
        null=True,
        blank=True
    )

    political_orientation = models.CharField(
        max_length=20,
        choices=POLITICAL_ORIENTATION_CHOICES,
        default='unknown',
        verbose_name='گرایش سیاسی',
        null=True,
        blank=True
    )

    orientation = models.CharField(
        max_length=20,
        choices=ORIENTATION_CHOICES,
        default='unknown',
        verbose_name='گرایش',
        null=True,
        blank=True
    )

    location = models.CharField(
        max_length=20,
        choices=LOCATION,
        default='unknown',
        verbose_name='موقعیت',
        null=True,
        blank=True
    )
    # آمارها
    followers_count = models.PositiveIntegerField(default=0, verbose_name='تعداد دنبال‌کنندگان')
    following_count = models.PositiveIntegerField(default=0, verbose_name='تعداد دنبال‌شوندگان')
    posts_count = models.PositiveIntegerField(default=0, verbose_name='تعداد پست‌ها')
    average_likes = models.PositiveIntegerField(default=0, verbose_name='میانگین لایک')
    average_comments = models.PositiveIntegerField(default=0, verbose_name='میانگین کامنت')
    is_verified = models.BooleanField(default=False, verbose_name='تایید شده')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='دسته')

    class Meta:
        verbose_name = 'صفحه اینستاگرام'
        verbose_name_plural = 'صفحات اینستاگرام'
        ordering = ['-followers_count']

    def __str__(self):
        return f"{self.page} (@{self.username})"


class StoryModel(models.Model):
    title = models.CharField(max_length=100, verbose_name='عنوان')
    page = models.ForeignKey(InstagramPage, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='صفحه')
    # page = models.CharField(max_length=20, verbose_name='کاربر')
    story = models.FileField(upload_to='images/', verbose_name='استوری')
    # topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='موضوع', related_name='storymodel')
    # sub_topic = models.ForeignKey(SubTopic, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='زیرموضوع')
    feeling = models.CharField(max_length=20, choices=Feeling.choices, verbose_name='احساس')
    ironic = models.CharField(max_length=10, choices=Ironic.choices, verbose_name='رویکرد')
    tone = models.CharField(max_length=20, choices=Tone.choices, verbose_name='لحن')
    description = models.TextField(max_length=100, verbose_name='توضیحات', null=True, blank=True)
    story_text = models.TextField(max_length=250, verbose_name='متن استوری', null=True, blank=True)
    story_type = models.CharField(max_length=20, choices=StoryType.choices, verbose_name='جنس استوری')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='دسته')

    @classmethod
    def get_top_tags_from_queryset(cls, queryset, limit=20):
        # استخراج تگ‌ها از عنوان‌های کوئری‌ست فیلتر شده
        titles = queryset.values_list('title', flat=True)

        tags = []
        for title in titles:
            if title:
                tags.extend([tag.strip() for tag in title.split('،') if tag.strip()])

        tag_counter = Counter(tags)
        top_tags = tag_counter.most_common(limit)

        return [{'name': tag, 'weight': count} for tag, count in top_tags]

    @classmethod
    def get_text_from_queryset(cls, queryset, limit=20):
        # استخراج تگ‌ها از عنوان‌های کوئری‌ست فیلتر شده
        texts = queryset.values_list('story_text', flat=True)

        tags = []
        for title in texts:
            if title:
                tags.extend([tag.strip() for tag in title.split(' ') if tag.strip()])

        tag_counter = Counter(tags)
        top_tags = tag_counter.most_common(limit)

        return [{'name': tag, 'weight': count} for tag, count in top_tags]

    class Meta:
        verbose_name = 'صفحه استوری'
        verbose_name_plural = 'صفحات استوری'

    def __str__(self):
        return self.title


class DayAnalysis(models.Model):
    text = models.TextField(verbose_name="متن")
    jalali_date = models.DateField(verbose_name="تاریخ جلالی", default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_jalali_date(self):
        """تبدیل تاریخ میلادی به جلالی برای نمایش"""
        gregorian_date = self.jalali_date
        jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
        return jalali_date.strftime('%Y/%m/%d')

    def __str__(self):
        return f"{self.text} - {self.get_jalali_date()}"

    class Meta:
        verbose_name = "تحلیل"
        verbose_name_plural = "تحلیل"
