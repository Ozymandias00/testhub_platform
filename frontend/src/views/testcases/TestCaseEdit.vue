<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">编辑测试用例</h1>
    </div>
    
    <div class="card-container" v-if="!loading">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="用例标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入测试用例标题" />
        </el-form-item>
        
        <el-form-item label="用例描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入用例描述"
          />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="归属项目" prop="project_id">
              <el-select 
                v-model="form.project_id" 
                placeholder="请选择项目"
                clearable
                filterable
                @change="onProjectChange"
              >
                <el-option
                  v-for="project in projects"
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="form.priority" placeholder="请选择优先级">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
                <el-option label="紧急" value="critical" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="测试类型" prop="test_type">
              <el-select v-model="form.test_type" placeholder="请选择测试类型">
                <el-option label="功能测试" value="functional" />
                <el-option label="集成测试" value="integration" />
                <el-option label="API测试" value="api" />
                <el-option label="UI测试" value="ui" />
                <el-option label="性能测试" value="performance" />
                <el-option label="安全测试" value="security" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="form.status" placeholder="请选择状态">
                <el-option label="草稿" value="draft" />
                <el-option label="激活" value="active" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联版本">
              <el-select 
                v-model="form.version_ids" 
                placeholder="请选择版本（可多选）" 
                multiple
                clearable
                filterable
                @change="onVersionChange"
              >
                <el-option
                  v-for="version in projectVersions"
                  :key="version.id"
                  :label="version.name + (version.is_baseline ? ' (基线)' : '')"
                  :value="version.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="前置条件" prop="preconditions">
          <el-input
            v-model="form.preconditions"
            type="textarea"
            :rows="3"
            placeholder="请输入前置条件"
          />
        </el-form-item>
        
        <el-form-item label="操作步骤" prop="steps">
          <el-input
            v-model="form.steps"
            type="textarea"
            :rows="6"
            maxlength="1000"
            show-word-limit
            placeholder="请输入详细的操作步骤，如：&#10;1. 打开登录页面&#10;2. 输入用户名和密码&#10;3. 点击登录按钮&#10;4. 验证登录结果"
          />
        </el-form-item>
        
        <el-form-item label="预期结果" prop="expected_result">
          <el-input
            v-model="form.expected_result"
            type="textarea"
            :rows="3"
            placeholder="请输入整体预期结果"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            保存修改
          </el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="card-container" v-else>
      <el-skeleton :rows="10" animated />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const route = useRoute()
const router = useRouter()
const formRef = ref()
const loading = ref(true)
const submitting = ref(false)
const projects = ref([])
const projectVersions = ref([])

const form = reactive({
  title: '',
  description: '',
  project_id: null,
  priority: 'medium',
  test_type: 'functional',
  status: 'draft',
  preconditions: '',
  steps: '',
  expected_result: '',
  version_ids: []
})

const rules = {
  title: [
    { required: true, message: '请输入用例标题', trigger: 'blur' },
    { min: 5, max: 500, message: '标题长度在 5 到 500 个字符', trigger: 'blur' }
  ],
  expected_result: [
    { required: true, message: '请输入预期结果', trigger: 'blur' }
  ],
  steps: [
    { max: 1000, message: '操作步骤不能超过1000个字符', trigger: 'blur' }
  ]
}

// 将HTML的<br>标签转换为换行符（用于编辑时显示）
const convertBrToNewline = (text) => {
  if (!text) return ''
  return text.replace(/<br\s*\/?>/gi, '\n')
}

// 将换行符转换为HTML的<br>标签（用于保存）
const convertNewlineToBr = (text) => {
  if (!text) return ''
  return text.replace(/\n/g, '<br>')
}

const fetchProjects = async () => {
  try {
    const response = await api.get('/projects/list/')
    projects.value = response.data.results || []
  } catch (error) {
    ElMessage.error('获取项目列表失败')
  }
}

const fetchProjectVersions = async (projectId) => {
  if (!projectId) {
    projectVersions.value = []
    return
  }
  
  try {
    const response = await api.get(`/versions/projects/${projectId}/versions/`)
    projectVersions.value = response.data || []
  } catch (error) {
    console.error('获取项目版本失败:', error)
    ElMessage.error('获取项目版本失败')
    projectVersions.value = []
  }
}

const onProjectChange = (projectId) => {
  // 当项目改变时，清空版本选择并重新获取版本列表
  form.version_ids = []
  fetchProjectVersions(projectId)
}

const onVersionChange = () => {
  // 版本选择变化的处理逻辑（如果需要的话）
}

const fetchTestCase = async () => {
  try {
    const response = await api.get(`/testcases/${route.params.id}/`)
    const testcase = response.data
    
    // 填充表单数据
    form.title = testcase.title
    form.description = testcase.description
    form.project_id = testcase.project?.id || null
    form.priority = testcase.priority
    form.test_type = testcase.test_type
    form.status = testcase.status
    form.preconditions = convertBrToNewline(testcase.preconditions || '')
    form.expected_result = convertBrToNewline(testcase.expected_result || '')

    // 填充操作步骤数据（将<br>转换为换行符）
    form.steps = convertBrToNewline(testcase.steps || '')
    
    // 填充版本关联数据
    form.version_ids = testcase.versions ? testcase.versions.map(v => v.id) : []
    
    // 如果有项目，获取该项目的版本列表
    if (form.project_id) {
      await fetchProjectVersions(form.project_id)
    }
    
    loading.value = false
  } catch (error) {
    ElMessage.error('获取用例详情失败')
    router.back()
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        // 在提交前将换行符转换回<br>标签
        const submitData = {
          ...form,
          preconditions: convertNewlineToBr(form.preconditions || ''),
          steps: convertNewlineToBr(form.steps || ''),
          expected_result: convertNewlineToBr(form.expected_result || '')
        }

        await api.put(`/testcases/${route.params.id}/`, submitData)
        ElMessage.success('测试用例修改成功')
        router.push(`/ai-generation/testcases/${route.params.id}`)
      } catch (error) {
        ElMessage.error('测试用例修改失败')
        console.error('提交错误:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(async () => {
  await fetchProjects()
  await fetchTestCase()  // fetchTestCase中会根据项目获取版本列表
})
</script>