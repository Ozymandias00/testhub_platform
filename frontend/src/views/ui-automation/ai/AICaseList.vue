<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">AI 用例管理</h1>
    </div>

    <div class="card-container">
      <div class="filter-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索用例名称或描述"
          clearable
          @input="handleSearch"
          style="width: 300px;"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <el-table :data="cases" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="用例名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="task_description" label="任务描述" min-width="300" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180" :formatter="formatDate" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="success" @click="runCase(row)">
              <el-icon><VideoPlay /></el-icon>
              执行
            </el-button>
            <el-button size="small" type="primary" @click="editCase(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="small" type="danger" @click="deleteCase(row.id)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑 AI 用例" width="600px">
      <el-form :model="editForm" :rules="formRules" ref="editFormRef" label-width="100px">
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="editForm.description" type="textarea" placeholder="请输入用例描述" />
        </el-form-item>
        <el-form-item label="任务描述" prop="task_description">
          <el-input 
            v-model="editForm.task_description" 
            type="textarea" 
            :rows="6"
            placeholder="请输入自然语言任务描述" 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="confirmEdit" :loading="saving">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, VideoPlay, Edit, Delete } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import {
  getAICases,
  updateAICase,
  deleteAICase,
  runAICase
} from '@/api/ui_automation'

const router = useRouter()
const cases = ref([])
const loading = ref(false)
const searchText = ref('')
const total = ref(0)
const pagination = reactive({
  currentPage: 1,
  pageSize: 20
})

const showEditDialog = ref(false)
const saving = ref(false)
const currentCaseId = ref(null)
const editForm = reactive({
  name: '',
  description: '',
  task_description: ''
})
const editFormRef = ref(null)

const formRules = {
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  task_description: [{ required: true, message: '请输入任务描述', trigger: 'blur' }]
}

// 加载用例列表
const loadCases = async () => {
  loading.value = true
  try {
    const response = await getAICases({
      page: pagination.currentPage,
      page_size: pagination.pageSize,
      search: searchText.value
    })

    cases.value = response.data.results || []
    total.value = response.data.count || 0
  } catch (error) {
    console.error('获取用例列表失败:', error)
    ElMessage.error('获取用例列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
  loadCases()
}

const handleSizeChange = () => {
  pagination.currentPage = 1
  loadCases()
}

const handleCurrentChange = () => {
  loadCases()
}

// 编辑用例
const editCase = (row) => {
  currentCaseId.value = row.id
  editForm.name = row.name
  editForm.description = row.description
  editForm.task_description = row.task_description
  showEditDialog.value = true
}

const confirmEdit = async () => {
  if (!editFormRef.value) return
  
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        await updateAICase(currentCaseId.value, {
          name: editForm.name,
          description: editForm.description,
          task_description: editForm.task_description
        })
        
        ElMessage.success('更新成功')
        showEditDialog.value = false
        loadCases()
      } catch (error) {
        console.error('更新失败:', error)
        ElMessage.error('更新失败')
      } finally {
        saving.value = false
      }
    }
  })
}

// 删除用例
const deleteCase = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该用例吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteAICase(id)
    ElMessage.success('删除成功')
    loadCases()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 执行用例
const runCase = async (row) => {
  try {
    await runAICase(row.id)
    ElMessage.success('用例开始执行')
    // 跳转到执行记录页面
    router.push('/ai-intelligent-mode/execution-records')
  } catch (error) {
    console.error('执行失败:', error)
    ElMessage.error('执行失败')
  }
}

const formatDate = (row, column, cellValue) => {
  if (!cellValue) return ''
  return new Date(cellValue).toLocaleString()
}

onMounted(() => {
  loadCases()
})
</script>

<style lang="scss" scoped>
.page-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  .page-title {
    font-size: 20px;
    font-weight: 600;
    margin: 0;
  }
}

.card-container {
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.filter-bar {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
