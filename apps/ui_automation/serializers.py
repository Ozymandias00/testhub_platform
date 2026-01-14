from rest_framework import serializers
from django.utils import timezone
from .models import (
    UiProject, LocatorStrategy, Element, TestScript, TestSuite,
    TestSuiteScript, TestSuiteTestCase, TestExecution, TestEnvironment, Screenshot,
    ElementGroup, PageObject, PageObjectElement, ScriptStep, ScriptElementUsage,
    TestCase, TestCaseStep, TestCaseExecution, OperationRecord,
    UiScheduledTask, UiNotificationLog, UiTaskNotificationSetting,
    AICase, AIExecutionRecord
)
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class UiProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = UiProject
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class UiProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UiProject
        fields = ('name', 'description', 'status', 'base_url', 'start_date', 'end_date', 'owner', 'members')


class UiProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UiProject
        fields = ('name', 'description', 'status', 'base_url', 'start_date', 'end_date', 'members')


class LocatorStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = LocatorStrategy
        fields = '__all__'


class ElementSerializer(serializers.ModelSerializer):
    project = UiProjectSerializer(read_only=True)
    locator_strategy = LocatorStrategySerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    project_id = serializers.IntegerField(write_only=True)
    group_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    locator_strategy_id = serializers.IntegerField()  # 显式定义，支持读写

    class Meta:
        model = Element
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')

    def validate_project_id(self, value):
        """验证项目ID是否有效"""
        try:
            UiProject.objects.get(id=value)
        except UiProject.DoesNotExist:
            raise serializers.ValidationError("请选择有效的项目")
        return value

    def validate_locator_strategy_id(self, value):
        """验证定位策略ID是否有效"""
        if value is not None:
            try:
                LocatorStrategy.objects.get(id=value)
            except LocatorStrategy.DoesNotExist:
                raise serializers.ValidationError("请选择有效的定位策略")
        return value

    def validate_group_id(self, value):
        """验证分组ID是否有效"""
        if value is not None:  # 允许None值
            try:
                ElementGroup.objects.get(id=value)
            except ElementGroup.DoesNotExist:
                raise serializers.ValidationError("请选择有效的元素分组")
        return value

    def create(self, validated_data):
        # 处理外键字段
        project_id = validated_data.pop('project_id')
        locator_strategy_id = validated_data.pop('locator_strategy_id', None)
        group_id = validated_data.pop('group_id', None)

        validated_data['project'] = UiProject.objects.get(id=project_id)

        if locator_strategy_id:
            validated_data['locator_strategy'] = LocatorStrategy.objects.get(id=locator_strategy_id)

        if group_id:
            validated_data['group'] = ElementGroup.objects.get(id=group_id)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # 处理外键字段
        project_id = validated_data.pop('project_id', None)
        locator_strategy_id = validated_data.pop('locator_strategy_id', None)
        group_id = validated_data.pop('group_id', None)

        if project_id:
            validated_data['project'] = UiProject.objects.get(id=project_id)

        if locator_strategy_id:
            validated_data['locator_strategy'] = LocatorStrategy.objects.get(id=locator_strategy_id)

        if group_id is not None:  # 允许设置为None来清除分组
            if group_id:
                validated_data['group'] = ElementGroup.objects.get(id=group_id)
            else:
                validated_data['group'] = None

        return super().update(instance, validated_data)


class TestScriptSerializer(serializers.ModelSerializer):
    project = UiProjectSerializer(read_only=True)
    project_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = TestScript
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class TestScriptCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestScript
        fields = ('project', 'name', 'description', 'script_type', 'content', 'language', 'framework')


class TestScriptUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestScript
        fields = ('name', 'description', 'script_type', 'content')


class TestSuiteScriptSerializer(serializers.ModelSerializer):
    test_script = TestScriptSerializer(read_only=True)
    test_script_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = TestSuiteScript
        fields = ('id', 'test_script', 'test_script_id', 'order')


class TestSuiteTestCaseSerializer(serializers.ModelSerializer):
    test_case = serializers.SerializerMethodField()
    test_case_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = TestSuiteTestCase
        fields = ('id', 'test_case', 'test_case_id', 'order')

    def get_test_case(self, obj):
        """获取测试用例信息"""
        test_case = obj.test_case
        return {
            'id': test_case.id,
            'name': test_case.name,
            'description': test_case.description,
            'status': test_case.status,
            'priority': test_case.priority,
            'created_at': test_case.created_at
        }


class TestSuiteSerializer(serializers.ModelSerializer):
    project = UiProjectSerializer(read_only=True)
    scripts = TestScriptSerializer(many=True, read_only=True)
    test_cases_data = serializers.SerializerMethodField()
    project_id = serializers.IntegerField(write_only=True)
    suite_scripts = TestSuiteScriptSerializer(many=True, read_only=True)
    suite_test_cases = TestSuiteTestCaseSerializer(many=True, read_only=True)
    test_case_count = serializers.SerializerMethodField()

    class Meta:
        model = TestSuite
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'execution_status', 'passed_count', 'failed_count')

    def get_test_cases_data(self, obj):
        """获取测试用例数据"""
        return TestSuiteTestCaseSerializer(obj.suite_test_cases.all(), many=True).data

    def get_test_case_count(self, obj):
        """获取测试用例数量"""
        return obj.suite_test_cases.count()


class TestSuiteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSuite
        fields = ('id', 'project', 'name', 'description')
        read_only_fields = ('id',)


class TestSuiteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSuite
        fields = ('name', 'description')


class TestSuiteWithScriptsSerializer(serializers.ModelSerializer):
    project = UiProjectSerializer(read_only=True)
    suite_scripts = TestSuiteScriptSerializer(many=True, read_only=True)

    class Meta:
        model = TestSuite
        fields = '__all__'


class TestExecutionSerializer(serializers.ModelSerializer):
    project = UiProjectSerializer(read_only=True)
    test_suite = TestSuiteSerializer(read_only=True)
    test_script = TestScriptSerializer(read_only=True)
    executed_by = UserSerializer(read_only=True)
    project_id = serializers.IntegerField(write_only=True)
    test_suite_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    test_script_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    executed_by_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    # 添加计算字段
    test_suite_name = serializers.SerializerMethodField()
    executed_by_name = serializers.SerializerMethodField()
    pass_rate = serializers.SerializerMethodField()

    class Meta:
        model = TestExecution
        fields = '__all__'
        read_only_fields = (
            'created_at', 'started_at', 'finished_at', 'duration',
            'total_cases', 'passed_cases', 'failed_cases', 'skipped_cases'
        )

    def get_test_suite_name(self, obj):
        """获取测试套件名称"""
        return obj.test_suite.name if obj.test_suite else '-'
    
    def get_executed_by_name(self, obj):
        """获取执行人姓名"""
        return obj.executed_by.username if obj.executed_by else '-'

    def get_pass_rate(self, obj):
        """获取通过率"""
        return obj.pass_rate


class TestExecutionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestExecution
        fields = ('project', 'test_suite', 'test_script', 'environment', 'executed_by')


class ScreenshotSerializer(serializers.ModelSerializer):
    execution = TestExecutionSerializer(read_only=True)
    execution_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Screenshot
        fields = '__all__'
        read_only_fields = ('created_at', 'captured_at')


# 新增的serializers
class ElementGroupSerializer(serializers.ModelSerializer):
    project = UiProjectSerializer(read_only=True)
    project_id = serializers.IntegerField(write_only=True)
    elements_count = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = ElementGroup
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_elements_count(self, obj):
        """获取分组下的元素数量"""
        return obj.elements.count()

    def get_children(self, obj):
        """获取子分组"""
        children = obj.elementgroup_set.all()
        return ElementGroupSerializer(children, many=True, context=self.context).data


class ElementGroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementGroup
        fields = ('project', 'name', 'description', 'parent_group', 'order')


class ElementEnhancedSerializer(serializers.ModelSerializer):
    """增强的元素序列化器，包含新字段"""
    project = UiProjectSerializer(read_only=True)
    group = ElementGroupSerializer(read_only=True)
    locator_strategy = LocatorStrategySerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    parent_element = serializers.SerializerMethodField()
    children_elements = serializers.SerializerMethodField()
    all_locators = serializers.SerializerMethodField()
    usage_scripts = serializers.SerializerMethodField()

    # Write-only fields for foreign keys
    project_id = serializers.IntegerField(write_only=True)
    group_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    locator_strategy_id = serializers.IntegerField()  # 允许读写,支持回显
    parent_element_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Element
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'usage_count', 'last_validated')

    def get_parent_element(self, obj):
        """获取父元素信息"""
        if obj.parent_element:
            return {
                'id': obj.parent_element.id,
                'name': obj.parent_element.name,
                'page': obj.parent_element.page
            }
        return None

    def get_children_elements(self, obj):
        """获取子元素"""
        children = obj.element_set.all()
        return [{
            'id': child.id,
            'name': child.name,
            'element_type': child.element_type
        } for child in children]

    def get_all_locators(self, obj):
        """获取所有定位器（主要+备用）"""
        return obj.get_all_locators()

    def get_usage_scripts(self, obj):
        """获取使用此元素的脚本列表"""
        usages = obj.script_usages.select_related('script').all()[:5]  # 只返回前5个
        return [{
            'script_id': usage.script.id,
            'script_name': usage.script.name,
            'usage_type': usage.usage_type,
            'frequency': usage.frequency
        } for usage in usages]

    def create(self, validated_data):
        # 处理外键字段
        project_id = validated_data.pop('project_id')
        locator_strategy_id = validated_data.pop('locator_strategy_id')
        group_id = validated_data.pop('group_id', None)
        parent_element_id = validated_data.pop('parent_element_id', None)

        validated_data['project'] = UiProject.objects.get(id=project_id)
        validated_data['locator_strategy'] = LocatorStrategy.objects.get(id=locator_strategy_id)

        if group_id:
            validated_data['group'] = ElementGroup.objects.get(id=group_id)

        if parent_element_id:
            validated_data['parent_element'] = Element.objects.get(id=parent_element_id)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # 处理外键字段
        project_id = validated_data.pop('project_id', None)
        locator_strategy_id = validated_data.pop('locator_strategy_id', None)
        group_id = validated_data.pop('group_id', None)
        parent_element_id = validated_data.pop('parent_element_id', None)

        if project_id:
            validated_data['project'] = UiProject.objects.get(id=project_id)

        if locator_strategy_id:
            validated_data['locator_strategy'] = LocatorStrategy.objects.get(id=locator_strategy_id)

        if group_id is not None:  # 允许设置为None来清除分组
            if group_id:
                validated_data['group'] = ElementGroup.objects.get(id=group_id)
            else:
                validated_data['group'] = None

        if parent_element_id is not None:  # 允许设置为None来清除父元素
            if parent_element_id:
                validated_data['parent_element'] = Element.objects.get(id=parent_element_id)
            else:
                validated_data['parent_element'] = None

        return super().update(instance, validated_data)


class PageObjectSerializer(serializers.ModelSerializer):
    project = UiProjectSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    elements_count = serializers.SerializerMethodField()
    elements = serializers.SerializerMethodField()
    project_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PageObject
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'template_code')

    def get_elements_count(self, obj):
        """获取页面对象包含的元素数量"""
        return obj.page_object_elements.count()

    def get_elements(self, obj):
        """获取页面对象包含的元素"""
        po_elements = obj.page_object_elements.select_related('element').all()
        return [{
            'id': po_element.id,
            'element_id': po_element.element.id,
            'element_name': po_element.element.name,
            'method_name': po_element.method_name,
            'is_property': po_element.is_property,
            'order': po_element.order
        } for po_element in po_elements]


class PageObjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageObject
        fields = ('project', 'name', 'class_name', 'url_pattern', 'description')

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class PageObjectElementSerializer(serializers.ModelSerializer):
    page_object = PageObjectSerializer(read_only=True)
    element = ElementEnhancedSerializer(read_only=True)
    page_object_id = serializers.IntegerField(write_only=True)
    element_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PageObjectElement
        fields = '__all__'
        read_only_fields = ('created_at',)

    def validate_method_name(self, value):
        """验证方法名称是否符合命名规范"""
        import re
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', value):
            raise serializers.ValidationError("方法名称只能包含字母、数字和下划线，且不能以数字开头")
        return value


class ScriptStepSerializer(serializers.ModelSerializer):
    script = TestScriptSerializer(read_only=True)
    target_element = ElementEnhancedSerializer(read_only=True)
    page_object = PageObjectSerializer(read_only=True)

    script_id = serializers.IntegerField(write_only=True)
    target_element_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    page_object_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = ScriptStep
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, data):
        """验证步骤配置"""
        target_element_id = data.get('target_element_id')
        page_object_id = data.get('page_object_id')
        action_type = data.get('action_type')

        # 某些操作类型需要指定目标元素
        if action_type in ['CLICK', 'INPUT', 'SELECT', 'HOVER', 'VERIFY'] and not target_element_id and not page_object_id:
            raise serializers.ValidationError("此操作类型需要指定目标元素或页面对象")

        return data


class ScriptElementUsageSerializer(serializers.ModelSerializer):
    script = TestScriptSerializer(read_only=True)
    element = ElementEnhancedSerializer(read_only=True)
    script_id = serializers.IntegerField(write_only=True)
    element_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ScriptElementUsage
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ScriptAnalysisSerializer(serializers.Serializer):
    """脚本分析结果序列化器"""
    element_usages = ScriptElementUsageSerializer(many=True, read_only=True)
    missing_elements = serializers.ListField(child=serializers.CharField(), read_only=True)
    recommendations = serializers.ListField(child=serializers.CharField(), read_only=True)
    complexity_score = serializers.IntegerField(read_only=True)


class ElementValidationSerializer(serializers.Serializer):
    """元素验证结果序列化器"""
    is_valid = serializers.BooleanField(read_only=True)
    validation_message = serializers.CharField(read_only=True)
    suggestions = serializers.ListField(child=serializers.CharField(), read_only=True)


class CodeGenerationSerializer(serializers.Serializer):
    """代码生成序列化器"""
    language = serializers.ChoiceField(choices=[('javascript', 'JavaScript'), ('python', 'Python')], default='javascript')
    framework = serializers.ChoiceField(choices=[('playwright', 'Playwright'), ('selenium', 'Selenium')], default='playwright')
    include_comments = serializers.BooleanField(default=True)

    def validate(self, data):
        # 可以添加更多验证逻辑
        return data


class TestCaseStepSerializer(serializers.ModelSerializer):
    """测试用例步骤序列化器"""
    element_name = serializers.CharField(source='element.name', read_only=True)
    element_locator = serializers.CharField(source='element.locator_value', read_only=True)

    class Meta:
        model = TestCaseStep
        fields = [
            'id', 'step_number', 'action_type', 'element', 'element_name', 'element_locator',
            'input_value', 'wait_time', 'assert_type', 'assert_value', 'description', 'created_at'
        ]


class TestCaseSerializer(serializers.ModelSerializer):
    """测试用例序列化器"""
    steps = TestCaseStepSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = TestCase
        fields = [
            'id', 'name', 'description', 'project', 'project_name', 'status', 'priority',
            'created_by', 'created_by_name', 'created_at', 'updated_at', 'steps'
        ]
        read_only_fields = ['created_by']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TestCaseExecutionSerializer(serializers.ModelSerializer):
    """测试用例执行记录序列化器"""
    test_case_name = serializers.CharField(source='test_case.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    test_suite_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = TestCaseExecution
        fields = [
            'id', 'test_case', 'test_case_name', 'project', 'project_name',
            'test_suite', 'test_suite_name', 'execution_source', 'status',
            'engine', 'browser', 'headless', 'execution_logs', 'error_message',
            'screenshots', 'execution_time', 'started_at', 'finished_at',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['created_by']
    
    def get_test_suite_name(self, obj):
        """获取测试套件名称"""
        return obj.test_suite.name if obj.test_suite else None
    
    def get_created_by_name(self, obj):
        """获取创建人姓名"""
        return obj.created_by.username if obj.created_by else '-'

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TestCaseRunSerializer(serializers.Serializer):
    """测试用例运行序列化器"""
    test_case_id = serializers.IntegerField()
    project_id = serializers.IntegerField()
    browser = serializers.ChoiceField(choices=['chrome', 'firefox', 'safari'], default='chrome')

    def validate_test_case_id(self, value):
        try:
            TestCase.objects.get(id=value)
        except TestCase.DoesNotExist:
            raise serializers.ValidationError("测试用例不存在")
        return value

    def validate_project_id(self, value):
        try:
            UiProject.objects.get(id=value)
        except UiProject.DoesNotExist:
            raise serializers.ValidationError("项目不存在")
        return value


class OperationRecordSerializer(serializers.ModelSerializer):
    """操作记录序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    operation_type_display = serializers.CharField(source='get_operation_type_display', read_only=True)
    resource_type_display = serializers.CharField(source='get_resource_type_display', read_only=True)

    class Meta:
        model = OperationRecord
        fields = [
            'id', 'operation_type', 'operation_type_display', 'resource_type',
            'resource_type_display', 'resource_id', 'resource_name', 'description',
            'user', 'user_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# ==================== 定时任务和通知相关序列化器 ====================

class UiScheduledTaskSerializer(serializers.ModelSerializer):
    """UI定时任务序列化器"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    test_suite_name = serializers.CharField(source='test_suite.name', read_only=True)
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    trigger_type_display = serializers.CharField(source='get_trigger_type_display', read_only=True)
    notification_type_display = serializers.SerializerMethodField()

    class Meta:
        model = UiScheduledTask
        fields = [
            'id', 'name', 'description', 'task_type', 'task_type_display',
            'trigger_type', 'trigger_type_display', 'cron_expression',
            'interval_seconds', 'execute_at', 'project', 'project_name',
            'test_suite', 'test_suite_name', 'test_cases',
            'engine', 'browser', 'headless',
            'notify_on_success', 'notify_on_failure', 'notification_type', 'notification_type_display', 'notify_emails',
            'status', 'status_display',
            'last_run_time', 'next_run_time', 'total_runs',
            'successful_runs', 'failed_runs', 'last_result', 'error_message',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_by', 'last_run_time', 'next_run_time', 'total_runs',
            'successful_runs', 'failed_runs', 'last_result',
            'error_message', 'created_at', 'updated_at'
        ]

    def get_notification_type_display(self, obj):
        """获取通知类型显示"""
        if obj.notification_type:
            return obj.get_notification_type_display()
        return "-"

    def validate(self, attrs):
        """验证定时任务配置"""
        trigger_type = attrs.get('trigger_type')

        if trigger_type == 'CRON':
            if not attrs.get('cron_expression'):
                raise serializers.ValidationError("Cron表达式不能为空")

        elif trigger_type == 'INTERVAL':
            if not attrs.get('interval_seconds'):
                raise serializers.ValidationError("间隔秒数不能为空")
            if attrs['interval_seconds'] < 60:
                raise serializers.ValidationError("间隔秒数不能小于60秒")

        elif trigger_type == 'ONCE':
            if not attrs.get('execute_at'):
                raise serializers.ValidationError("执行时间不能为空")
            if attrs['execute_at'] <= timezone.now():
                raise serializers.ValidationError("执行时间必须大于当前时间")

        # 验证任务类型配置
        task_type = attrs.get('task_type')
        if task_type == 'TEST_SUITE' and not attrs.get('test_suite'):
            raise serializers.ValidationError("测试套件不能为空")
        elif task_type == 'TEST_CASE':
            test_cases = attrs.get('test_cases', [])
            if not test_cases or len(test_cases) == 0:
                raise serializers.ValidationError("至少选择一个测试用例")

        return attrs

    def create(self, validated_data):
        """创建定时任务"""
        validated_data['created_by'] = self.context['request'].user
        instance = super().create(validated_data)
        # 计算下次运行时间
        instance.next_run_time = instance.calculate_next_run()
        instance.save()

        # 创建对应的通知设置（如果启用了通知）
        if instance.notify_on_success or instance.notify_on_failure:
            from .models import UiTaskNotificationSetting
            from apps.core.models import UnifiedNotificationConfig

            # 确定通知类型（默认为webhook）
            notification_type = validated_data.get('notification_type', 'webhook')

            # 根据通知类型选择合适的通知配置
            notification_config = None
            if notification_type in ['webhook', 'both']:
                # 如果需要Webhook通知，优先选择Webhook配置
                notification_config = UnifiedNotificationConfig.objects.filter(
                    config_type__in=['webhook_wechat', 'webhook_feishu', 'webhook_dingtalk'],
                    is_active=True
                ).first()

            if not notification_config:
                # 如果没有找到webhook配置或者是邮件通知，使用默认配置
                notification_config = UnifiedNotificationConfig.objects.filter(
                    is_default=True,
                    is_active=True
                ).first()

            # 创建通知设置
            UiTaskNotificationSetting.objects.create(
                task=instance,
                notification_type=notification_type,
                is_enabled=True,
                notify_on_success=instance.notify_on_success,
                notify_on_failure=instance.notify_on_failure,
                notification_config=notification_config
            )

        return instance

    def update(self, instance, validated_data):
        """更新定时任务"""
        # 更新任务基本信息
        instance = super().update(instance, validated_data)

        # 重新计算下次运行时间
        instance.next_run_time = instance.calculate_next_run()
        instance.save()

        # 更新通知设置
        if instance.notify_on_success or instance.notify_on_failure:
            from .models import UiTaskNotificationSetting
            from apps.core.models import UnifiedNotificationConfig

            # 确定通知类型（默认为webhook）
            notification_type = validated_data.get('notification_type', 'webhook')

            # 根据通知类型选择合适的通知配置
            notification_config = None
            if notification_type in ['webhook', 'both']:
                # 如果需要Webhook通知，优先选择Webhook配置
                notification_config = UnifiedNotificationConfig.objects.filter(
                    config_type__in=['webhook_wechat', 'webhook_feishu', 'webhook_dingtalk'],
                    is_active=True
                ).first()

            if not notification_config:
                # 如果没有找到webhook配置或者是邮件通知，使用默认配置
                notification_config = UnifiedNotificationConfig.objects.filter(
                    is_default=True,
                    is_active=True
                ).first()

            # 获取或创建通知设置
            notification_setting, created = UiTaskNotificationSetting.objects.get_or_create(
                task=instance,
                defaults={
                    'notification_type': notification_type,
                    'is_enabled': True,
                    'notify_on_success': instance.notify_on_success,
                    'notify_on_failure': instance.notify_on_failure,
                    'notification_config': notification_config
                }
            )

            # 如果通知设置已存在，更新它
            if not created:
                notification_setting.notification_type = notification_type
                notification_setting.is_enabled = True
                notification_setting.notify_on_success = instance.notify_on_success
                notification_setting.notify_on_failure = instance.notify_on_failure
                notification_setting.notification_config = notification_config
                notification_setting.save()
        else:
            # 如果不需要通知，禁用通知设置
            from .models import UiTaskNotificationSetting
            UiTaskNotificationSetting.objects.filter(task=instance).update(is_enabled=False)

        return instance


class AICaseSerializer(serializers.ModelSerializer):
    project = UiProjectSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    project_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = AICase
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class AIExecutionRecordSerializer(serializers.ModelSerializer):
    project = UiProjectSerializer(read_only=True)
    ai_case = AICaseSerializer(read_only=True)
    executed_by = UserSerializer(read_only=True)
    project_id = serializers.IntegerField(write_only=True)
    ai_case_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    ai_case_name = serializers.CharField(source='ai_case.name', read_only=True)
    executed_by_name = serializers.CharField(source='executed_by.username', read_only=True)

    class Meta:
        model = AIExecutionRecord
        fields = [
            'id', 'project', 'project_id', 'project_name', 'ai_case', 'ai_case_id', 'ai_case_name', 'case_name',
            'task_description',
            'execution_mode', 'status', 'start_time', 'end_time', 'duration',
            'logs', 'steps_completed', 'planned_tasks', 'executed_by', 'executed_by_name',
            'gif_path', 'screenshots_sequence'
        ]
        read_only_fields = ('start_time', 'end_time', 'duration', 'executed_by', 'gif_path', 'screenshots_sequence')



class UiNotificationLogSerializer(serializers.ModelSerializer):
    """UI通知日志序列化器"""
    recipient_names = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    retry_status = serializers.SerializerMethodField()
    task_type_display = serializers.SerializerMethodField()
    actual_notification_type_display = serializers.SerializerMethodField()

    class Meta:
        model = UiNotificationLog
        fields = [
            'id', 'task', 'task_name', 'notification_type',
            'notification_type_display', 'actual_notification_type_display', 'task_type_display',
            'sender_name', 'sender_email',
            'recipient_names', 'webhook_bot_info', 'notification_content',
            'status', 'status_display', 'error_message', 'response_info',
            'created_at', 'sent_at', 'retry_count', 'retry_status'
        ]
        read_only_fields = ['created_at', 'sent_at']

    def get_recipient_names(self, obj):
        """获取收件人姓名列表"""
        return obj.get_recipient_names()

    def get_retry_status(self, obj):
        """获取重试状态"""
        return obj.get_retry_status()

    def get_task_type_display(self, obj):
        """获取任务类型显示 - 使用保存的快照值"""
        if obj.task_type:
            # 使用保存的任务类型快照
            task_type_choices = dict(UiScheduledTask.TASK_TYPE_CHOICES)
            return task_type_choices.get(obj.task_type, obj.task_type)
        # 如果 task_type 为空，返回未记录，不要从 task 对象获取（避免显示修改后的值）
        return '未记录'

    def get_actual_notification_type_display(self, obj):
        """获取实际的通知类型显示 - 根据实际发送的通知来判断"""
        # 优先检查webhook_bot_info,如果存在则说明是webhook通知
        if obj.webhook_bot_info:
            bot_type = obj.webhook_bot_info.get('bot_type', '') or obj.webhook_bot_info.get('type', '')
            # 根据机器人类型返回友好名称
            type_map = {
                'wechat': '企微机器人',
                'feishu': '飞书机器人',
                'dingtalk': '钉钉机器人'
            }
            return type_map.get(bot_type, 'Webhook机器人')

        # 检查recipient_info,如果存在则说明是邮箱通知
        if obj.recipient_info:
            if isinstance(obj.recipient_info, list) and len(obj.recipient_info) > 0:
                return '邮箱通知'
            elif isinstance(obj.recipient_info, dict) and obj.recipient_info.get('email'):
                return '邮箱通知'

        # 如果都没有,回退到任务的notification_type
        if obj.task:
            notification_type = obj.task.notification_type
            type_map = {
                'email': '邮箱通知',
                'webhook': 'Webhook机器人',
                'both': '两种都发送'
            }
            return type_map.get(notification_type, notification_type)

        return '-'


class UiTaskNotificationSettingSerializer(serializers.ModelSerializer):
    """UI任务通知设置序列化器"""
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    notification_config_name = serializers.CharField(source='notification_config.name', read_only=True)
    active_types = serializers.SerializerMethodField()

    class Meta:
        model = UiTaskNotificationSetting
        fields = [
            'id', 'task', 'notification_type', 'notification_type_display',
            'notification_config', 'notification_config_name', 'is_enabled',
            'notify_on_success', 'notify_on_failure', 'notify_on_timeout',
            'notify_on_error', 'custom_webhook_bots', 'active_types',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_active_types(self, obj):
        """获取激活的通知类型"""
        types = obj.get_active_notification_types()
        type_names = []
        if 'email' in types:
            type_names.append('邮箱')
        if 'webhook' in types:
            type_names.append('Webhook机器人')
        return ', '.join(type_names) if type_names else "无"

