"""
Django管理命令：初始化定位策略
用法：python manage.py init_locator_strategies
"""
from django.core.management.base import BaseCommand
from apps.ui_automation.models import LocatorStrategy


class Command(BaseCommand):
    help = '初始化UI自动化的元素定位策略'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始初始化定位策略...'))

        # 定义所有支持的定位策略
        strategies = [
            {
                'name': 'ID',
                'description': '通过元素的 id 属性定位，最快速可靠'
            },
            {
                'name': 'CSS',
                'description': '通过 CSS 选择器定位，灵活强大'
            },
            {
                'name': 'XPath',
                'description': '通过 XPath 表达式定位，功能最强大'
            },
            {
                'name': 'name',
                'description': '通过元素的 name 属性定位'
            },
            {
                'name': 'class',
                'description': '通过元素的 class 属性定位'
            },
            {
                'name': 'tag',
                'description': '通过 HTML 标签名定位'
            },
            {
                'name': 'text',
                'description': 'Playwright 专用：通过文本内容定位，推荐用于按钮、链接等'
            },
            {
                'name': 'placeholder',
                'description': 'Playwright 专用：通过 placeholder 属性定位输入框'
            },
            {
                'name': 'role',
                'description': 'Playwright 专用：通过 ARIA role 定位，推荐用于可访问性'
            },
            {
                'name': 'label',
                'description': 'Playwright 专用：通过关联的 label 文本定位表单元素'
            },
            {
                'name': 'title',
                'description': 'Playwright 专用：通过 title 属性定位'
            },
            {
                'name': 'test-id',
                'description': 'Playwright 专用：通过 data-testid 属性定位，推荐用于测试'
            },
        ]

        created_count = 0
        updated_count = 0

        for strategy_data in strategies:
            strategy, created = LocatorStrategy.objects.get_or_create(
                name=strategy_data['name'],
                defaults={'description': strategy_data['description']}
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ 创建策略: {strategy.name}'))
                created_count += 1
            else:
                # 更新描述
                if strategy.description != strategy_data['description']:
                    strategy.description = strategy_data['description']
                    strategy.save()
                    self.stdout.write(self.style.WARNING(f'  ↻ 更新策略: {strategy.name}'))
                    updated_count += 1
                else:
                    self.stdout.write(f'  - 策略已存在: {strategy.name}')

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'初始化完成！'))
        self.stdout.write(self.style.SUCCESS(f'新创建: {created_count} 个'))
        self.stdout.write(self.style.SUCCESS(f'更新: {updated_count} 个'))
        self.stdout.write(self.style.SUCCESS(f'总计: {LocatorStrategy.objects.count()} 个定位策略'))
        self.stdout.write('='*60 + '\n')

        # 列出所有定位策略
        self.stdout.write('\n当前可用的定位策略：')
        for strategy in LocatorStrategy.objects.all().order_by('id'):
            playwright_tag = ' [Playwright专用]' if strategy.name in ['text', 'placeholder', 'role', 'label', 'title', 'test-id'] else ''
            self.stdout.write(f'  - {strategy.name}{playwright_tag}: {strategy.description}')
