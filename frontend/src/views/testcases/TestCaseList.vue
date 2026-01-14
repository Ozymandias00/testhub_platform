<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">测试用例</h1>
      <div class="header-actions">
        <el-button 
          v-if="selectedTestCases.length > 0" 
          type="danger" 
          @click="batchDeleteTestCases"
          :disabled="isDeleting">
          <el-icon><Delete /></el-icon>
          批量删除 ({{ selectedTestCases.length }})
        </el-button>
        <el-button type="success" @click="exportToExcel">
          <el-icon><Download /></el-icon>
          导出Excel
        </el-button>
        <el-button type="primary" @click="$router.push('/ai-generation/testcases/create')">
          <el-icon><Plus /></el-icon>
          新建用例
        </el-button>
      </div>
    </div>
    
    <div class="card-container">
      <div class="filter-bar">
        <el-row :gutter="20">
          <el-col :span="5">
            <el-input
              v-model="searchText"
              placeholder="搜索用例标题"
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-select v-model="projectFilter" placeholder="关联项目" clearable @change="handleFilter">
              <el-option
                v-for="project in projects"
                :key="project.id"
                :label="project.name"
                :value="project.id"
              />
            </el-select>
          </el-col>
          <el-col :span="3">
            <el-select v-model="priorityFilter" placeholder="优先级筛选" clearable @change="handleFilter">
              <el-option label="低" value="low" />
              <el-option label="中" value="medium" />
              <el-option label="高" value="high" />
              <el-option label="紧急" value="critical" />
            </el-select>
          </el-col>
          <el-col :span="3">
            <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="handleFilter">
              <el-option label="草稿" value="draft" />
              <el-option label="激活" value="active" />
              <el-option label="废弃" value="deprecated" />
            </el-select>
          </el-col>
        </el-row>
      </div>
      
      <el-table 
        :data="testcases" 
        v-loading="loading" 
        style="width: 100%"
        @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column type="index" label="序号" width="80" :index="getSerialNumber" />
        <el-table-column prop="title" label="用例标题" min-width="250">
          <template #default="{ row }">
            <el-link @click="goToTestCase(row.id)" type="primary">
              {{ row.title }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="project.name" label="关联项目" width="150">
          <template #default="{ row }">
            {{ row.project?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="versions" label="关联版本" width="200">
          <template #default="{ row }">
            <div v-if="row.versions && row.versions.length > 0" class="version-tags">
              <el-tag 
                v-for="version in row.versions.slice(0, 2)" 
                :key="version.id" 
                size="small" 
                :type="version.is_baseline ? 'warning' : 'info'"
                class="version-tag"
              >
                {{ version.name }}
              </el-tag>
              <el-tooltip v-if="row.versions.length > 2" :content="getVersionsTooltip(row.versions)">
                <el-tag size="small" type="info" class="version-tag">
                  +{{ row.versions.length - 2 }}
                </el-tag>
              </el-tooltip>
            </div>
            <span v-else class="no-version">未关联版本</span>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :class="`priority-tag ${row.priority}`">{{ getPriorityText(row.priority) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="test_type" label="测试类型" width="120">
          <template #default="{ row }">
            {{ getTypeText(row.test_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="author.username" label="作者" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="editTestCase(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteTestCase(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Download, Delete } from '@element-plus/icons-vue'
import api from '@/utils/api'
import dayjs from 'dayjs'
import * as XLSX from 'xlsx'

const router = useRouter()
const loading = ref(false)
const testcases = ref([])
const projects = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchText = ref('')
const projectFilter = ref('')
const priorityFilter = ref('')
const statusFilter = ref('')
const selectedTestCases = ref([])
const isDeleting = ref(false)

const fetchTestCases = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      search: searchText.value,
      project: projectFilter.value,
      priority: priorityFilter.value,
      status: statusFilter.value
    }
    const response = await api.get('/testcases/', { params })
    testcases.value = response.data.results || []
    total.value = response.data.count || 0
  } catch (error) {
    ElMessage.error('获取测试用例列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchTestCases()
}

const handleFilter = () => {
  currentPage.value = 1
  fetchTestCases()
}

const handlePageChange = () => {
  fetchTestCases()
}

const goToTestCase = (id) => {
  router.push(`/ai-generation/testcases/${id}`)
}

const editTestCase = (testcase) => {
  router.push(`/ai-generation/testcases/${testcase.id}/edit`)
}

const deleteTestCase = async (testcase) => {
  try {
    await ElMessageBox.confirm('确定要删除这个测试用例吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.delete(`/testcases/${testcase.id}/`)
    ElMessage.success('测试用例删除成功')
    fetchTestCases()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('测试用例删除失败')
    }
  }
}

// 处理选择变化
const handleSelectionChange = (selection) => {
  selectedTestCases.value = selection
}

// 获取序号
const getSerialNumber = (index) => {
  return (currentPage.value - 1) * pageSize.value + index + 1
}

// 批量删除
const batchDeleteTestCases = async () => {
  if (selectedTestCases.value.length === 0) {
    ElMessage.warning('请先选择要删除的测试用例')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedTestCases.value.length} 个测试用例吗？此操作不可恢复。`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    isDeleting.value = true
    let successCount = 0
    let failCount = 0

    // 逐个删除选中的测试用例
    for (const testcase of selectedTestCases.value) {
      try {
        await api.delete(`/testcases/${testcase.id}/`)
        successCount++
      } catch (error) {
        console.error(`删除测试用例 ${testcase.id} 失败:`, error)
        failCount++
      }
    }

    // 显示删除结果
    if (successCount > 0) {
      ElMessage.success(`成功删除 ${successCount} 个测试用例${failCount > 0 ? `，${failCount} 个失败` : ''}`)
    } else {
      ElMessage.error('删除失败')
    }

    // 清空选择并重新加载列表
    selectedTestCases.value = []
    fetchTestCases()

  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败: ' + (error.message || '未知错误'))
    }
  } finally {
    isDeleting.value = false
  }
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

const getVersionsTooltip = (versions) => {
  return versions.map(v => v.name + (v.is_baseline ? ' (基线)' : '')).join('、')
}

// 将HTML的<br>标签转换为换行符（用于Excel导出）
const convertBrToNewline = (text) => {
  if (!text) return ''
  return text.replace(/<br\s*\/?>/gi, '\n')
}

const exportToExcel = async () => {
  try {
    loading.value = true
    
    // 获取所有测试用例数据（不分页）
    const response = await api.get('/testcases/', { 
      params: { 
        page_size: 9999, // 获取所有数据
        search: searchText.value,
        project: projectFilter.value,
        priority: priorityFilter.value,
        status: statusFilter.value
      } 
    })
    
    const allTestCases = response.data.results || []
    
    if (allTestCases.length === 0) {
      ElMessage.warning('没有测试用例数据可导出')
      return
    }
    
    // 创建工作簿
    const workbook = XLSX.utils.book_new()
    
    // 准备Excel数据
    const worksheetData = [
      ['测试用例编号', '用例标题', '关联项目', '关联版本', '前置条件', '操作步骤', '预期结果', '优先级', '状态', '测试类型', '作者', '创建时间']
    ]
    
    allTestCases.forEach((testcase, index) => {
      const versions = testcase.versions && testcase.versions.length > 0 
        ? testcase.versions.map(v => v.name + (v.is_baseline ? '(基线)' : '')).join('、')
        : '未关联版本'
      
      worksheetData.push([
        `TC${String(index + 1).padStart(3, '0')}`,
        testcase.title || '',
        testcase.project?.name || '',
        versions,
        convertBrToNewline(testcase.preconditions || ''),
        convertBrToNewline(testcase.steps || ''),
        convertBrToNewline(testcase.expected_result || ''),
        getPriorityText(testcase.priority),
        getStatusText(testcase.status),
        getTypeText(testcase.test_type),
        testcase.author?.username || '',
        formatDate(testcase.created_at)
      ])
    })
    
    // 创建工作表
    const worksheet = XLSX.utils.aoa_to_sheet(worksheetData)
    
    // 设置列宽
    const colWidths = [
      { wch: 15 }, // 测试用例编号
      { wch: 30 }, // 用例标题
      { wch: 20 }, // 关联项目
      { wch: 25 }, // 关联版本
      { wch: 30 }, // 前置条件
      { wch: 40 }, // 操作步骤
      { wch: 30 }, // 预期结果
      { wch: 10 }, // 优先级
      { wch: 10 }, // 状态
      { wch: 15 }, // 测试类型
      { wch: 15 }, // 作者
      { wch: 20 }  // 创建时间
    ]
    worksheet['!cols'] = colWidths
    
    // 设置表头样式
    for (let col = 0; col < worksheetData[0].length; col++) {
      const cellAddress = XLSX.utils.encode_cell({ r: 0, c: col })
      if (!worksheet[cellAddress]) continue
      worksheet[cellAddress].s = {
        font: { bold: true },
        alignment: { horizontal: 'center', vertical: 'center', wrapText: true }
      }
    }
    
    // 设置其他行的样式
    for (let row = 1; row < worksheetData.length; row++) {
      for (let col = 0; col < worksheetData[row].length; col++) {
        const cellAddress = XLSX.utils.encode_cell({ r: row, c: col })
        if (worksheet[cellAddress]) {
          worksheet[cellAddress].s = {
            alignment: { vertical: 'top', wrapText: true }
          }
        }
      }
    }
    
    // 添加工作表到工作簿
    XLSX.utils.book_append_sheet(workbook, worksheet, '测试用例')
    
    // 生成文件名
    const fileName = `测试用例_${new Date().toISOString().slice(0, 10)}.xlsx`
    
    // 导出文件
    XLSX.writeFile(workbook, fileName)
    
    ElMessage.success('测试用例导出成功')
  } catch (error) {
    console.error('导出测试用例失败:', error)
    ElMessage.error('导出测试用例失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const fetchProjects = async () => {
  try {
    const response = await api.get('/projects/')
    projects.value = response.data.results || response.data || []
  } catch (error) {
    ElMessage.error('获取项目列表失败')
  }
}

onMounted(() => {
  fetchProjects()
  fetchTestCases()
})
</script>

<style lang="scss" scoped>
.filter-bar {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.priority-tag {
  &.low { color: #67c23a; }
  &.medium { color: #e6a23c; }
  &.high { color: #f56c6c; }
  &.critical { color: #f56c6c; font-weight: bold; }
}

.version-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  
  .version-tag {
    margin: 0;
  }
}

.no-version {
  color: #909399;
  font-size: 12px;
  font-style: italic;
}
</style>