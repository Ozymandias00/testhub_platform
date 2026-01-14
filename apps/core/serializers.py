"""
Core 应用序列化器
"""
from rest_framework import serializers
from .models import UnifiedNotificationConfig


class UnifiedNotificationConfigSerializer(serializers.ModelSerializer):
    """统一通知配置序列化器"""

    webhook_bots_display = serializers.SerializerMethodField()

    class Meta:
        model = UnifiedNotificationConfig
        fields = [
            'id', 'name', 'config_type', 'webhook_bots',
            'is_default', 'is_active', 'created_at', 'updated_at',
            'created_by', 'webhook_bots_display'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'webhook_bots_display']

    def get_webhook_bots_display(self, obj):
        """获取webhook机器人显示信息"""
        bots = obj.get_webhook_bots()
        display_list = []
        for bot in bots:
            display_list.append({
                'type': bot.get('type'),
                'name': bot.get('name'),
                'enabled': bot.get('enabled'),
                'enable_ui_automation': bot.get('enable_ui_automation'),
                'enable_api_testing': bot.get('enable_api_testing')
            })
        return display_list
