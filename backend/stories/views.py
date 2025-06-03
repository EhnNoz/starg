from datetime import timedelta
import jdatetime
from django.db.models import Count, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import StoryModel, Topic, InstagramPage, Category, DayAnalysis
from .serializers import StoryModelSerializer, TopicSerializer, StoryStatsSerializer, InstagramPageSerializer, \
    CategorySerializer, DayAnalysisSerializer
from rest_framework import filters
from collections import defaultdict


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

    def get_queryset(self):
        days = self.request.query_params.get('days')
        queryset = Topic.objects.all()

        if days is not None and days.isdigit():
            date_threshold = timezone.now() - timedelta(days=int(days))
            queryset = queryset.annotate(
                story_count=Count(
                    'instagrampage__storymodel',
                    filter=Q(instagrampage__storymodel__created_at__gte=date_threshold)
                )
            )
            # queryset = queryset.filter(instagrampage__storymodel__created_at__gte=date_threshold).distinct()

        return queryset

    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['topic', 'page']
    # permission_classes = [IsAuthenticatedOrReadOnly]


class StoryModelViewSet(viewsets.ModelViewSet):
    queryset = StoryModel.objects.all()
    serializer_class = StoryModelSerializer
    filter_backends = [filters.SearchFilter]
    # filterset_fields = ['top', 'in_stock']
    search_fields = ['title', 'story_text']

    def get_queryset(self):
        queryset = self.serializer_class.Meta.model.objects.all()

        # # 1. search
        # search_term = self.request.query_params.get('search')
        # if search_term:
        #     queryset = queryset.filter(
        #         Q(title__icontains=search_term) |
        #         Q(text__icontains=search_term)
        #     )

        # 2. topic_id
        topic_id = self.request.query_params.get('topic_id')
        if topic_id and topic_id.isdigit():
            queryset = queryset.filter(page__topic_id=int(topic_id))

        # 3. page_id
        page_id = self.request.query_params.get('page_id')
        if page_id and page_id.isdigit():
            queryset = queryset.filter(page_id=int(page_id))

        # 4. days
        days = self.request.query_params.get('days')
        if days and days.isdigit():
            date_threshold = timezone.now() - timedelta(days=int(days))
            queryset = queryset.filter(created_at__gte=date_threshold)

        return queryset

    # permission_classes = [IsAccountAdminOrReadOnly]


class StateStoryModelViewSet(viewsets.ModelViewSet):
    queryset = StoryModel.objects.all()
    serializer_class = StoryModelSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'story_text']

    # permission_classes = [IsAuthenticatedOrReadOnly]

    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user)

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        queryset = StoryModel.objects.all()

        # دسترسی به پارامتر search از URL
        search_term = request.query_params.get('search', None)

        if search_term:
            queryset = queryset.filter(
                Q(title__icontains=search_term) |
                Q(story_text__icontains=search_term)
            )

        topic_id = request.query_params.get('topic_id')
        if topic_id:
            queryset = queryset.filter(page__topic=topic_id)

        # فیلتر page
        page_id = self.request.query_params.get('page_id')
        if page_id:
            queryset = queryset.filter(page__id=page_id)

        days = self.request.query_params.get('days', None)
        # queryset = self.filter_queryset(self.get_queryset())
        if days:
            try:
                days = int(days)
                date_threshold = timezone.now() - timedelta(days=days)
                queryset = queryset.filter(created_at__gte=date_threshold)
            except ValueError:
                return Response(
                    {'error': 'پارامتر days باید یک عدد صحیح باشد'},
                    status=400
                )

        # آمار کلی
        total_count = queryset.count()

        page_count = InstagramPage.objects.all().count()
        # published_count = StoryModel.objects.filter(status='created_at').count()
        # draft_count = StoryModel.objects.filter(status='draft').count()

        # روند روزانه (آخرین 7 روز)
        daily_trend_calc = (
            queryset
                .annotate(date=TruncDate('created_at'))
                .values('date')
                .annotate(count=Count('id'))
                .order_by('date')[:days]
        )

        categories_daily_trend = [item['date'] for item in daily_trend_calc]
        story_counts_daily_trend = [item['count'] for item in daily_trend_calc]

        daily_trend = [
            {
                "categories": categories_daily_trend,
                "data": story_counts_daily_trend
            }
        ]
        #
        # # روند ماهانه (آخرین 6 ماه)
        monthly_trend = (
            queryset
                .annotate(month=TruncMonth('created_at'))
                .values('month')
                .annotate(count=Count('id'))
                .order_by('-month')[:6]
        )
        #
        # آمار بر اساس موضوع
        # by_topic = (
        #     queryset
        #     .annotate(story_count=Count('id'))
        #     .values('topic_id', 'story_count')
        #     .order_by('-story_count')
        # )

        by_topic = (
            queryset
                .values('page__topic__id', 'page__topic__name')  # گروه‌بندی بر اساس موضوع
                .annotate(story_count=Count('id'))  # شمارش داستان‌ها
                .order_by('-story_count')  # مرتب سازی
                .filter(page__topic__isnull=False)  # حذف موارد بدون موضوع
        )

        categories_by_topic = [item['page__topic__name'] for item in by_topic]
        story_counts_by_topic = [item['story_count'] for item in by_topic]

        by_topic = [
            {
                "categories": categories_by_topic,
                "data": story_counts_by_topic
            }
        ]

        by_sub_topic = (
            queryset
                .values('page__sub_topic__id', 'page__sub_topic__name')  # گروه‌بندی بر اساس موضوع
                .annotate(story_count=Count('id'))  # شمارش داستان‌ها
                .order_by('-story_count')  # مرتب سازی
                .filter(page__sub_topic__isnull=False)  # حذف موارد بدون موضوع
        )

        categories_by_sub_topic = [item['page__sub_topic__name'] for item in by_sub_topic]
        story_counts_by_sub_topic = [item['story_count'] for item in by_sub_topic]

        by_sub_topic = [
            {
                "categories": categories_by_sub_topic,
                "data": story_counts_by_sub_topic
            }
        ]

        #
        # آمار بر اساس نویسنده
        by_page = (
            queryset
                .values('page__id', 'page__page', 'page__followers_count')  # گروه‌بندی بر اساس موضوع
                .annotate(story_count=Count('id'))  # شمارش داستان‌ها
                .order_by('-story_count')  # مرتب سازی
                .filter(page__isnull=False)  # حذف موارد بدون موضوع
        )
        # print(by_page)
        ###################################
        by_page_queryset = (
            StoryModel.objects
                .select_related('page', 'page__topic')
                .values('page__topic__name', 'page__page', 'page__followers_count')
                # .distinct('page__page')
                .order_by('page__topic__name')
        )

        # گروه‌بندی داده‌ها بر اساس موضوع
        grouped_data = defaultdict(list)

        # یک لیست از تمام مقادیر value برای محاسبه max_value
        all_values = []

        for item in by_page_queryset:
            topic_name = item['page__topic__name'] or 'بدون موضوع'
            raw_value = item['page__followers_count'] or 0
            all_values.append(raw_value)
            grouped_data[topic_name].append({
                'page': item['page__page'],
                'value': raw_value
            })

        # پیدا کردن max_value
        max_value = max(all_values) if all_values else 1  # جلوگیری از تقسیم بر صفر

        # نرمالایز کردن همه مقادیر بر اساس max_value
        normalized_grouped_data = []

        for topic, pages in grouped_data.items():
            normalized_pages = []
            for page_info in pages:
                normalized_value = int((page_info['value'] / max_value) * 1000)
                normalized_pages.append({
                    'name': page_info['page'],
                    'value': normalized_value
                })
            normalized_grouped_data.append({
                'name': topic,
                'data': normalized_pages
            })

        by_page_bubble = normalized_grouped_data

        ###############
        # by_page_queryset = (
        #     StoryModel.objects
        #         .select_related('page', 'page__topic')
        #         .values('page__topic__name', 'page__page')  # فقط اسم صفحه و موضوع
        #         .annotate(story_count=Count('id'))  # شمارش استوری‌ها برای هر صفحه
        #         .order_by('page__topic__name')
        # )
        #
        # # مرحله 2: گروه‌بندی داده‌ها بر اساس موضوع + ذخیره story_count
        # grouped_data = defaultdict(list)
        #
        # for item in by_page_queryset:
        #     topic_name = item['page__topic__name'] or 'بدون موضوع'
        #
        #     grouped_data[topic_name].append({
        #         'page': item['page__page'],
        #         'value': item['story_count']
        #     })
        #
        # # مرحله 3: پیدا کردن max_value برای هر موضوع
        # max_values_per_topic = {
        #     topic: max((item['value'] for item in pages), default=0)
        #     for topic, pages in grouped_data.items()
        # }
        #
        # # مرحله 4: نرمالایز کردن داده‌ها بر اساس max_value هر موضوع و گرفتن 10 تا اولی
        # normalized_grouped_data = []
        #
        # for topic, pages in grouped_data.items():
        #     max_val = max_values_per_topic[topic]
        #
        #     # مرتب‌سازی بر اساس value (نزولی) و گرفتن 10 تا اولی
        #     sorted_pages = sorted(pages, key=lambda x: x['value'], reverse=True)[:10]
        #
        #     normalized_pages = []
        #     for page_info in sorted_pages:
        #         if max_val > 0:
        #             normalized_value = int(round((page_info['value'] / max_val) * 1000, 0))
        #         else:
        #             normalized_value = 0  # اگر max_val صفر بود
        #
        #         normalized_pages.append({
        #             'page': page_info['page'],
        #             'value': normalized_value
        #         })
        #
        #     normalized_grouped_data.append({
        #         'topic': topic,
        #         'data': normalized_pages
        #     })
        ###############
        categories_by_page = [item['page__page'] for item in by_page]
        story_counts_by_page = [item['story_count'] for item in by_page]

        by_page = [
            {
                "categories": categories_by_page,
                "data": story_counts_by_page
            }
        ]

        # by_page = (
        #     queryset
        #         .values('page')
        #         .annotate(story_count=Count('id'))
        #         .order_by('-story_count')
        # )

        by_type = (
            queryset
                .values('story_type')
                .annotate(story_count=Count('id'))
                .order_by('-story_count')
        )

        formatted_by_type = [
            {"name": item["story_type"], "y": item["story_count"]}
            for item in by_type
        ]

        by_type = formatted_by_type

        by_feeling = (
            queryset
                .values('feeling')
                .annotate(story_count=Count('id'))
                .order_by('-story_count')
        )

        formatted_by_feeling = [
            {"name": item["feeling"], "y": item["story_count"]}
            for item in by_feeling
        ]

        by_feeling = formatted_by_feeling

        categories = [
            jdatetime.date.fromgregorian(date=item['date']).strftime('%Y-%m-%d')
            for item in daily_trend_calc
        ]
        # categories = categories_daily_trend
        all_feelings = set(queryset.values_list('feeling', flat=True).distinct())

        feeling_data = defaultdict(list)
        for feeling in all_feelings:
            if feeling:
                feeling_data[feeling] = []

        for day in daily_trend_calc:
            date = day['date']
            for feeling in all_feelings:
                count = queryset.filter(feeling=feeling, created_at__date=date).count()
                feeling_data[feeling].append(count)

        series = []
        for feeling in feeling_data:
            series.append({
                "name": feeling,
                "data": feeling_data[feeling]
            })

        by_feeling_streamgraph = {
            "categories": categories,
            "series": series
        }



        by_tone = (
            queryset
                .values('tone')
                .annotate(story_count=Count('id'))
                .order_by('-story_count')
        )

        formatted_by_tone = [
            {"name": item["tone"], "y": item["story_count"]}
            for item in by_tone
        ]

        by_tone = formatted_by_tone

        by_ironic = (
            queryset
                .values('ironic')
                .annotate(story_count=Count('id'))
                .order_by('-story_count')
        )

        formatted_by_ironic = [
            {"name": item["ironic"], "y": item["story_count"]}
            for item in by_ironic
        ]

        by_ironic = formatted_by_ironic

        top_tag = StoryModel.get_top_tags_from_queryset(queryset)
        text_tag = StoryModel.get_text_from_queryset(queryset)

        #########################
        # categories based on tone
        tone_categories = []
        for item in by_tone:
            # You can customize the icon or class based on tone value
            flag_class = item['name'].lower()  # e.g., formal → 'formal'
            tone_categories.append(
                f"{item['name']}"
                )

        # series based on feeling
        feeling_dict = defaultdict(list)
        all_feelings = set(item['name'] for item in formatted_by_feeling)

        # For each tone, collect counts per feeling
        for story in queryset:
            feeling_dict[story.feeling].append({
                'tone': story.tone,
                'count': 1  # Count per row
            })

        # Aggregate data
        aggregated_data = {}
        for feeling in all_feelings:
            aggregated_data[feeling] = [0] * len(tone_categories)

        for i, tone_item in enumerate([item['name'] for item in by_tone]):
            stories = queryset.filter(tone=tone_item)
            feeling_counts = stories.values('feeling').annotate(count=Count('id'))
            for fc in feeling_counts:

                if fc['feeling'] in aggregated_data:
                    aggregated_data[fc['feeling']][i] = fc['count']

        final_series = [
            {
                'name': feeling,
                'data': aggregated_data[feeling]
            } for feeling in aggregated_data
        ]

        all_values = []
        for series_item in final_series:
            all_values.extend(series_item['data'])

        # محاسبه max_value
        if all_values:
            max_value = max(all_values)
        else:
            max_value = 0


        # Final structure
        by_feeling_tone = {
            'categories': tone_categories,
            'series': final_series,
            'max_value': max_value
        }
        ################################

        #
        # تبدیل تاریخ‌ها به جلالی
        def convert_to_jalali(trend):
            for item in trend:
                if 'date' in item:
                    item['date'] = jdatetime.date.fromgregorian(date=item['date']).strftime('%Y-%m-%d')
                if 'month' in item:
                    item['month'] = jdatetime.date.fromgregorian(date=item['month']).strftime('%Y-%m')
            return trend

        data = {
            'total_count': total_count,
            'page_count': page_count,
            # 'published_count': published_count,
            'daily_trend': convert_to_jalali(list(daily_trend)),
            'monthly_trend': convert_to_jalali(list(monthly_trend)),
            'by_topic': list(by_topic),
            'by_page': list(by_page),
            'by_type': list(by_type),
            'top_tag': list(top_tag),
            'text_tag': list(text_tag),
            'by_feeling': list(by_feeling),
            'by_tone': list(by_tone),
            'by_ironic': list(by_ironic),
            'by_sub_topic': list(by_sub_topic),
            'by_page_bubble': by_page_bubble,
            'by_feeling_tone': by_feeling_tone,
            'by_feeling_streamgraph' : by_feeling_streamgraph
        }

        serializer = StoryStatsSerializer(data)
        return Response(serializer.data)


class InstagramPageViewSet(viewsets.ModelViewSet):
    queryset = InstagramPage.objects.all()
    serializer_class = InstagramPageSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['topic_id','category_id']


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['topic_id','category_id']


class DayAnalysisViewSet(viewsets.ModelViewSet):
    queryset = DayAnalysis.objects.all()
    serializer_class = DayAnalysisSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        days = self.request.query_params.get('days')

        if days is not None and days.isdigit():
            date_threshold = timezone.now() - timedelta(days=int(days))
            queryset = queryset.filter(created_at__gte=date_threshold)

        return queryset
