<template>
  <div class="layout">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="240px">
        <div class="logo" @click="router.push('/home')" style="cursor: pointer;">
          <h2>TestHub</h2>
        </div>
        <el-menu
          :default-active="$route.path"
          router
          background-color="#001529"
          text-color="#fff"
          active-text-color="#1890ff"
        >
          <!-- AI用例生成模块菜单 -->
          <template v-if="currentModule === 'ai-generation'">
            <el-sub-menu index="requirement">
              <template #title>
                <el-icon><MagicStick /></el-icon>
                <span>智能用例生成</span>
              </template>
              <el-menu-item index="/ai-generation/requirement-analysis">AI用例生成</el-menu-item>
              <el-menu-item index="/ai-generation/generated-testcases">AI生成用例记录</el-menu-item>
              <el-menu-item index="/ai-generation/prompt-config">提示词配置</el-menu-item>
            </el-sub-menu>
            <el-menu-item index="/ai-generation/projects">
              <el-icon><Folder /></el-icon>
              <span>项目管理</span>
            </el-menu-item>
            <el-menu-item index="/ai-generation/testcases">
              <el-icon><Document /></el-icon>
              <span>测试用例</span>
            </el-menu-item>
            <el-menu-item index="/ai-generation/versions">
              <el-icon><Flag /></el-icon>
              <span>版本管理</span>
            </el-menu-item>
            <el-sub-menu index="reviews">
              <template #title>
                <el-icon><Check /></el-icon>
                <span>评审管理</span>
              </template>
              <el-menu-item index="/ai-generation/reviews">评审列表</el-menu-item>
              <el-menu-item index="/ai-generation/review-templates">评审模板</el-menu-item>
            </el-sub-menu>

            <el-menu-item index="/ai-generation/executions">
              <el-icon><VideoPlay /></el-icon>
              <span>测试计划</span>
            </el-menu-item>
            <el-menu-item index="/ai-generation/reports">
              <el-icon><DataAnalysis /></el-icon>
              <span>测试报告</span>
            </el-menu-item>
          </template>

          <!-- 接口测试模块菜单 -->
          <template v-else-if="currentModule === 'api-testing'">
            <el-menu-item index="/api-testing/dashboard">
              <el-icon><Odometer /></el-icon>
              <span>数据看板</span>
            </el-menu-item>
            <el-menu-item index="/api-testing/projects">
              <el-icon><Folder /></el-icon>
              <span>项目管理</span>
            </el-menu-item>
            <el-menu-item index="/api-testing/interfaces">
              <el-icon><Link /></el-icon>
              <span>接口管理</span>
            </el-menu-item>
            <el-menu-item index="/api-testing/automation">
              <el-icon><VideoPlay /></el-icon>
              <span>自动化测试</span>
            </el-menu-item>
            <el-menu-item index="/api-testing/history">
              <el-icon><Timer /></el-icon>
              <span>请求历史</span>
            </el-menu-item>
            <el-menu-item index="/api-testing/environments">
              <el-icon><Setting /></el-icon>
              <span>环境管理</span>
            </el-menu-item>
            <el-menu-item index="/api-testing/reports">
              <el-icon><DataAnalysis /></el-icon>
              <span>测试报告</span>
            </el-menu-item>
            <el-menu-item index="/api-testing/scheduled-tasks">
              <el-icon><AlarmClock /></el-icon>
              <span>定时任务</span>
            </el-menu-item>
            <el-menu-item index="/api-testing/notification-logs">
              <el-icon><Bell /></el-icon>
              <span>通知列表</span>
            </el-menu-item>
          </template>

          <!-- UI自动化测试模块菜单 -->
          <template v-else-if="currentModule === 'ui-automation'">
            <el-menu-item index="/ui-automation/dashboard">
              <el-icon><Odometer /></el-icon>
              <span>数据看板</span>
            </el-menu-item>
            <el-menu-item index="/ui-automation/projects">
              <el-icon><Folder /></el-icon>
              <span>项目管理</span>
            </el-menu-item>
            <el-menu-item index="/ui-automation/elements-enhanced">
              <el-icon><Aim /></el-icon>
              <span>元素管理</span>
            </el-menu-item>
            <el-menu-item index="/ui-automation/test-cases">
              <el-icon><Document /></el-icon>
              <span>用例管理</span>
            </el-menu-item>
            <el-menu-item index="/ui-automation/scripts-enhanced">
              <el-icon><Edit /></el-icon>
              <span>脚本生成</span>
            </el-menu-item>
            <el-menu-item index="/ui-automation/scripts">
              <el-icon><DocumentCopy /></el-icon>
              <span>脚本列表</span>
            </el-menu-item>
            <el-menu-item index="/ui-automation/suites">
              <el-icon><Collection /></el-icon>
              <span>套件管理</span>
            </el-menu-item>
            <el-menu-item index="/ui-automation/executions">
              <el-icon><VideoPlay /></el-icon>
              <span>执行记录</span>
            </el-menu-item>
            <el-menu-item index="/ui-automation/reports">
              <el-icon><DataAnalysis /></el-icon>
              <span>测试报告</span>
            </el-menu-item>
            <el-menu-item index="/ui-automation/scheduled-tasks">
              <el-icon><AlarmClock /></el-icon>
              <span>定时任务</span>
            </el-menu-item>
            <el-menu-item index="/ui-automation/notification-logs">
              <el-icon><Bell /></el-icon>
              <span>通知列表</span>
            </el-menu-item>
          </template>

          <!-- AI 智能模式模块菜单 -->
          <template v-else-if="currentModule === 'ai-intelligent-mode'">
            <el-menu-item index="/ai-intelligent-mode/testing">
              <el-icon><VideoPlay /></el-icon>
              <span>AI 智能测试</span>
            </el-menu-item>
            <el-menu-item index="/ai-intelligent-mode/cases">
              <el-icon><Document /></el-icon>
              <span>AI 用例管理</span>
            </el-menu-item>
            <el-menu-item index="/ai-intelligent-mode/execution-records">
              <el-icon><Timer /></el-icon>
              <span>AI 测试报告</span>
            </el-menu-item>

          </template>

          <!-- 配置中心模块菜单 -->
          <template v-else-if="currentModule === 'configuration'">
            <el-menu-item index="/configuration/ai-model">
              <el-icon><Cpu /></el-icon>
              <span>AI用例生成模型配置</span>
            </el-menu-item>
            <el-menu-item index="/configuration/ui-env">
              <el-icon><Monitor /></el-icon>
              <span>UI环境配置</span>
            </el-menu-item>
            <el-menu-item index="/configuration/ai-mode">
              <el-icon><MagicStick /></el-icon>
              <span>AI智能模式配置</span>
            </el-menu-item>
            <el-menu-item index="/configuration/scheduled-task">
              <el-icon><Timer /></el-icon>
              <span>定时任务配置</span>
            </el-menu-item>
            <el-menu-item index="/configuration/dify">
              <el-icon><ChatDotRound /></el-icon>
              <span>AI评测师配置</span>
            </el-menu-item>
          </template>
        </el-menu>
      </el-aside>

      <!-- 主体内容 -->
      <el-container>
        <!-- 顶部导航 -->
        <el-header height="60px">
          <div class="header-content">
            <div class="header-left">
              <el-breadcrumb separator="/">
                <el-breadcrumb-item :to="{ path: '/home' }">首页</el-breadcrumb-item>
                <el-breadcrumb-item v-if="moduleName">{{ moduleName }}</el-breadcrumb-item>
                <el-breadcrumb-item>{{ breadcrumbTitle }}</el-breadcrumb-item>
              </el-breadcrumb>
            </div>
            <div class="header-right">
              <el-dropdown @command="handleCommand">
                <span class="user-info">
                  <el-avatar :size="32" :src="userStore.user?.avatar" />
                  <span class="username">{{ userStore.user?.username }}</span>
                  <el-icon><ArrowDown /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">个人设置</el-dropdown-item>
                    <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-header>

        <!-- 页面内容 -->
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { 
  Monitor, Folder, Document, Flag, Check, Collection, VideoPlay, 
  DataAnalysis, ChatDotRound, DocumentCopy, Link, MagicStick,
  Odometer, Timer, Setting, AlarmClock, Bell, Aim, Edit, Cpu
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const currentModule = computed(() => {
  if (route.path.startsWith('/ai-generation')) return 'ai-generation'
  if (route.path.startsWith('/api-testing')) return 'api-testing'
  if (route.path.startsWith('/ui-automation')) return 'ui-automation'
  if (route.path.startsWith('/ai-intelligent-mode')) return 'ai-intelligent-mode'
  if (route.path.startsWith('/configuration')) return 'configuration'
  return ''
})

const moduleName = computed(() => {
  const map = {
    'ai-generation': 'AI用例生成',
    'api-testing': '接口测试',
    'ui-automation': 'UI自动化测试',
    'ai-intelligent-mode': 'AI 智能模式',
    'configuration': '配置中心'
  }
  return map[currentModule.value] || ''
})

const breadcrumbTitle = computed(() => {
  const routeMap = {
    // AI用例生成
    '/ai-generation/requirement-analysis': 'AI用例生成',
    '/ai-generation/generated-testcases': 'AI生成用例记录',
    '/ai-generation/prompt-config': '提示词配置',
    '/ai-generation/projects': '项目管理',
    '/ai-generation/testcases': '测试用例',
    '/ai-generation/versions': '版本管理',
    '/ai-generation/reviews': '评审列表',
    '/ai-generation/review-templates': '评审模板',
    '/ai-generation/testsuites': '测试套件',
    '/ai-generation/executions': '执行记录',
    '/ai-generation/reports': '测试报告',
    
    // 接口测试
    '/api-testing/dashboard': '数据看板',
    '/api-testing/projects': '项目管理',
    '/api-testing/interfaces': '接口管理',
    '/api-testing/automation': '自动化测试',
    '/api-testing/history': '请求历史',
    '/api-testing/environments': '环境管理',
    '/api-testing/reports': '测试报告',
    '/api-testing/scheduled-tasks': '定时任务',
    '/api-testing/notification-logs': '通知列表',
    
    // UI自动化测试
    '/ui-automation/dashboard': '数据看板',
    '/ui-automation/projects': '项目管理',
    '/ui-automation/elements-enhanced': '元素管理',
    '/ui-automation/test-cases': '用例管理',
    '/ui-automation/scripts-enhanced': '脚本生成',
    '/ui-automation/scripts': '脚本列表',
    '/ui-automation/suites': '套件管理',
    '/ui-automation/executions': '执行记录',
    '/ui-automation/reports': '测试报告',
    '/ui-automation/scheduled-tasks': '定时任务',
    '/ui-automation/notification-logs': '通知列表',
    
    // AI 智能模式
    '/ai-intelligent-mode/testing': 'AI 智能测试',
    '/ai-intelligent-mode/cases': 'AI 用例管理',
    '/ai-intelligent-mode/execution-records': 'AI 测试报告',

    
    // 配置中心
    '/configuration/ai-model': 'AI用例生成模型配置',
    '/configuration/ui-env': 'UI环境配置',
    '/configuration/ai-mode': 'AI智能模式配置',
    '/configuration/scheduled-task': '定时任务配置',
    '/configuration/dify': 'AI评测师配置',
    
    '/profile': '个人设置'
  }
  return routeMap[route.path] || route.meta.title || ''
})

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    ElMessage.success('退出登录成功')
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/ai-generation/profile')
  }
}
</script>

<style lang="scss" scoped>
.layout {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.layout > .el-container {
  height: 100%;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #001529;
  color: white;
  border-bottom: 1px solid #1f1f1f;
  flex-shrink: 0;

  h2 {
    margin: 0;
    font-weight: 600;
    font-size: 20px;
  }
}

.el-aside {
  background-color: #001529;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: width 0.3s ease;
  width: 240px !important;

  .el-menu {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    border-right: none;
    
    &::-webkit-scrollbar {
      width: 0;
    }
  }
}

.el-menu {
  :deep(.el-sub-menu__title),
  :deep(.el-menu-item) {
    font-size: 14px;
  }
}

.el-menu--collapse {
  width: 64px !important;
  
  :deep(.el-sub-menu__title),
  :deep(.el-menu-item) {
    padding-left: 20px !important;
  }
  
  :deep(.el-sub-menu__title span),
  :deep(.el-menu-item span) {
    display: none;
  }
}

.el-container .el-container {
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.el-header {
  background-color: white;
  border-bottom: 1px solid #e8e8e8;
  padding: 0;
  flex-shrink: 0;
  height: 60px !important;

  .header-content {
    height: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
  }

  .header-left {
    flex: 1;
    overflow: hidden;
    
    :deep(.el-breadcrumb) {
      font-size: 14px;
    }
  }

  .user-info {
    display: flex;
    align-items: center;
    cursor: pointer;
    white-space: nowrap;

    .username {
      margin: 0 8px;
      color: #303133;
      font-size: 14px;
    }
  }
}

.el-main {
  background-color: #f5f5f5;
  padding: 20px;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

@media screen and (max-width: 1920px) {
  .el-aside {
    width: 220px !important;
  }
  
  .el-main {
    padding: 18px;
  }
  
  .logo h2 {
    font-size: 19px;
  }
}

@media screen and (max-width: 1600px) {
  .el-aside {
    width: 200px !important;
  }
  
  .el-main {
    padding: 16px;
  }
  
  .logo h2 {
    font-size: 18px;
  }
  
  .el-menu {
    :deep(.el-sub-menu__title),
    :deep(.el-menu-item) {
      font-size: 13px;
    }
  }
}

@media screen and (max-width: 1440px) {
  .el-aside {
    width: 180px !important;
  }
  
  .el-main {
    padding: 14px;
  }
  
  .logo h2 {
    font-size: 17px;
  }
  
  .el-menu {
    :deep(.el-sub-menu__title),
    :deep(.el-menu-item) {
      font-size: 13px;
    }
  }
}

@media screen and (max-width: 1366px) {
  .el-aside {
    width: 180px !important;
  }
  
  .el-main {
    padding: 12px;
  }
  
  .logo h2 {
    font-size: 16px;
  }
  
  .el-header {
    height: 56px !important;
  }
  
  .el-menu {
    :deep(.el-sub-menu__title),
    :deep(.el-menu-item) {
      font-size: 12px;
    }
  }
}

@media screen and (max-width: 1280px) {
  .el-aside {
    width: 160px !important;
  }
  
  .el-main {
    padding: 12px;
  }
  
  .logo h2 {
    font-size: 15px;
  }
  
  .el-header {
    height: 56px !important;
    
    .header-content {
      padding: 0 15px;
    }
  }
  
  .el-menu {
    :deep(.el-sub-menu__title),
    :deep(.el-menu-item) {
      font-size: 12px;
      padding-left: 15px !important;
    }
  }
}

@media screen and (max-width: 1024px) {
  .el-aside {
    width: 140px !important;
  }
  
  .el-main {
    padding: 10px;
  }
  
  .logo h2 {
    font-size: 14px;
  }
  
  .el-header {
    height: 52px !important;
    
    .header-content {
      padding: 0 12px;
    }
  }
  
  .el-menu {
    :deep(.el-sub-menu__title),
    :deep(.el-menu-item) {
      font-size: 12px;
      padding-left: 12px !important;
    }
  }
  
  .user-info .username {
    display: none;
  }
}

@media screen and (max-width: 768px) {
  .el-aside {
    position: fixed;
    left: 0;
    top: 0;
    z-index: 1000;
    width: 240px !important;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    
    &.mobile-open {
      transform: translateX(0);
    }
  }
  
  .el-main {
    padding: 8px;
  }
  
  .logo h2 {
    font-size: 16px;
  }
  
  .el-header {
    height: 50px !important;
    
    .header-content {
      padding: 0 10px;
    }
    
    .header-left {
      :deep(.el-breadcrumb__item) {
        &:not(:last-child) {
          display: none;
        }
      }
    }
  }
}

@media screen and (max-width: 480px) {
  .el-aside {
    width: 220px !important;
  }
  
  .el-main {
    padding: 6px;
  }
  
  .logo h2 {
    font-size: 15px;
  }
  
  .el-header {
    height: 48px !important;
    
    .header-content {
      padding: 0 8px;
    }
  }
  
  .user-info {
    .el-avatar {
      width: 28px !important;
      height: 28px !important;
    }
  }
}
</style>