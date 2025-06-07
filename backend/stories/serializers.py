from rest_framework import serializers
from .models import StoryModel, Topic, SubTopic, InstagramPage, Category, DayAnalysis
import jdatetime
# from django_jalali.templatetags.jalali import jalali_format


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'category_image']


class SubTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTopic
        fields = ['id', 'name']


class TopicSerializer(serializers.ModelSerializer):
    sub_topics = SubTopicSerializer(many=True, read_only=True)
    usage_count = serializers.SerializerMethodField()
    # story_count = serializers.SerializerMethodField()
    story_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Topic
        fields = ['id', 'name', 'sub_topics', 'usage_count', 'story_count', 'icon']


    def get_usage_count(self, obj):
        return obj.instagrampage.count()


    # def get_story_count(self, obj):
    #     return StoryModel.objects.filter(page__topic=obj).count()



class StoryModelSerializer(serializers.ModelSerializer):
    jalali_created_at = serializers.SerializerMethodField()
    page_name = serializers.SerializerMethodField()
    # topic = TopicSerializer(read_only=True)
    # sub_topic = SubTopicSerializer(read_only=True)
    # topic_id = serializers.PrimaryKeyRelatedField(
    #     queryset=Topic.objects.all(),
    #     source='topic',
    #     write_only=True,
    #     required=False,
    #     allow_null=True
    # )
    # sub_topic_id = serializers.PrimaryKeyRelatedField(
    #     queryset=SubTopic.objects.all(),
    #     source='sub_topic',
    #     write_only=True,
    #     required=False,
    #     allow_null=True
    # )

    class Meta:
        model = StoryModel
        fields = [
            'id',
            'story',
            'page',
            'created_at',
            'jalali_created_at',
            'feeling',
            'tone',
            'ironic',
            'description',
            # 'topic',
            # 'sub_topic',
            # 'topic_id',
            # 'sub_topic_id',
            'story_text',
            'story_type',
            'page_name',
            'category_id'
        ]
        read_only_fields = ['page']

    def get_jalali_created_at(self, obj):
        created_at = obj.created_at
        return created_at.strftime('%Y-%m-%d')

    def get_page_name(self, obj):
        return obj.page.username

    def get_story_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.story.url)
        return None

    # def create(self, validated_data):
    #     validated_data['user'] = self.context['request'].user
    #     return super().create(validated_data)


class StoryStatsSerializer(serializers.Serializer):
    total_count = serializers.IntegerField()
    page_count = serializers.IntegerField()
    # published_count = serializers.IntegerField()
    # draft_count = serializers.IntegerField()
    daily_trend = serializers.ListField(child=serializers.DictField())
    monthly_trend = serializers.ListField(child=serializers.DictField())
    by_topic = serializers.ListField(child=serializers.DictField())
    by_sub_topic = serializers.ListField(child=serializers.DictField())
    by_page = serializers.ListField(child=serializers.DictField())
    by_type = serializers.ListField(child=serializers.DictField())
    top_tag = serializers.ListField(child=serializers.DictField())
    text_tag = serializers.ListField(child=serializers.DictField())
    by_feeling = serializers.ListField(child=serializers.DictField())
    by_tone = serializers.ListField(child=serializers.DictField())
    by_ironic = serializers.ListField(child=serializers.DictField())
    by_page_bubble = serializers.ListField(child=serializers.DictField())
    by_feeling_tone = serializers.DictField()
    by_feeling_streamgraph = serializers.DictField()


class InstagramPageSerializer(serializers.ModelSerializer):
    # jalali_created_at = serializers.SerializerMethodField()
    # jalali_updated_at = serializers.SerializerMethodField()
    # profile_image_url = serializers.SerializerMethodField()
    usage_count = serializers.SerializerMethodField()
    page_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = InstagramPage
        fields = [
            'id', 'page','page_id','username', 'profile_image', 'bio', 'topic', 'sub_topic', 'topic_id', 'sub_topic_id',
            'followers_count', 'following_count', 'posts_count',
            'average_likes', 'average_comments', 'is_verified',
            'is_active', 'created_at','usage_count','category_id'
        ]

    # def get_jalali_created_at(self, obj):
    #     return jalali_convert(obj.created_at)
    #
    # def get_jalali_updated_at(self, obj):
    #     return jalali_convert(obj.updated_at)
    #

    def get_usage_count(self, obj):
        return obj.storymodel_set.count()


    def get_profile_image_url(self, obj):
        if obj.profile_image:
            return self.context['request'].build_absolute_uri(obj.profile_image.url)
        return None




class DayAnalysisSerializer(serializers.ModelSerializer):
    jalali_date = serializers.SerializerMethodField()

    class Meta:
        model = DayAnalysis
        fields = ['id', 'text', 'jalali_date', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_jalali_date(self, obj):
        gregorian_date = obj.jalali_date
        jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
        return jalali_date.strftime('%Y/%m/%d')