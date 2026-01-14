<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">用例详情</h1>
      <div>
        <el-button @click="$router.back()">返回</el-button>
        <el-button type="primary" @click="editTestCase">编辑</el-button>
      </div>
    </div>
    
    <div class="card-container" v-if="testcase">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="用例标题" :span="2">{{ testcase.title }}</el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :class="`priority-tag ${testcase.priority}`">{{ getPriorityText(testcase.priority) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(testcase.status)">{{ getStatusText(testcase.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="测试类型">{{ getTypeText(testcase.test_type) }}</el-descriptions-item>
        <el-descriptions-item label="归属项目">{{ testcase.project?.name || '未关联项目' }}</el-descriptions-item>
        <el-descriptions-item label="关联版本" :span="2">
          <div v-if="testcase.versions && testcase.versions.length > 0" class="version-tags">
            <el-tag 
              v-for="version in testcase.versions" 
              :key="version.id" 
              size="small" 
              :type="version.is_baseline ? 'warning' : 'info'"
              class="version-tag"
            >
              {{ version.name }}
            </el-tag>
          </div>
          <span v-else class="no-version">未关联版本</span>
        </el-descriptions-item>
        <el-descriptions-item label="作者">{{ testcase.author?.username }}</el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">{{ formatDate(testcase.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="用例描述" :span="2">{{ testcase.description || '暂无描述' }}</el-descriptions-item>
        <el-descriptions-item label="前置条件" :span="2">
          <div v-html="testcase.preconditions || '无'"></div>
        </el-descriptions-item>
        <el-descriptions-item label="操作步骤" :span="2">
          <div class="steps-content" v-html="testcase.steps || '无'"></div>
        </el-descriptions-item>
        <el-descriptions-item label="预期结果" :span="2">
          <div v-html="testcase.expected_result || '无'"></div>
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const testcase = ref(null)

const fetchTestCase = async () => {
  try {
    const response = await api.get(`/testcases/${route.params.id}/`)
    testcase.value = response.data
  } catch (error) {
    ElMessage.error('获取用例详情失败')
  }
}

const editTestCase = () => {
  router.push(`/ai-generation/testcases/${route.params.id}/edit`)
}

const getPriorityText = (priority) => {
  const textMap = {
    low: '低',
    medium: '中',
    high: '高',
    critical: '紧急'
  }
  return textMap[priority] || priority
}

const getStatusType = (status) => {
  const typeMap = {
    draft: 'info',
    active: 'success',
    deprecated: 'warning'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    draft: '草稿',
    active: '激活',
    deprecated: '废弃'
  }
  return textMap[status] || status
}

const getTypeText = (type) => {
  const textMap = {
    functional: '功能测试',
    integration: '集成测试',
    api: 'API测试',
    ui: 'UI测试',
    performance: '性能测试',
    security: '安全测试'
  }
  return textMap[type] || '-'
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

onMounted(() => {
  fetchTestCase()
})
</script>

<style lang="scss" scoped>
.priority-tag {
  &.low { color: #67c23a; }
  &.medium { color: #e6a23c; }
  &.high { color: #f56c6c; }
  &.critical { color: #f56c6c; font-weight: bold; }
}

.version-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  
  .version-tag {
    margin: 0;
  }
}

.no-version {
  color: #909399;
  font-size: 14px;
  font-style: italic;
}

.steps-content {
  white-space: pre-wrap;
  line-height: 1.6;
  color: #303133;
  font-family: inherit;
}
</style>