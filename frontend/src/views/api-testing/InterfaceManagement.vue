<template>
  <div class="interface-management">
    <div class="interface-layout">
      <!-- 左侧集合树 -->
      <div class="sidebar">
        <div class="sidebar-header">
          <el-select v-model="selectedProject" placeholder="选择项目" @change="onProjectChange">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
          <div class="header-actions">
            <el-button type="primary" size="small" @click="showCreateCollectionDialog = true" title="创建集合">
              <el-icon><Folder /></el-icon>
            </el-button>
            <el-button type="success" size="small" @click="createEmptyRequest" title="添加接口">
              <el-icon><Plus /></el-icon>
            </el-button>
          </div>
        </div>
        
        <div class="collection-tree">
          <el-tree
            ref="treeRef"
            :data="collections"
            :props="treeProps"
            node-key="id"
            :expand-on-click-node="false"
            :default-expanded-keys="expandedKeys"
            @node-click="onNodeClick"
            @node-contextmenu="onNodeRightClick"
            @node-expand="onNodeExpand"
            @node-collapse="onNodeCollapse"
          >
            <template #default="{ node, data }">
              <div class="tree-node">
                <el-icon v-if="data.type === 'collection'">
                  <Folder />
                </el-icon>
                <el-icon v-else>
                  <Document />
                </el-icon>
                
                <!-- 集合名称编辑 -->
                <div v-if="data.type === 'collection' && editingNodeId === data.id" class="node-edit">
                  <el-input
                    v-model="editingNodeName"
                    size="small"
                    @blur="saveCollectionName"
                    @keyup.enter="saveCollectionName"
                    @keyup.esc="cancelEdit"
                    ref="editInputRef"
                  />
                </div>
                
                <!-- 普通显示模式 -->
                <span v-else class="node-label">{{ node.label }}</span>
                
                <span v-if="data.type === 'request' && data.request_type !== 'WEBSOCKET'" class="method-tag" :class="data.method?.toLowerCase()">
                  {{ data.method }}
                </span>
              </div>
            </template>
          </el-tree>
        </div>
      </div>

      <!-- 右侧请求详情 -->
      <div class="main-content">
        <div v-if="!selectedRequest" class="empty-state">
          <el-empty description="请选择一个接口查看详情，或点击上方绿色按钮创建新接口">
            <el-button type="primary" @click="createEmptyRequest">创建新接口</el-button>
          </el-empty>
        </div>
        
        <div v-else class="request-detail">
          <!-- 请求基本信息 -->
          <div class="request-header">
            <div class="request-line">
              <!-- HTTP接口显示方法选择器 -->
              <el-select 
                v-if="!selectedRequest || selectedRequest.request_type !== 'WEBSOCKET'" 
                v-model="selectedRequest.method" 
                style="width: 100px;"
              >
                <el-option v-for="method in availableMethods" :key="method" :label="method" :value="method" />
              </el-select>
              
              <el-input
                v-model="selectedRequest.url"
                placeholder="输入请求URL"
                class="url-input"
                :class="{ 'websocket-url': selectedRequest && selectedRequest.request_type === 'WEBSOCKET' }"
              >
                <template #prepend>
                  <el-select v-model="selectedEnvironment" placeholder="环境" style="width: 120px;">
                    <el-option label="无环境" :value="null" />
                    <el-option
                      v-for="env in environments"
                      :key="env.id"
                      :label="env.name"
                      :value="env.id"
                    />
                  </el-select>
                </template>
              </el-input>
              
              <!-- WebSocket连接按钮 -->
              <el-button 
                v-if="selectedRequest && selectedRequest.request_type === 'WEBSOCKET'"
                :type="websocketConnectionStatus === 'disconnected' ? 'primary' : 'info'"
                :loading="websocketConnectionStatus === 'connecting'"
                @click="toggleWebSocketConnection"
              >
                <span v-if="websocketConnectionStatus === 'disconnected'">连接</span>
                <span v-else-if="websocketConnectionStatus === 'connecting'">连接中</span>
                <span v-else>关闭连接</span>
              </el-button>
              
              <!-- HTTP发送按钮 -->
              <el-button 
                v-else
                type="primary" 
                @click="sendRequest" 
                :loading="sending"
              >
                发送
              </el-button>
            </div>
            
            <div class="request-name">
              <el-input
                v-model="selectedRequest.name"
                placeholder="请求名称"
                size="small"
                style="width: 300px;"
              />
              <el-button size="small" @click="saveRequest" :loading="saving" ref="saveButtonRef">
                保存
              </el-button>
            </div>
          </div>

          <!-- 请求配置 -->
          <el-tabs v-model="activeTab" class="request-tabs">
            <el-tab-pane label="Params" name="params">
              <KeyValueEditor
                v-model="selectedRequest.params"
                placeholder-key="参数名"
                placeholder-value="参数值"
              />
            </el-tab-pane>
            
            <el-tab-pane label="Headers" name="headers">
              <KeyValueEditor
                ref="headersEditorRef"
                v-model="selectedRequest.headers"
                placeholder-key="Header名"
                placeholder-value="Header值"
                @update:modelValue="onHeadersUpdate"
              />
            </el-tab-pane>
            
            <el-tab-pane label="Body" name="body" v-if="hasBody">
              <div class="body-container">
                <el-radio-group v-model="bodyType" @change="onBodyTypeChange">
                  <el-radio value="none">none</el-radio>
                  <el-radio value="form-data">form-data</el-radio>
                  <el-radio value="x-www-form-urlencoded">x-www-form-urlencoded</el-radio>
                  <el-radio value="raw">raw</el-radio>
                  <el-radio value="binary">binary</el-radio>
                </el-radio-group>
                
                <div v-if="bodyType === 'form-data'" class="body-content">
                  <KeyValueEditor
                    v-model="formData"
                    placeholder-key="键"
                    placeholder-value="值"
                    :show-file="true"
                  />
                </div>
                
                <div v-else-if="bodyType === 'x-www-form-urlencoded'" class="body-content">
                  <KeyValueEditor
                    v-model="formUrlEncoded"
                    placeholder-key="键"
                    placeholder-value="值"
                  />
                </div>
                
                <div v-else-if="bodyType === 'raw'" class="body-content">
                  <div class="raw-options">
                    <el-select v-model="rawType" style="width: 150px;">
                      <el-option label="Text" value="text" />
                      <el-option label="JSON" value="json" />
                      <el-option label="HTML" value="html" />
                      <el-option label="XML" value="xml" />
                    </el-select>
                  </div>
                  <el-input
                    v-model="rawBody"
                    type="textarea"
                    :rows="10"
                    placeholder="请输入请求体内容"
                    class="raw-body"
                  />
                </div>
              </div>
            </el-tab-pane>
            
            <!-- HTTP接口专用标签页 -->
            <template v-if="!selectedRequest || selectedRequest.request_type !== 'WEBSOCKET'">
              <el-tab-pane label="Pre-request Script" name="pre-script">
                <el-input
                  v-model="selectedRequest.pre_request_script"
                  type="textarea"
                  :rows="10"
                  placeholder="// 请求前脚本，使用JavaScript语法"
                />
              </el-tab-pane>
              
              <el-tab-pane label="Tests" name="tests">
                <el-input
                  v-model="selectedRequest.post_request_script"
                  type="textarea"
                  :rows="10"
                  placeholder="// 请求后脚本和测试，使用JavaScript语法"
                />
              </el-tab-pane>
              
              <el-tab-pane label="断言" name="assertions">
                <div class="assertions-editor">
                  <div class="assertions-header">
                    <el-button size="small" type="primary" @click="addAssertion">
                      <el-icon><Plus /></el-icon>
                      添加断言
                    </el-button>
                  </div>
                  
                  <div class="assertions-list">
                    <div 
                      v-for="(assertion, index) in selectedRequest.assertions" 
                      :key="index" 
                      class="assertion-item"
                    >
                      <div class="assertion-header">
                        <el-input 
                          v-model="assertion.name" 
                          placeholder="断言名称" 
                          size="small" 
                          class="assertion-name"
                        />
                        <el-button 
                          size="small" 
                          type="danger" 
                          @click="removeAssertion(index)"
                          circle
                        >
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </div>
                      
                      <div class="assertion-config">
                        <el-select 
                          v-model="assertion.type" 
                          placeholder="选择断言类型" 
                          size="small"
                          @change="onAssertionTypeChange(assertion)"
                        >
                          <el-option label="状态码" value="status_code" />
                          <el-option label="响应时间" value="response_time" />
                          <el-option label="包含文本" value="contains" />
                          <el-option label="JSON路径" value="json_path" />
                          <el-option label="响应头" value="header" />
                          <el-option label="完全匹配" value="equals" />
                        </el-select>
                        
                        <div class="assertion-params" v-if="assertion.type">
                          <!-- 状态码断言 -->
                          <div v-if="assertion.type === 'status_code'">
                            <el-input-number 
                              v-model="assertion.expected" 
                              :min="100" 
                              :max="599" 
                              size="small"
                              placeholder="期望状态码"
                            />
                          </div>
                          
                          <!-- 响应时间断言 -->
                          <div v-else-if="assertion.type === 'response_time'">
                            <el-input-number 
                              v-model="assertion.expected" 
                              :min="1" 
                              size="small"
                              placeholder="最大响应时间(ms)"
                            />
                          </div>
                          
                          <!-- 包含文本断言 -->
                          <div v-else-if="assertion.type === 'contains'">
                            <el-input 
                              v-model="assertion.expected" 
                              placeholder="期望包含的文本" 
                              size="small"
                            />
                          </div>
                          
                          <!-- JSON路径断言 -->
                          <div v-else-if="assertion.type === 'json_path'">
                            <el-input 
                              v-model="assertion.json_path" 
                              placeholder="JSON路径表达式" 
                              size="small"
                              class="assertion-input"
                            />
                            <el-input 
                              v-model="assertion.expected" 
                              placeholder="期望值" 
                              size="small"
                              class="assertion-input"
                            />
                          </div>
                          
                          <!-- 响应头断言 -->
                          <div v-else-if="assertion.type === 'header'">
                            <el-input 
                              v-model="assertion.header_name" 
                              placeholder="响应头名称" 
                              size="small"
                              class="assertion-input"
                            />
                            <el-input 
                              v-model="assertion.expected_value" 
                              placeholder="期望值" 
                              size="small"
                              class="assertion-input"
                            />
                          </div>
                          
                          <!-- 完全匹配断言 -->
                          <div v-else-if="assertion.type === 'equals'">
                            <el-input 
                              v-model="assertion.expected" 
                              placeholder="期望完全匹配的文本" 
                              size="small"
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div v-if="!selectedRequest.assertions || selectedRequest.assertions.length === 0" class="no-assertions">
                      <p>暂无断言配置</p>
                      <el-button size="small" type="primary" @click="addAssertion">
                        <el-icon><Plus /></el-icon>
                        添加第一个断言
                      </el-button>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
            </template>
            
            <!-- WebSocket接口专用标签页 -->
            <template v-else-if="selectedRequest && selectedRequest.request_type === 'WEBSOCKET'">
              <el-tab-pane label="Message" name="message">
                <div class="message-container">
                  <div class="message-input-section">
                    <el-select 
                      v-model="websocketMessageType" 
                      placeholder="选择消息类型" 
                      style="width: 150px; margin-bottom: 15px;"
                    >
                      <el-option label="Text" value="text" />
                      <el-option label="JSON" value="json" />
                      <el-option label="Binary" value="binary" />
                    </el-select>
                    
                    <div v-if="websocketMessageType === 'text' || websocketMessageType === 'json'">
                      <el-input
                        v-model="websocketMessageContent"
                        type="textarea"
                        :rows="6"
                        placeholder="请输入要发送的WebSocket消息内容"
                      />
                    </div>
                    
                    <div v-else-if="websocketMessageType === 'binary'">
                      <el-upload
                        drag
                        action="#"
                        :auto-upload="false"
                        :show-file-list="false"
                        :on-change="handleWebSocketFileUpload"
                      >
                        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                        <div class="el-upload__text">
                          将二进制文件拖到此处，或<em>点击上传</em>
                        </div>
                      </el-upload>
                      <div v-if="websocketBinaryFile" class="uploaded-file">
                        <span>{{ websocketBinaryFile.name }}</span>
                        <el-button size="small" type="danger" @click="clearWebSocketBinaryFile">清除</el-button>
                      </div>
                    </div>
                    
                    <div class="message-actions" style="margin-top: 15px;">
                      <el-button type="primary" @click="sendWebSocketMessage">
                        发送消息
                      </el-button>
                      <el-button @click="clearWebSocketMessage">
                        清空消息
                      </el-button>
                    </div>
                  </div>
                  
                  <!-- WebSocket消息历史记录 -->
                  <div class="websocket-response-section" v-if="websocketMessages.length > 0">
                    <h3>消息历史</h3>
                    <div class="websocket-messages">
                      <div 
                        v-for="(msg, index) in websocketMessages.slice().reverse()" 
                        :key="index" 
                        class="websocket-message-item"
                        :class="msg.type"
                      >
                        <div class="message-header">
                          <span class="message-type" :class="msg.type">
                            {{ msg.type === 'sent' ? '↑ 发送' : 
                               msg.type === 'connected' ? '✅连接成功' : 
                               msg.type === 'info' ? 'ℹ️信息' : 
                               msg.type === 'error' ? '❌错误' : '↓ 接收' }}
                          </span>
                          <span class="message-time">{{ msg.timestamp }}</span>
                        </div>
                        <div class="message-content">
                          <pre v-if="msg.type === 'received' && isJsonString(msg.content)">{{ formatJson(msg.content) }}</pre>
                          <pre v-else>{{ msg.content }}</pre>
                        </div>
                      </div>
                    </div>
                    <div class="message-actions">
                      <el-button size="small" @click="clearWebSocketMessages">清空历史</el-button>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
            </template>
          </el-tabs>

          <!-- 响应区域 -->
          <div v-if="response" class="response-section">
            <div class="response-header">
              <h3>响应</h3>
              <div class="response-info">
                <el-tag :type="getStatusType(response.status_code)">
                  {{ response.status_code }}
                </el-tag>
                <span class="response-time">{{ response.response_time?.toFixed(0) }}ms</span>
              </div>
            </div>
            
            <el-tabs v-model="responseActiveTab">
              <el-tab-pane label="Body" name="body">
                <div class="response-body">
                  <div class="response-actions">
                    <el-button-group>
                      <el-button size="small" @click="formatResponse">格式化</el-button>
                      <el-button size="small" @click="copyResponse">复制</el-button>
                    </el-button-group>
                  </div>
                  <pre class="response-content">{{ responseBody }}</pre>
                </div>
              </el-tab-pane>
              
              <el-tab-pane label="Headers" name="headers">
                <div class="response-headers">
                  <div v-for="(value, key) in response.response_data?.headers" :key="key" class="header-row">
                    <strong>{{ key }}:</strong> {{ value }}
                  </div>
                </div>
              </el-tab-pane>
              
              <el-tab-pane label="断言结果" name="assertions" v-if="response.assertions_results && response.assertions_results.length > 0">
                <div class="assertions-results">
                  <div 
                    v-for="(result, index) in response.assertions_results" 
                    :key="index" 
                    class="assertion-result-item"
                    :class="{ 'passed': result.passed, 'failed': !result.passed }"
                  >
                    <div class="assertion-result-header">
                      <el-tag :type="result.passed ? 'success' : 'danger'" size="small">
                        {{ result.passed ? '通过' : '失败' }}
                      </el-tag>
                      <span class="assertion-name">{{ result.name }}</span>
                    </div>
                    <div class="assertion-result-details">
                      <div class="result-row">
                        <span class="label">期望:</span>
                        <span class="value">{{ result.expected !== null && result.expected !== undefined ? result.expected : '未设置' }}</span>
                      </div>
                      <div class="result-row">
                        <span class="label">实际:</span>
                        <span class="value">{{ result.actual !== null && result.actual !== undefined ? result.actual : '未获取到' }}</span>
                      </div>
                      <div class="result-row" v-if="result.error">
                        <span class="label">错误:</span>
                        <span class="value error">{{ result.error }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建集合对话框 -->
    <el-dialog v-model="showCreateCollectionDialog" title="创建集合" width="500px">
      <el-form ref="collectionFormRef" :model="collectionForm" :rules="collectionRules" label-width="80px">
        <el-form-item label="集合名称" prop="name">
          <el-input v-model="collectionForm.name" placeholder="请输入集合名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="collectionForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="父级集合" prop="parent">
          <el-select v-model="collectionForm.parent" placeholder="选择父级集合（可选）" clearable>
            <el-option
              v-for="collection in flatCollections"
              :key="collection.id"
              :label="collection.name"
              :value="collection.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateCollectionDialog = false">取消</el-button>
        <el-button type="primary" @click="createCollection">创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑集合对话框 -->
    <el-dialog v-model="showEditCollectionDialog" title="编辑集合" width="500px">
      <el-form ref="editCollectionFormRef" :model="editCollectionForm" :rules="collectionRules" label-width="80px">
        <el-form-item label="集合名称" prop="name">
          <el-input v-model="editCollectionForm.name" placeholder="请输入集合名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="editCollectionForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="父级集合" prop="parent">
          <el-select v-model="editCollectionForm.parent" placeholder="选择父级集合（可选）" clearable>
            <el-option
              v-for="collection in flatCollections.filter(c => c.id !== editCollectionForm.id)"
              :key="collection.id"
              :label="collection.name"
              :value="collection.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showEditCollectionDialog = false">取消</el-button>
        <el-button type="primary" @click="updateCollection">保存</el-button>
      </template>
    </el-dialog>

    <!-- 右键菜单 -->
    <ul v-show="showContextMenu" class="context-menu" :style="{ left: contextMenuX + 'px', top: contextMenuY + 'px' }">
      <li @click="addRequest">添加请求</li>
      <li @click="addCollection">添加子集合</li>
      <li @click="editNode">编辑</li>
      <li @click="deleteNode">删除</li>
    </ul>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Folder, Document } from '@element-plus/icons-vue'
import api from '@/utils/api'
import KeyValueEditor from './components/KeyValueEditor.vue'

const treeRef = ref(null)
const expandedKeys = ref([])
const projects = ref([])
const selectedProject = ref(null)
const collections = ref([])
const flatCollections = ref([])
const environments = ref([])
const selectedEnvironment = ref(null)
const selectedRequest = ref(null)
const response = ref(null)
const sending = ref(false)
const saving = ref(false)
const activeTab = ref('params')
const responseActiveTab = ref('body')
const showCreateCollectionDialog = ref(false)
const showEditCollectionDialog = ref(false)
const showContextMenu = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const rightClickedNode = ref(null)
const headersEditorRef = ref(null)
const editingNodeId = ref(null)
const editingNodeName = ref('')
const editInputRef = ref(null)

// 辅助函数：将对象或数组转换为键值对数组（用于KeyValueEditor组件）
const convertObjectToKeyValueArray = (obj) => {
  if (!obj) return []
  
  // 如果已经是数组格式（新的完整格式），直接返回
  if (Array.isArray(obj)) {
    console.log('Input is already array format:', obj)
    return obj.map(item => ({
      key: item.key || '',
      value: item.value || '',
      enabled: item.enabled !== false,
      description: item.description || ''
    }))
  }
  
  // 如果是对象格式（旧的简单key-value格式），转换为数组
  if (typeof obj === 'object') {
    console.log('Converting object to array:', obj)
    return Object.entries(obj).map(([key, value]) => ({
      key,
      value: String(value),
      enabled: true,
      description: ''
    }))
  }
  
  return []
}

// 辅助函数：将键值对数组转换为对象（保存时使用）
const convertKeyValueArrayToObject = (input) => {
  console.log('convertKeyValueArrayToObject input:', input)
  
  // 如果输入已经是普通对象，直接返回
  if (input && typeof input === 'object' && !Array.isArray(input)) {
    console.log('Input is already an object, returning as-is')
    return input
  }
  
  // 如果输入是数组，转换为对象
  if (!Array.isArray(input)) return {}
  
  const obj = {}
  input.forEach(item => {
    console.log('Processing item:', item, 'enabled:', item.enabled)
    if (item.enabled !== false && item.key) {
      obj[item.key] = item.value || ''
      console.log('Added to obj:', item.key, '=', item.value)
    }
  })
  console.log('convertKeyValueArrayToObject output:', obj)
  return obj
}

const httpMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
const websocketMethods = ['CONNECT', 'SUBSCRIBE', 'UNSUBSCRIBE', 'SEND', 'PING', 'PONG']

const availableMethods = computed(() => {
  return selectedRequest.value && selectedRequest.value.request_type === 'WEBSOCKET' 
    ? websocketMethods 
    : httpMethods
})

// WebSocket消息相关数据
const websocketMessageType = ref('text')
const websocketMessageContent = ref('')
const websocketBinaryFile = ref(null)
const websocketConnectionStatus = ref('disconnected') // disconnected, connecting, connected
const websocketConnection = ref(null)
const websocketMessages = ref([]) // WebSocket消息历史记录
const bodyType = ref('none')
const rawType = ref('json')
const formData = ref({})
const formUrlEncoded = ref({})
const rawBody = ref('')

const treeProps = {
  children: 'children',
  label: 'name'
}

const collectionForm = reactive({
  name: '',
  description: '',
  parent: null
})

const editCollectionForm = reactive({
  id: null,
  name: '',
  description: '',
  parent: null
})

const collectionRules = {
  name: [{ required: true, message: '请输入集合名称', trigger: 'blur' }]
}

const hasBody = computed(() => {
  return selectedRequest.value && ['POST', 'PUT', 'PATCH'].includes(selectedRequest.value.method)
})

const responseBody = computed(() => {
  if (!response.value?.response_data) return ''
  
  try {
    if (response.value.response_data.json) {
      return JSON.stringify(response.value.response_data.json, null, 2)
    } else {
      return response.value.response_data.body || ''
    }
  } catch (e) {
    return response.value.response_data.body || ''
  }
})

const getStatusType = (status) => {
  if (status >= 200 && status < 300) return 'success'
  if (status >= 300 && status < 400) return 'warning'
  if (status >= 400) return 'danger'
  return 'info'
}

const loadProjects = async () => {
  try {
    const res = await api.get('/api-testing/projects/')
    projects.value = res.data.results || res.data
    if (projects.value.length > 0 && !selectedProject.value) {
      selectedProject.value = projects.value[0].id
      await onProjectChange()
    }
  } catch (error) {
    ElMessage.error('加载项目失败')
  }
}

const loadCollections = async (preserveExpandState = true) => {
  if (!selectedProject.value) return
  
  try {
    const res = await api.get('/api-testing/collections/', {
      params: { project: selectedProject.value }
    })
    const collectionsData = res.data.results || res.data
    
    // 构建树形结构
    collections.value = buildTree(collectionsData)
    flatCollections.value = collectionsData
    
    // 加载每个集合的请求
    await loadRequests()
    
    // 如果不保留展开状态，清空展开键
    if (!preserveExpandState) {
      expandedKeys.value = []
    }
    
  } catch (error) {
    ElMessage.error('加载集合失败')
  }
}

const loadRequests = async () => {
  if (!selectedProject.value) return
  
  try {
    const res = await api.get('/api-testing/requests/')
    const requests = res.data.results || res.data
    
    // 清空所有集合的子节点（请求）
    collections.value.forEach(collection => {
      clearCollectionChildren(collection)
    })
    
    // 将请求添加到对应集合中
    requests.forEach(request => {
      const collection = findCollectionById(collections.value, request.collection)
      if (collection) {
        if (!collection.children) collection.children = []
        collection.children.push({
          ...request,
          type: 'request',
          name: request.name
        })
      }
    })
  } catch (error) {
    ElMessage.error('加载请求失败')
  }
}

const clearCollectionChildren = (collection) => {
  if (collection.children) {
    collection.children = collection.children.filter(child => child.type === 'collection')
    collection.children.forEach(child => clearCollectionChildren(child))
  }
}

const loadEnvironments = async () => {
  try {
    // 获取全局环境 + 当前项目环境，不传递project参数
    const res = await api.get('/api-testing/environments/')
    const allEnvironments = res.data.results || res.data
    
    // 过滤全局环境和当前项目环境
    environments.value = allEnvironments.filter(env => 
      env.scope === 'GLOBAL' || 
      (env.scope === 'LOCAL' && (!selectedProject.value || env.project === selectedProject.value))
    )
  } catch (error) {
    ElMessage.error('加载环境失败')
  }
}

const buildTree = (items) => {
  const map = {}
  const roots = []
  
  items.forEach(item => {
    map[item.id] = { ...item, type: 'collection', children: [] }
  })
  
  items.forEach(item => {
    if (item.parent) {
      if (map[item.parent]) {
        map[item.parent].children.push(map[item.id])
      }
    } else {
      roots.push(map[item.id])
    }
  })
  
  return roots
}

const findCollectionById = (collections, id) => {
  for (const collection of collections) {
    if (collection.id === id) return collection
    if (collection.children) {
      const found = findCollectionById(collection.children, id)
      if (found) return found
    }
  }
  return null
}

const onProjectChange = async () => {
  await Promise.all([loadCollections(false), loadEnvironments()])
}

const onNodeClick = (data) => {
  if (data.type === 'request') {
    console.log('onNodeClick - original data.headers:', data.headers)
    const convertedHeaders = convertObjectToKeyValueArray(data.headers || {})
    console.log('onNodeClick - converted headers:', convertedHeaders)
    
    // 初始化currentHeaders
    currentHeaders.value = data.headers || {}
    console.log('onNodeClick - initialized currentHeaders:', currentHeaders.value)
    
    selectedRequest.value = {
      ...data,
      params: convertObjectToKeyValueArray(data.params || {}),
      headers: convertedHeaders,
      body: data.body || {},
      auth: data.auth || {}
    }
    
    console.log('onNodeClick - selectedRequest.value.headers:', selectedRequest.value.headers)

    // 解析body数据
    if (data.body && data.body.type) {
      if (data.body.type === 'json' && data.body.data) {
        bodyType.value = 'raw'
        rawType.value = 'json'
        rawBody.value = JSON.stringify(data.body.data, null, 2)
      } else if (data.body.type === 'raw' && data.body.data) {
        bodyType.value = 'raw'
        rawType.value = 'text'
        rawBody.value = data.body.data
      } else if (data.body.type === 'form-data') {
        bodyType.value = 'form-data'
        formData.value = data.body.data || {}
      } else if (data.body.type === 'x-www-form-urlencoded') {
        bodyType.value = 'x-www-form-urlencoded'
        formUrlEncoded.value = data.body.data || {}
      } else if (data.body.type === 'binary') {
        bodyType.value = 'binary'
      } else {
        bodyType.value = 'none'
        rawBody.value = ''
      }
    } else {
      bodyType.value = 'none'
      rawBody.value = ''
    }
    
    response.value = null
  }
}

const onNodeRightClick = (event, data) => {
  event.preventDefault()
  rightClickedNode.value = data
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
  showContextMenu.value = true
  
  nextTick(() => {
    document.addEventListener('click', hideContextMenu)
  })
}

const hideContextMenu = () => {
  showContextMenu.value = false
  document.removeEventListener('click', hideContextMenu)
}

const startEditCollection = (collection) => {
  editingNodeId.value = collection.id
  editingNodeName.value = collection.name
  nextTick(() => {
    if (editInputRef.value) {
      editInputRef.value.focus()
    }
  })
}

const saveCollectionName = async () => {
  if (!editingNodeId.value || !editingNodeName.value.trim()) {
    cancelEdit()
    return
  }

  try {
    const collection = flatCollections.value.find(c => c.id === editingNodeId.value)
    if (!collection) {
      ElMessage.error('集合不存在')
      cancelEdit()
      return
    }

    const data = {
      name: editingNodeName.value.trim(),
      description: collection.description,
      parent: collection.parent,
      project: selectedProject.value
    }

    await api.put(`/api-testing/collections/${editingNodeId.value}/`, data)
    
    // 直接更新本地数据，避免重新加载
    const updateCollectionName = (collections, id, newName) => {
      for (const collection of collections) {
        // 只更新集合类型的节点，跳过接口类型的节点
        if (collection.type === 'collection' && collection.id === id) {
          collection.name = newName
          return true
        }
        if (collection.children && updateCollectionName(collection.children, id, newName)) {
          return true
        }
      }
      return false
    }
    
    // 更新树中的集合名称
    updateCollectionName(collections.value, editingNodeId.value, editingNodeName.value.trim())
    
    // 更新平均集合列表
    const flatCollection = flatCollections.value.find(c => c.id === editingNodeId.value)
    if (flatCollection) {
      flatCollection.name = editingNodeName.value.trim()
    }
    
    ElMessage.success('集合名称更新成功')
    cancelEdit()
  } catch (error) {
    ElMessage.error('更新失败')
    cancelEdit()
  }
}

const cancelEdit = () => {
  editingNodeId.value = null
  editingNodeName.value = ''
}

const onNodeExpand = (data) => {
  if (!expandedKeys.value.includes(data.id)) {
    expandedKeys.value.push(data.id)
  }
}

const onNodeCollapse = (data) => {
  const index = expandedKeys.value.indexOf(data.id)
  if (index > -1) {
    expandedKeys.value.splice(index, 1)
  }
}

const addRequest = () => {
  // 创建新请求
  const newRequest = {
    name: '新建请求',
    method: 'GET',
    url: '',
    headers: {},
    params: {},
    body: {},
    collection: rightClickedNode.value.type === 'collection' ? rightClickedNode.value.id : rightClickedNode.value.collection,
    type: 'request'
  }
  selectedRequest.value = newRequest
  hideContextMenu()
}

const addCollection = () => {
  collectionForm.parent = rightClickedNode.value.type === 'collection' ? rightClickedNode.value.id : null
  showCreateCollectionDialog.value = true
  hideContextMenu()
}

const editNode = () => {
  if (rightClickedNode.value.type === 'request') {
    // 使用与onNodeClick相同的逻辑来正确设置selectedRequest
    const data = rightClickedNode.value
    console.log('editNode - original data.headers:', data.headers)
    const convertedHeaders = convertObjectToKeyValueArray(data.headers || {})
    console.log('editNode - converted headers:', convertedHeaders)
    
    // 初始化currentHeaders
    currentHeaders.value = data.headers || {}
    console.log('editNode - initialized currentHeaders:', currentHeaders.value)
    
    selectedRequest.value = {
      ...data,
      params: convertObjectToKeyValueArray(data.params || {}),
      headers: convertedHeaders,
      body: data.body || {},
      auth: data.auth || {}
    }
    
    console.log('editNode - selectedRequest.value.headers:', selectedRequest.value.headers)

    // 解析body数据
    if (data.body && data.body.type) {
      if (data.body.type === 'json' && data.body.data) {
        bodyType.value = 'raw'
        rawType.value = 'json'
        rawBody.value = JSON.stringify(data.body.data, null, 2)
      } else if (data.body.type === 'raw' && data.body.data) {
        bodyType.value = 'raw'
        rawType.value = 'text'
        rawBody.value = data.body.data
      } else if (data.body.type === 'form-data') {
        bodyType.value = 'form-data'
        formData.value = data.body.data || {}
      } else if (data.body.type === 'x-www-form-urlencoded') {
        bodyType.value = 'x-www-form-urlencoded'
        formUrlEncoded.value = data.body.data || {}
      } else if (data.body.type === 'binary') {
        bodyType.value = 'binary'
      } else {
        bodyType.value = 'none'
        rawBody.value = ''
      }
    } else {
      bodyType.value = 'none'
      rawBody.value = ''
    }
    
    response.value = null
  } else if (rightClickedNode.value.type === 'collection') {
    // 启动集合内联编辑
    startEditCollection(rightClickedNode.value)
  }
  hideContextMenu()
}

const deleteNode = async () => {
  if (!rightClickedNode.value) {
    hideContextMenu()
    return
  }

  const nodeType = rightClickedNode.value.type
  const nodeName = rightClickedNode.value.name
  
  // 显示确认对话框
  try {
    await ElMessageBox.confirm(
      `确定要删除${nodeType === 'collection' ? '集合' : '接口'} "${nodeName}" 吗？${nodeType === 'collection' ? '删除集合会同时删除其中的所有接口。' : ''}`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    // 用户确认删除，执行删除操作
    if (nodeType === 'collection') {
      await deleteCollection(rightClickedNode.value.id)
    } else if (nodeType === 'request') {
      await deleteRequest(rightClickedNode.value.id)
    }
  } catch (error) {
    // 用户取消删除或删除失败，不做任何处理
    console.log('删除操作被取消或失败:', error)
  }
  
  hideContextMenu()
}

const deleteCollection = async (collectionId) => {
  try {
    await api.delete(`/api-testing/collections/${collectionId}/`)
    ElMessage.success('集合删除成功')
    
    // 如果当前选中的请求属于被删除的集合，清空选中状态
    if (selectedRequest.value && selectedRequest.value.collection === collectionId) {
      selectedRequest.value = null
      response.value = null
    }
    
    // 直接从树中移除集合，而不是重新加载
    const removeCollectionFromTree = (collections, id) => {
      for (let i = 0; i < collections.length; i++) {
        if (collections[i].id === id) {
          collections.splice(i, 1)
          return true
        }
        if (collections[i].children && removeCollectionFromTree(collections[i].children, id)) {
          return true
        }
      }
      return false
    }
    
    removeCollectionFromTree(collections.value, collectionId)
    
    // 从平集合列表中移除
    const index = flatCollections.value.findIndex(c => c.id === collectionId)
    if (index > -1) {
      flatCollections.value.splice(index, 1)
    }
    
    // 从展开键中移除
    const expandedIndex = expandedKeys.value.indexOf(collectionId)
    if (expandedIndex > -1) {
      expandedKeys.value.splice(expandedIndex, 1)
    }
    
  } catch (error) {
    ElMessage.error('删除集合失败')
    console.error('Delete collection error:', error)
  }
}

const deleteRequest = async (requestId) => {
  try {
    await api.delete(`/api-testing/requests/${requestId}/`)
    ElMessage.success('接口删除成功')
    
    // 如果当前选中的是被删除的请求，清空选中状态
    if (selectedRequest.value && selectedRequest.value.id === requestId) {
      selectedRequest.value = null
      response.value = null
    }
    
    // 直接从树中移除请求，而不是重新加载
    const removeRequestFromTree = (collections, requestId) => {
      for (const collection of collections) {
        if (collection.children) {
          const requestIndex = collection.children.findIndex(child => child.type === 'request' && child.id === requestId)
          if (requestIndex > -1) {
            collection.children.splice(requestIndex, 1)
            return true
          }
        }
        if (collection.children && removeRequestFromTree(collection.children, requestId)) {
          return true
        }
      }
      return false
    }
    
    removeRequestFromTree(collections.value, requestId)
    
  } catch (error) {
    ElMessage.error('删除接口失败')
    console.error('Delete request error:', error)
  }
}

const createCollection = async () => {
  try {
    const data = {
      ...collectionForm,
      project: selectedProject.value
    }
    const res = await api.post('/api-testing/collections/', data)
    const newCollection = res.data
    
    ElMessage.success('创建成功')
    showCreateCollectionDialog.value = false
    Object.assign(collectionForm, { name: '', description: '', parent: null })
    
    // 直接添加到本地数据，避免重新加载
    const newTreeNode = {
      ...newCollection,
      type: 'collection',
      children: []
    }
    
    // 添加到平集合列表
    flatCollections.value.push(newCollection)
    
    // 添加到树结构
    if (newCollection.parent) {
      // 找到父节点并添加
      const findAndAddToParent = (collections, parentId, newNode) => {
        for (const collection of collections) {
          if (collection.id === parentId) {
            if (!collection.children) collection.children = []
            collection.children.push(newNode)
            return true
          }
          if (collection.children && findAndAddToParent(collection.children, parentId, newNode)) {
            return true
          }
        }
        return false
      }
      
      findAndAddToParent(collections.value, newCollection.parent, newTreeNode)
      
      // 自动展开父节点
      if (!expandedKeys.value.includes(newCollection.parent)) {
        expandedKeys.value.push(newCollection.parent)
      }
    } else {
      // 添加到根级
      collections.value.push(newTreeNode)
    }
    
    // 自动展开新创建的集合
    if (!expandedKeys.value.includes(newCollection.id)) {
      expandedKeys.value.push(newCollection.id)
    }
    
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

// 断言相关方法
const addAssertion = () => {
  if (!selectedRequest.value.assertions) {
    selectedRequest.value.assertions = []
  }
  
  selectedRequest.value.assertions.push({
    name: `断言${selectedRequest.value.assertions.length + 1}`,
    type: '',
    expected: null,
    json_path: '',
    header_name: ''
  })
}

const removeAssertion = (index) => {
  if (selectedRequest.value.assertions) {
    selectedRequest.value.assertions.splice(index, 1)
  }
}

const onAssertionTypeChange = (assertion) => {
  // 重置断言参数
  assertion.expected = null
  assertion.json_path = ''
  assertion.header_name = ''
}

// WebSocket消息处理函数
const handleWebSocketFileUpload = (file) => {
  websocketBinaryFile.value = file.raw
  return false
}

const clearWebSocketBinaryFile = () => {
  websocketBinaryFile.value = null
}

const sendWebSocketMessage = () => {
  if (websocketConnectionStatus.value !== 'connected') {
    ElMessage.warning('请先建立WebSocket连接')
    return
  }
  
  if (!websocketConnection.value) {
    ElMessage.error('WebSocket连接不存在')
    return
  }
  
  try {
    let messageToSend = ''
    
    if (websocketMessageType.value === 'text' || websocketMessageType.value === 'json') {
      messageToSend = websocketMessageContent.value
    } else if (websocketMessageType.value === 'binary' && websocketBinaryFile.value) {
      // 对于二进制文件，需要读取文件内容
      const reader = new FileReader()
      reader.onload = (e) => {
        websocketConnection.value.send(e.target.result)
        addWebSocketMessage('sent', '[二进制数据]')
        ElMessage.success('二进制消息已发送')
      }
      reader.onerror = () => {
        ElMessage.error('读取文件失败')
      }
      reader.readAsArrayBuffer(websocketBinaryFile.value)
      return
    } else {
      ElMessage.warning('请输入消息内容或选择文件')
      return
    }
    
    websocketConnection.value.send(messageToSend)
    addWebSocketMessage('sent', messageToSend)
    ElMessage.success('消息已发送')
    
  } catch (error) {
    const errorMsg = '发送消息失败: ' + error.message
    addWebSocketMessage('error', errorMsg)
    ElMessage.error(errorMsg)
  }
}

const clearWebSocketMessage = () => {
  websocketMessageContent.value = ''
  websocketBinaryFile.value = null
  websocketMessageType.value = 'text'
}

// WebSocket消息历史记录相关方法
const addWebSocketMessage = (type, content) => {
  const timestamp = new Date().toLocaleTimeString()
  websocketMessages.value.push({
    type,
    content,
    timestamp
  })
}

const clearWebSocketMessages = () => {
  websocketMessages.value = []
}

const isJsonString = (str) => {
  try {
    JSON.parse(str)
    return true
  } catch (e) {
    return false
  }
}

const formatJson = (str) => {
  try {
    return JSON.stringify(JSON.parse(str), null, 2)
  } catch (e) {
    return str
  }
}

// WebSocket连接管理函数
const toggleWebSocketConnection = () => {
  if (websocketConnectionStatus.value === 'disconnected') {
    connectWebSocket()
  } else {
    disconnectWebSocket()
  }
}

const connectWebSocket = () => {
  if (!selectedRequest.value || !selectedRequest.value.url) {
    ElMessage.warning('请输入WebSocket连接地址')
    return
  }
  
  websocketConnectionStatus.value = 'connecting'
  
  try {
    // 替换环境变量
    let url = selectedRequest.value.url
    if (selectedEnvironment.value) {
      const env = environments.value.find(e => e.id === selectedEnvironment.value)
      if (env && env.variables) {
        Object.entries(env.variables).forEach(([key, value]) => {
          url = url.replace(`{{${key}}}`, value.currentValue || value.initialValue || '')
        })
      }
    }
    
    // 创建WebSocket连接
    websocketConnection.value = new WebSocket(url)
    
    websocketConnection.value.onopen = () => {
      websocketConnectionStatus.value = 'connected'
      // 添加连接成功的特殊消息
      addWebSocketMessage('connected', `Websocket已连接至${url}`)
      ElMessage.success('WebSocket连接成功')
    }
    
    websocketConnection.value.onmessage = (event) => {
      // 处理接收到的消息
      console.log('WebSocket message received:', event.data)
      addWebSocketMessage('received', event.data)
      ElMessage.info('收到WebSocket消息')
    }
    
    websocketConnection.value.onclose = () => {
      websocketConnectionStatus.value = 'disconnected'
      addWebSocketMessage('info', 'WebSocket连接已关闭')
      ElMessage.info('WebSocket连接已关闭')
    }
    
    websocketConnection.value.onerror = (error) => {
      websocketConnectionStatus.value = 'disconnected'
      const errorMsg = 'WebSocket连接错误: ' + (error.message || '连接失败')
      addWebSocketMessage('error', errorMsg)
      ElMessage.error(errorMsg)
    }
    
  } catch (error) {
    websocketConnectionStatus.value = 'disconnected'
    const errorMsg = 'WebSocket连接失败: ' + error.message
    addWebSocketMessage('error', errorMsg)
    ElMessage.error(errorMsg)
  }
}

const disconnectWebSocket = () => {
  if (websocketConnection.value) {
    websocketConnection.value.close()
    websocketConnection.value = null
  }
  websocketConnectionStatus.value = 'disconnected'
  // 清空消息历史
  clearWebSocketMessages()
}

const createEmptyRequest = async () => {
  // 检查是否有选中的项目
  if (!selectedProject.value) {
    ElMessage.warning('请先选择一个项目')
    return
  }
  
  // 检查是否有可用的集合
  if (!flatCollections.value || flatCollections.value.length === 0) {
    ElMessage.warning('请先创建一个集合')
    return
  }
  
  // 使用第一个集合作为默认集合
  const defaultCollection = flatCollections.value[0]
  
  // 获取当前项目信息
  const currentProject = projects.value.find(p => p.id === selectedProject.value)
  const isWebSocketProject = currentProject && currentProject.project_type === 'WEBSOCKET'
  
  saving.value = true
  try {
    // 创建一个空的接口，参照"获取宠物列表"的样式
    const data = {
      name: '新建接口',
      method: isWebSocketProject ? 'CONNECT' : 'GET',
      url: isWebSocketProject ? 'ws://{{host}}/websocket' : '{{base_url}}/api/new-endpoint',
      description: '',
      collection: defaultCollection.id,
      project: selectedProject.value,
      request_type: isWebSocketProject ? 'WEBSOCKET' : 'HTTP',
      params: {},
      headers: isWebSocketProject ? {} : {
        'Content-Type': 'application/json'
      },
      body: {},
      auth: {},
      pre_request_script: '',
      post_request_script: ''
    }
    
    const res = await api.post('/api-testing/requests/', data)
    ElMessage.success('创建成功')
    
    // 重新加载集合和请求
    await Promise.all([loadCollections(), loadRequests()])
    
    // 自动选中新创建的请求并进入编辑状态
    selectedRequest.value = {
      id: res.data.id,
      name: res.data.name,
      method: res.data.method,
      url: res.data.url,
      description: res.data.description || '',
      collection: res.data.collection,
      project: res.data.project,
      request_type: res.data.request_type,
      params: convertObjectToKeyValueArray(res.data.params || {}),
      headers: convertObjectToKeyValueArray(res.data.headers || {}),
      body: res.data.body || {},
      auth: res.data.auth || {},
      pre_request_script: res.data.pre_request_script || '',
      post_request_script: res.data.post_request_script || ''
    }
    
    // 默认进入params标签页
    activeTab.value = 'params'
    
    // 初始化body相关变量
    bodyType.value = 'none'
    rawType.value = 'json'
    formData.value = {}
    formUrlEncoded.value = {}
    rawBody.value = ''
    
  } catch (error) {
    ElMessage.error('创建失败')
    console.error('Create request error:', error)
  } finally {
    saving.value = false
  }
}

const sendRequest = async () => {
  if (!selectedRequest.value) return
  
  // 检查是否为WebSocket接口
  if (selectedRequest.value.request_type === 'WEBSOCKET') {
    ElMessage.warning('WebSocket接口暂不支持在此界面直接执行，请使用专门的WebSocket测试工具')
    return
  }
  
  // 检查是否选择了环境
  if (!selectedEnvironment.value) {
    ElMessage.warning('请选择环境')
    return
  }
  
  sending.value = true
  try {
    // 发送请求前先自动保存当前的修改
    await saveRequest()

    // 准备请求体数据
    let bodyData = {}
    if (hasBody.value) {
      if (bodyType.value === 'none') {
        bodyData = {}
      } else if (bodyType.value === 'raw' && rawBody.value) {
        if (rawType.value === 'json') {
          try {
            bodyData = {
              type: 'json',
              data: JSON.parse(rawBody.value)
            }
          } catch (e) {
            bodyData = {
              type: 'raw',
              data: rawBody.value
            }
          }
        } else {
          bodyData = {
            type: 'raw',
            data: rawBody.value
          }
        }
      } else if (bodyType.value === 'form-data') {
        bodyData = {
          type: 'form-data',
          data: formData.value || {}
        }
      } else if (bodyType.value === 'x-www-form-urlencoded') {
        bodyData = {
          type: 'x-www-form-urlencoded',
          data: formUrlEncoded.value || {}
        }
      } else if (bodyType.value === 'binary') {
        bodyData = {
          type: 'binary',
          data: null
        }
      }
    }
    
    const requestData = {
      ...selectedRequest.value,
      params: convertKeyValueArrayToObject(selectedRequest.value.params || []),
      headers: selectedRequest.value.headers,  // 现在直接使用数组格式
      body: bodyData,
      environment_id: selectedEnvironment.value
    }
    
    const res = await api.post(`/api-testing/requests/${selectedRequest.value.id}/execute/`, requestData)
    response.value = res.data
    ElMessage.success('请求发送成功')
  } catch (error) {
    ElMessage.error('请求发送失败')
    if (error.response?.data) {
      response.value = error.response.data
    }
  } finally {
    sending.value = false
  }
}

// 存储最新的headers数据
const currentHeaders = ref({})

const onHeadersUpdate = (newHeaders) => {
  console.log('Headers updated:', newHeaders)
  currentHeaders.value = newHeaders
  if (selectedRequest.value) {
    // 强制更新整个selectedRequest对象以触发响应式更新
    selectedRequest.value = {
      ...selectedRequest.value,
      headers: newHeaders
    }
    console.log('Updated selectedRequest.headers:', selectedRequest.value.headers)
  }
}

const saveRequest = async () => {
  if (!selectedRequest.value) return

  saving.value = true
  try {
    // 准备保存的数据
    let bodyData = {}

    if (hasBody.value) {
      if (bodyType.value === 'none') {
        bodyData = {}
      } else if (bodyType.value === 'raw' && rawBody.value) {
        if (rawType.value === 'json') {
          try {
            bodyData = {
              type: 'json',
              data: JSON.parse(rawBody.value)
            }
          } catch (e) {
            bodyData = {
              type: 'raw',
              data: rawBody.value
            }
          }
        } else {
          bodyData = {
            type: 'raw',
            data: rawBody.value
          }
        }
      } else if (bodyType.value === 'form-data') {
        // 处理 form-data 类型
        bodyData = {
          type: 'form-data',
          data: formData.value || {}
        }
      } else if (bodyType.value === 'x-www-form-urlencoded') {
        // 处理 x-www-form-urlencoded 类型
        bodyData = {
          type: 'x-www-form-urlencoded',
          data: formUrlEncoded.value || {}
        }
      } else if (bodyType.value === 'binary') {
        // 处理 binary 类型
        bodyData = {
          type: 'binary',
          data: null
        }
      }
    }
    
    // 直接从KeyValueEditor组件获取当前headers（完整数组格式）
    let finalHeaders = []
    console.log('headersEditorRef.value:', headersEditorRef.value)
    if (headersEditorRef.value) {
      // 直接访问KeyValueEditor的rows数据，保持完整的数组格式
      const rows = headersEditorRef.value.rows || []
      console.log('Direct access to headers rows:', rows)
      finalHeaders = rows
        .filter(row => row.enabled && row.key && row.key.trim())
        .map(row => ({
          key: row.key.trim(),
          value: row.value || '',
          description: row.description || '',
          enabled: row.enabled !== false
        }))
      console.log('Final headers array format:', finalHeaders)
    } else {
      console.log('headersEditorRef.value is null or undefined')
      // 如果无法获取，使用selectedRequest中的headers
      if (selectedRequest.value.headers && Array.isArray(selectedRequest.value.headers)) {
        finalHeaders = selectedRequest.value.headers.filter(item => item.enabled && item.key)
      }
    }
    
    console.log('Final headers to save:', finalHeaders)
    console.log('selectedRequest.value.params:', selectedRequest.value.params)
    
    const data = {
      ...selectedRequest.value,
      params: convertKeyValueArrayToObject(selectedRequest.value.params || []),
      headers: finalHeaders,  // 保存完整的数组格式，包含description
      body: bodyData
    }
    
    console.log('Data being sent to backend:', data)
    
    console.log('Final save data:', data)
    console.log('Headers being saved:', data.headers)
    
    if (selectedRequest.value.id) {
      await api.put(`/api-testing/requests/${selectedRequest.value.id}/`, data)
      
      // 更新树中的请求名称，避免重新加载
      const updateRequestName = (collections, requestId, newName) => {
        for (const collection of collections) {
          if (collection.children) {
            const request = collection.children.find(child => child.type === 'request' && child.id === requestId)
            if (request) {
              request.name = newName
              return true
            }
          }
          if (collection.children && updateRequestName(collection.children, requestId, newName)) {
            return true
          }
        }
        return false
      }
      
      updateRequestName(collections.value, selectedRequest.value.id, selectedRequest.value.name)
    } else {
      const res = await api.post('/api-testing/requests/', data)
      selectedRequest.value.id = res.data.id
      // 新建的请求需要重新加载树以显示新请求
      await loadCollections()
    }
    
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const onBodyTypeChange = () => {
  if (bodyType.value === 'raw') {
    rawType.value = 'json'
    rawBody.value = ''
  }
}

const formatResponse = () => {
  // 格式化响应内容
  try {
    if (response.value?.response_data?.json) {
      response.value.response_data.body = JSON.stringify(response.value.response_data.json, null, 2)
    }
  } catch (e) {
    ElMessage.error('格式化失败')
  }
}

const copyResponse = () => {
  if (responseBody.value) {
    navigator.clipboard.writeText(responseBody.value)
    ElMessage.success('已复制到剪贴板')
  }
}

onMounted(() => {
  loadProjects()
})

onBeforeUnmount(() => {
  // 清理WebSocket连接
  if (websocketConnection.value) {
    websocketConnection.value.close()
    websocketConnection.value = null
  }
})
</script>

<style scoped>
.interface-management {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.interface-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 300px;
  border-right: 1px solid #e4e7ed;
  background: #f8f9fa;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 10px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  gap: 10px;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.collection-tree {
  flex: 1;
  overflow: auto;
  padding: 10px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 5px;
  flex: 1;
}

.node-label {
  flex: 1;
}

.node-edit {
  flex: 1;
}

.node-edit .el-input {
  font-size: 14px;
}

.method-tag {
  font-size: 10px;
  padding: 1px 4px;
  border-radius: 2px;
  color: white;
  font-weight: bold;
}

.method-tag.get { background: #67c23a; }
.method-tag.post { background: #409eff; }
.method-tag.put { background: #e6a23c; }
.method-tag.delete { background: #f56c6c; }
.method-tag.patch { background: #909399; }

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.request-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: auto;
}

.request-header {
  margin-bottom: 20px;
}

.request-line {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.url-input {
  flex: 1;
}

.request-name {
  display: flex;
  gap: 10px;
  align-items: center;
}

.request-tabs {
  margin-bottom: 20px;
}

.body-container {
  padding: 10px 0;
}

.body-content {
  margin-top: 15px;
}

.raw-options {
  margin-bottom: 10px;
}

.raw-body {
  font-family: 'Courier New', monospace;
}

.response-section {
  border-top: 1px solid #e4e7ed;
  padding-top: 20px;
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.response-info {
  display: flex;
  gap: 10px;
  align-items: center;
}

.response-time {
  color: #909399;
  font-size: 12px;
}

.response-body {
  position: relative;
}

.response-actions {
  margin-bottom: 10px;
}

.response-content {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  max-height: 400px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.response-headers {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
}

.header-row {
  margin-bottom: 5px;
  font-size: 12px;
}

/* 断言样式 */
.assertions-editor {
  padding: 10px;
}

.assertions-header {
  margin-bottom: 15px;
}

.assertion-item {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 15px;
  background: #fafafa;
}

.assertion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #e4e7ed;
  background: white;
}

.assertion-name {
  flex: 1;
  margin-right: 10px;
}

.assertion-config {
  padding: 10px;
}

.assertion-config .el-select {
  width: 100%;
  margin-bottom: 10px;
}

.assertion-params {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.assertion-input {
  margin-bottom: 5px;
}

.no-assertions {
  text-align: center;
  padding: 30px;
  color: #909399;
}

/* WebSocket信息样式 */
.websocket-info-section {
  padding: 20px;
}

.websocket-tips {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.websocket-tips h4 {
  margin-top: 0;
  margin-bottom: 10px;
}

.websocket-tips ul {
  margin: 0;
  padding-left: 20px;
}

.websocket-tips li {
  margin-bottom: 5px;
}

/* WebSocket消息样式 */
.message-container {
  padding: 15px;
}

.message-input-section {
  margin-bottom: 20px;
}

.uploaded-file {
  margin-top: 10px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* WebSocket响应区域样式 */
.websocket-response-section {
  border-top: 1px solid #e4e7ed;
  padding-top: 20px;
}

.websocket-response-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
}

.websocket-messages {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 15px;
}

.websocket-message-item {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 10px;
  background-color: #fafafa;
}

.websocket-message-item.sent {
  border-left: 3px solid #409eff;
}

.websocket-message-item.received {
  border-left: 3px solid #67c23a;
}

.websocket-message-item.info {
  border-left: 3px solid #909399;
}

.websocket-message-item.error {
  border-left: 3px solid #f56c6c;
}

.websocket-message-item.connected {
  border-left: 3px solid #67c23a;
}

.message-header {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  font-size: 12px;
}

.message-type.sent {
  color: #409eff;
  font-weight: bold;
}

.message-type.received {
  color: #67c23a;
  font-weight: bold;
}

.message-type.info {
  color: #909399;
  font-weight: bold;
}

.message-type.error {
  color: #f56c6c;
  font-weight: bold;
}

.message-type.connected {
  color: #67c23a;
  font-weight: bold;
}

.message-time {
  color: #909399;
}

.message-content {
  padding: 10px 12px;
}

.message-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
}

/* WebSocket URL样式 */
.websocket-url {
  flex: 1;
}

/* 断言结果样式 */
.assertions-results {
  padding: 15px;
}

.assertion-result-item {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 10px;
  padding: 10px;
}

.assertion-result-item.passed {
  border-color: #67c23a;
  background-color: #f0f9ff;
}

.assertion-result-item.failed {
  border-color: #f56c6c;
  background-color: #fef0f0;
}

.assertion-result-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.assertion-name {
  margin-left: 8px;
  font-weight: 500;
}

.assertion-result-details {
  padding-left: 24px;
  font-size: 12px;
}

.result-row {
  display: flex;
  margin-bottom: 4px;
}

.label {
  width: 50px;
  font-weight: 500;
}

.value {
  flex: 1;
  word-break: break-all;
}

.value.error {
  color: #f56c6c;
}

.context-menu {
  position: fixed;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 5px 0;
  margin: 0;
  list-style: none;
  z-index: 9999;
}

.context-menu li {
  padding: 8px 15px;
  cursor: pointer;
  font-size: 14px;
}

.context-menu li:hover {
  background: #f5f7fa;
}
</style>