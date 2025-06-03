from django.contrib import admin
# from django_jalali.admin import JalaliDateFieldListFilter
from .models import StoryModel, Topic, SubTopic, InstagramPage, Category, DayAnalysis


@admin.register(StoryModel)
class StoryModelAdmin(admin.ModelAdmin):
    list_display = ('page', 'created_at', 'feeling', 'tone')
    list_filter = (
        'created_at',  # فیلتر تاریخ جلالی
        'feeling',
        'tone',
        'ironic'
    )
    search_fields = ('description', 'user__username')


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('sub_topics',)


@admin.register(Category)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name',)
    # filter_horizontal = ('name',)


@admin.register(SubTopic)
class SubTopicAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(InstagramPage)
class InstagramPageAdmin(admin.ModelAdmin):
    list_display = ('page', 'username', 'followers_count', 'is_verified', 'is_active', 'topic', 'sub_topic','category')
    list_filter = (
        'is_verified',
        'is_active',
        'created_at',
    )
    search_fields = ('page', 'username', 'bio')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('اطلاعات پایه', {
            'fields': ('page', 'username', 'bio', 'profile_image', 'topic', 'sub_topic', 'category')
        }),
        # ('لینک‌ها', {
        #     'fields': ('website_url', 'instagram_url'),
        #     'classes': ('collapse',)
        # }),
        ('آمار', {
            'fields': ('followers_count', 'following_count', 'posts_count', 'average_likes', 'average_comments'),
        }),
        # ('مدیریت', {
        #     'fields': ('owner', 'is_verified', 'is_active'),
        # }),
        # ('تاریخ‌ها', {
        #     'fields': ('created_at', 'updated_at'),
        #     'classes': ('collapse',)
        # }),
    )
    # inlines = [PageStatisticInline]
    actions = ['mark_as_verified', 'mark_as_unverified']

    def mark_as_verified(self, request, queryset):
        queryset.update(is_verified=True)
    mark_as_verified.short_description = "تایید صفحات انتخاب شده"

    def mark_as_unverified(self, request, queryset):
        queryset.update(is_verified=False)
    mark_as_unverified.short_description = "لغو تایید صفحات انتخاب شده"


@admin.register(DayAnalysis)
class DayAnalysisAdmin(admin.ModelAdmin):
    list_display = ('text', 'get_jalali_date_display')
    search_fields = ('text',)

    def get_jalali_date_display(self, obj):
        return obj.get_jalali_date()

    get_jalali_date_display.short_description = 'تاریخ جلالی'