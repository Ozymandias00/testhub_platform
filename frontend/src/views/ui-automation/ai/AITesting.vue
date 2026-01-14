<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">AI 智能测试</h1>
    </div>

    <div class="card-container">
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="section-title">任务输入</div>
          <el-form :model="taskForm" label-position="top">
            <el-form-item label="任务描述" required>
              <el-input
                v-model="taskForm.description"
                type="textarea"
                :rows="10"
                placeholder="请用自然语言描述要执行的任务，例如：&#10;1. 访问 https://www.baidu.com&#10;2. 搜索 'TestHub'&#10;3. 点击第一条搜索结果"
                maxlength="2000"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="GIF录制">
              <el-switch
                v-model="taskForm.enableGif"
                active-text="开启"
                inactive-text="关闭"
              />
              <span style="margin-left: 10px; color: #909399; font-size: 12px;">
                开启后将录制执行过程并生成GIF文件，保存到 ai_agent_history 目录
              </span>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                @click="handleRun"
                :loading="running"
                :disabled="!taskForm.description"
              >
                <el-icon><VideoPlay /></el-icon>
                开始执行
              </el-button>
              <el-button
                type="danger"
                @click="handleStop"
                :disabled="!running || analyzing"
                v-if="running"
              >
                <el-icon><SwitchButton /></el-icon>
                停止执行
              </el-button>
              <el-button
                type="success"
                @click="handleSaveAsCase"
                :disabled="!taskForm.description"
              >
                <el-icon><DocumentAdd /></el-icon>
                保存为用例
              </el-button>
            </el-form-item>
          </el-form>
          
          <el-alert
            title="提示"
            type="info"
            :closable="false"
            style="margin-top: 20px;"
          >
            <template #default>
              <div>AI 模式使用"配置中心-AI智能模式配置"中的模型（如未添加模型，请前往添加）。</div>
              <div>支持中英文任务描述，任务描述越详细，执行效果越好。</div>
            </template>
          </el-alert>
          
          <div class="section-title" style="margin-top: 20px;">执行日志</div>
          <div class="log-container" ref="logContainer">
            <div v-if="!logs && !running" class="empty-logs">
              暂无执行日志
            </div>
            <pre v-else class="log-content">{{ logs }}</pre>
          </div>
        </el-col>
        
        <el-col :span="12">
          <div class="section-title">任务明细</div>
          <div class="task-list-container">
            <div v-if="analyzing" class="analyzing-state">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>任务分析中...</span>
            </div>
            <div v-else-if="plannedTasks.length > 0">
              <div 
                v-for="task in plannedTasks" 
                :key="task.id" 
                class="task-item"
                :class="task.status"
              >
                <div class="task-status-icon">
                  <el-icon v-if="task.status === 'completed'" color="#67C23A"><CircleCheckFilled /></el-icon>
                  <el-icon v-else-if="task.status === 'in_progress'" class="is-loading" color="#409EFF"><Loading /></el-icon>
                  <el-icon v-else color="#909399"><CircleCheck /></el-icon>
                </div>
                <div class="task-content">
                  <span class="task-id">{{ task.id }}.</span>
                  <span class="task-desc">{{ task.description }}</span>
                </div>
              </div>
            </div>
            <div v-else class="empty-tasks">
              暂无任务
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 保存为用例对话框 -->
    <el-dialog v-model="showSaveDialog" title="保存为 AI 用例" width="500px">
      <el-form :model="saveForm" :rules="saveRules" ref="saveFormRef" label-width="80px">
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="saveForm.name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="saveForm.description" type="textarea" placeholder="请输入用例描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showSaveDialog = false">取消</el-button>
          <el-button type="primary" @click="confirmSaveCase" :loading="saving">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPlay, DocumentAdd, CircleCheckFilled, CircleCheck, Loading, SwitchButton } from '@element-plus/icons-vue'
import {
  runAdhocAITask,
  createAICase,
  getAIExecutionRecordDetail,
  stopAITask
} from '@/api/ui_automation'

const running = ref(false)
const analyzing = ref(false)
const saving = ref(false)
const logs = ref('')
const plannedTasks = ref([])
const currentExecutionId = ref(null)
const logContainer = ref(null)

const taskForm = reactive({
  description: '',
  enableGif: true  // GIF录制开关，默认开启
})

const showSaveDialog = ref(false)
const saveForm = reactive({
  name: '',
  description: ''
})
const saveFormRef = ref(null)

const saveRules = {
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }]
}

// 执行任务
const handleRun = async () => {
  running.value = true
  analyzing.value = true
  logs.value = '正在初始化 AI Agent...\n'
  plannedTasks.value = []

  try {
    const response = await runAdhocAITask({
      task_description: taskForm.description,
      execution_mode: 'text',  // 始终使用文本模式
      enable_gif: taskForm.enableGif  // 传递GIF录制开关状态
    })

    // analyzing.value = false // 移除过早设置，改为在轮询获取到任务列表后再取消
    
    currentExecutionId.value = response.data.execution_id
    ElMessage.success('任务开始执行')
    
    // 开始轮询日志
    pollLogs()
    
  } catch (error) {
    console.error('执行失败:', error)
    ElMessage.error('执行失败: ' + (error.response?.data?.error || error.message))
    running.value = false
    analyzing.value = false
  }
}

// 停止任务
const handleStop = async () => {
  if (!currentExecutionId.value) return
  
  try {
    await stopAITask(currentExecutionId.value)
    ElMessage.warning('正在停止任务...')
    // 不立即设置 running = false，等待轮询检测到状态变化
  } catch (error) {
    console.error('停止失败:', error)
    ElMessage.error('停止失败')
  }
}

// 轮询日志
const pollLogs = () => {
  const pollInterval = setInterval(async () => {
    if (!currentExecutionId.value) {
      clearInterval(pollInterval)
      return
    }
    
    try {
      const response = await getAIExecutionRecordDetail(currentExecutionId.value)
      const record = response.data
      
      logs.value = record.logs || ''
      plannedTasks.value = record.planned_tasks || []
      
      // 如果获取到了任务列表，则取消“分析中”状态
      if (plannedTasks.value.length > 0) {
        analyzing.value = false
      }
      
      // 滚动到底部
      nextTick(() => {
        if (logContainer.value) {
          logContainer.value.scrollTop = logContainer.value.scrollHeight
        }
      })
      
      if (record.status === 'passed' || record.status === 'failed' || record.status === 'stopped') {
        clearInterval(pollInterval)
        running.value = false
        analyzing.value = false // 确保结束时必然取消分析状态
        if (record.status === 'passed') {
          ElMessage.success('执行成功')
        } else if (record.status === 'stopped') {
          ElMessage.warning('任务已停止')
        } else {
          ElMessage.error('执行失败')
        }
      }
    } catch (error) {
      console.error('获取日志失败:', error)
      // 不停止轮询，可能是临时网络问题
    }
  }, 2000) // 每2秒轮询一次
}

// 保存为用例
const handleSaveAsCase = () => {
  showSaveDialog.value = true
  saveForm.name = ''
  saveForm.description = ''
}

const confirmSaveCase = async () => {
  if (!saveFormRef.value) return

  await saveFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        await createAICase({
          name: saveForm.name,
          description: saveForm.description,
          task_description: taskForm.description
        })

        ElMessage.success('保存成功')
        showSaveDialog.value = false
      } catch (error) {
        console.error('保存失败:', error)
        ElMessage.error('保存失败')
      } finally {
        saving.value = false
      }
    }
  })
}
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
  min-height: calc(100vh - 140px);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 15px;
  padding-left: 10px;
  border-left: 4px solid #409eff;
}

.task-list-container {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 20px;
  height: calc(100vh - 200px);
  overflow-y: auto;
  
  .task-item {
    display: flex;
    align-items: flex-start;
    padding: 10px;
    border-bottom: 1px solid #e4e7ed;
    transition: all 0.3s;
    
    &:last-child {
      border-bottom: none;
    }
    
    &.completed {
      background-color: #f0f9eb;
      .task-desc {
        color: #67c23a;
        text-decoration: line-through;
      }
    }
    
    &.in_progress {
      background-color: #ecf5ff;
      .task-desc {
        color: #409eff;
        font-weight: bold;
      }
    }
    
    .task-status-icon {
      margin-right: 10px;
      margin-top: 2px;
      font-size: 16px;
    }
    
    .task-content {
      flex: 1;
      line-height: 1.5;
      
      .task-id {
        font-weight: bold;
        margin-right: 5px;
      }
    }
  }
}

.empty-tasks {
  color: #909399;
  text-align: center;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.analyzing-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #409eff;
  
  .el-icon {
    font-size: 24px;
    margin-bottom: 10px;
  }
}

.log-container {
  background-color: #1e1e1e;
  border-radius: 4px;
  height: 300px;
  overflow-y: auto;
  padding: 15px;
  color: #fff;
  font-family: 'Consolas', 'Monaco', monospace;
  
  .empty-logs {
    color: #909399;
    text-align: center;
    margin-top: 100px;
  }
  
  .log-content {
    margin: 0;
    white-space: pre-wrap;
    word-wrap: break-word;
    font-size: 14px;
    line-height: 1.5;
  }
}
</style>
