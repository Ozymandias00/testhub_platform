<template>
  <div class="notification-configs-container">
    <!-- 页面说明 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon class="title-icon">
          <Setting/>
        </el-icon>
        通知配置
      </h1>
      <p class="page-description">
        配置飞书、企微、钉钉Webhook机器人地址
      </p>
    </div>

    <!-- Tab切换 -->
    <div class="content-wrapper">
      <el-tabs v-model="activeTab" class="notification-tabs">


        <!-- 飞书机器人Tab -->
        <el-tab-pane label="飞书机器人" name="feishu">
          <div class="tab-content">
            <div class="config-section">
              <el-form
                  ref="feishuFormRef"
                  :model="webhookBots.feishu"
                  label-position="top"
                  class="config-form"
              >
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="机器人名称">
                      <el-input
                          v-model="webhookBots.feishu.name"
                          placeholder="请输入飞书机器人名称"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="启用">
                      <el-switch v-model="webhookBots.feishu.enabled"/>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item label="Webhook URL">
                      <el-input
                          v-model="webhookBots.feishu.webhook_url"
                          placeholder="请输入飞书机器人Webhook URL"
                      />
                      <div class="form-item-hint">
                        飞书机器人Webhook URL格式：https://open.feishu.cn/open-apis/bot/v2/hook/...
                      </div>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item label="业务类型">
                      <el-checkbox v-model="webhookBots.feishu.enable_ui_automation">UI自动化测试</el-checkbox>
                      <el-checkbox v-model="webhookBots.feishu.enable_api_testing">接口测试</el-checkbox>
                    </el-form-item>
                  </el-col>
                </el-row>

                <div class="form-actions">
                  <el-button type="primary" @click="saveWebhookBot('feishu')">
                    保存飞书机器人配置
                  </el-button>
                </div>
              </el-form>
            </div>
          </div>
        </el-tab-pane>

        <!-- 企业微信机器人Tab -->
        <el-tab-pane label="企微机器人" name="wechat">
          <div class="tab-content">
            <div class="config-section">
              <el-form
                  ref="wechatFormRef"
                  :model="webhookBots.wechat"
                  label-position="top"
                  class="config-form"
              >
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="机器人名称">
                      <el-input
                          v-model="webhookBots.wechat.name"
                          placeholder="请输入企业微信机器人名称"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="启用">
                      <el-switch v-model="webhookBots.wechat.enabled"/>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item label="Webhook URL">
                      <el-input
                          v-model="webhookBots.wechat.webhook_url"
                          placeholder="请输入企业微信机器人Webhook URL"
                      />
                      <div class="form-item-hint">
                        企业微信机器人Webhook URL格式：https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=...
                      </div>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item label="业务类型">
                      <el-checkbox v-model="webhookBots.wechat.enable_ui_automation">UI自动化测试</el-checkbox>
                      <el-checkbox v-model="webhookBots.wechat.enable_api_testing">接口测试</el-checkbox>
                    </el-form-item>
                  </el-col>
                </el-row>

                <div class="form-actions">
                  <el-button type="primary" @click="saveWebhookBot('wechat')">
                    保存企微机器人配置
                  </el-button>
                </div>
              </el-form>
            </div>
          </div>
        </el-tab-pane>

        <!-- 钉钉机器人Tab -->
        <el-tab-pane label="钉钉机器人" name="dingtalk">
          <div class="tab-content">
            <div class="config-section">
              <el-form
                  ref="dingtalkFormRef"
                  :model="webhookBots.dingtalk"
                  label-position="top"
                  class="config-form"
              >
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="机器人名称">
                      <el-input
                          v-model="webhookBots.dingtalk.name"
                          placeholder="请输入钉钉机器人名称"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="启用">
                      <el-switch v-model="webhookBots.dingtalk.enabled"/>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item label="Webhook URL">
                      <el-input
                          v-model="webhookBots.dingtalk.webhook_url"
                          placeholder="请输入钉钉机器人Webhook URL"
                      />
                      <div class="form-item-hint">
                        钉钉机器人Webhook URL格式：https://oapi.dingtalk.com/robot/send?access_token=...
                      </div>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item label="签名密钥">
                      <el-input
                          v-model="webhookBots.dingtalk.secret"
                          placeholder="请输入钉钉机器人签名密钥（可选）"
                          type="password"
                          show-password
                      />
                      <div class="form-item-hint">
                        钉钉机器人的签名密钥，用于安全验证。如果机器人开启了"加签"安全设置，请填写此字段。
                      </div>
                    </el-form-item>
                  </el-col>
                  <el-col :span="24">
                    <el-form-item label="业务类型">
                      <el-checkbox v-model="webhookBots.dingtalk.enable_ui_automation">UI自动化测试</el-checkbox>
                      <el-checkbox v-model="webhookBots.dingtalk.enable_api_testing">接口测试</el-checkbox>
                    </el-form-item>
                  </el-col>
                </el-row>

                <div class="form-actions">
                  <el-button type="primary" @click="saveWebhookBot('dingtalk')">
                    保存钉钉机器人配置
                  </el-button>
                </div>
              </el-form>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script>
import {Setting} from '@element-plus/icons-vue'
import {ref, reactive, onMounted} from 'vue'
import {ElMessage} from 'element-plus'
import {
  getUnifiedNotificationConfigs,
  createUnifiedNotificationConfig,
  updateUnifiedNotificationConfig
} from '@/api/core.js'

export default {
  name: 'NotificationConfigs',
  components: {
    Setting
  },
  setup() {
    // 数据状态
    // const emailFormRef = ref(null)
    const feishuFormRef = ref(null)
    const wechatFormRef = ref(null)
    const dingtalkFormRef = ref(null)
    const activeTab = ref('feishu')


    // Webhook机器人配置
    const webhookBots = reactive({
      feishu: {
        name: '',
        webhook_url: '',
        enabled: true,
        enable_ui_automation: true,
        enable_api_testing: true
      },
      wechat: {
        name: '',
        webhook_url: '',
        enabled: true,
        enable_ui_automation: true,
        enable_api_testing: true
      },
      dingtalk: {
        name: '',
        webhook_url: '',
        secret: '',
        enabled: true,
        enable_ui_automation: true,
        enable_api_testing: true
      }
    })

    // 获取config_type映射
    const getConfigType = (botType) => {
      const configTypeMap = {
        'feishu': 'webhook_feishu',
        'wechat': 'webhook_wechat',
        'dingtalk': 'webhook_dingtalk'
      }
      return configTypeMap[botType]
    }

    // 保存Webhook机器人配置
    const saveWebhookBot = async (botType) => {
      const formRef = botType === 'feishu' ? feishuFormRef.value :
          botType === 'wechat' ? wechatFormRef.value :
              dingtalkFormRef.value

      if (!formRef) return

      // 验证表单
      await new Promise((resolve) => {
        formRef.validate((valid) => {
          resolve(valid)
        })
      })

      try {
        const configType = getConfigType(botType)

        // 检查是否已存在对应类型的机器人配置
        let webhookConfigId = null
        try {
          const response = await getUnifiedNotificationConfigs({ config_type: configType })
          if (response.data.results && response.data.results.length > 0) {
            webhookConfigId = response.data.results[0].id
          }
        } catch (error) {
          console.log('未找到现有Webhook配置，将创建新配置')
        }

        const botConfig = webhookBots[botType]
        let requestData

        if (webhookConfigId) {
          // 更新现有配置 - 需要先获取现有配置，然后更新webhook_bots
          const configResponse = await getUnifiedNotificationConfigs({ config_type: configType })
          const existingConfig = configResponse.data.results[0]

          // 合并现有的webhook_bots和其他字段
          const updatedWebhookBots = existingConfig.webhook_bots || {}
          const botData = {
            name: botConfig.name || `${botType}机器人`,
            webhook_url: botConfig.webhook_url,
            enabled: botConfig.enabled,
            enable_ui_automation: botConfig.enable_ui_automation,
            enable_api_testing: botConfig.enable_api_testing
          }

          // 钉钉机器人需要额外保存secret字段
          if (botType === 'dingtalk' && botConfig.secret) {
            botData.secret = botConfig.secret
          }

          updatedWebhookBots[botType] = botData

          requestData = {
            name: existingConfig.name || `${botType === 'feishu' ? '飞书' : botType === 'wechat' ? '企微' : '钉钉'}机器人配置`,
            config_type: configType,
            webhook_bots: updatedWebhookBots,
            is_active: true
          }

          // 更新现有配置
          await updateUnifiedNotificationConfig(webhookConfigId, requestData)
          ElMessage.success(`${botType === 'feishu' ? '飞书' : botType === 'wechat' ? '企微' : '钉钉'}机器人配置更新成功`)
        } else {
          // 创建新配置
          const botData = {
            name: botConfig.name || `${botType}机器人`,
            webhook_url: botConfig.webhook_url,
            enabled: botConfig.enabled,
            enable_ui_automation: botConfig.enable_ui_automation,
            enable_api_testing: botConfig.enable_api_testing
          }

          // 钉钉机器人需要额外保存secret字段
          if (botType === 'dingtalk' && botConfig.secret) {
            botData.secret = botConfig.secret
          }

          requestData = {
            name: `${botType === 'feishu' ? '飞书' : botType === 'wechat' ? '企微' : '钉钉'}机器人配置`,
            config_type: configType,
            webhook_bots: {
              [botType]: botData
            },
            is_active: true
          }

          await createUnifiedNotificationConfig(requestData)
          ElMessage.success(`${botType === 'feishu' ? '飞书' : botType === 'wechat' ? '企微' : '钉钉'}机器人配置创建成功`)
        }

        // 重新加载数据以确保状态同步
        fetchWebhookConfig(botType)
      } catch (error) {
        console.error('保存Webhook机器人配置失败:', error)
        ElMessage.error(`${botType === 'feishu' ? '飞书' : botType === 'wechat' ? '企微' : '钉钉'}机器人配置保存失败: ` + (error.response?.data?.detail || error.message))
      }
    }

    // 获取Webhook机器人配置
    const fetchWebhookConfig = async (botType) => {
      try {
        const configType = getConfigType(botType)
        const response = await getUnifiedNotificationConfigs({ config_type: configType })
        if (response.data.results && response.data.results.length > 0) {
          const config = response.data.results[0]
          if (config.webhook_bots && config.webhook_bots[botType]) {
            const bot = config.webhook_bots[botType]
            webhookBots[botType].name = bot.name || ''
            webhookBots[botType].webhook_url = bot.webhook_url || ''
            webhookBots[botType].enabled = bot.enabled !== false
            webhookBots[botType].enable_ui_automation = bot.enable_ui_automation !== false
            webhookBots[botType].enable_api_testing = bot.enable_api_testing !== false
            // 钉钉机器人需要额外读取secret字段
            if (botType === 'dingtalk' && bot.secret) {
              webhookBots[botType].secret = bot.secret
            }
          }
        }
      } catch (error) {
        console.error('获取Webhook机器人配置失败:', error)
      }
    }

    // 获取所有Webhook机器人配置
    const fetchAllWebhookConfigs = async () => {
      try {
        // 遍历所有机器人类型，分别获取配置
        for (const botType of Object.keys(webhookBots)) {
          await fetchWebhookConfig(botType)
        }
      } catch (error) {
        console.error('获取所有Webhook机器人配置失败:', error)
      }
    }

    // 组件挂载时获取数据
    onMounted(async () => {
      try {
        console.log('NotificationConfigs 组件开始初始化')
        await fetchAllWebhookConfigs()
        console.log('NotificationConfigs 组件初始化完成')
      } catch (error) {
        console.error('NotificationConfigs 组件初始化失败:', error)
      }
    })

    return {
      // emailFormRef,
      feishuFormRef,
      wechatFormRef,
      dingtalkFormRef,
      activeTab,
      webhookBots,
      saveWebhookBot,
      fetchWebhookConfig,
      fetchAllWebhookConfigs
    }
  }
}
</script>

<style scoped>
.notification-configs-container {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 32px 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
}

.title-icon {
  margin-right: 12px;
  font-size: 24px;
}

.page-description {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}

.content-wrapper {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.notification-tabs :deep(.el-tabs__nav-wrap) {
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.notification-tabs :deep(.el-tabs__nav-scroll) {
  padding: 0;
}

.notification-tabs :deep(.el-tabs__nav) {
  display: flex;
  background: #f8f9fa;
}

.notification-tabs :deep(.el-tabs__item) {
  padding: 16px 32px;
  font-size: 15px;
  font-weight: 500;
  color: #6c757d;
  border: none;
  position: relative;
}

.notification-tabs :deep(.el-tabs__item:hover) {
  color: #667eea;
  background: rgba(102, 126, 234, 0.08);
}

.notification-tabs :deep(.el-tabs__item.is-active) {
  color: #667eea;
  background: white;
  border-bottom: 2px solid #667eea;
}

.notification-tabs :deep(.el-tabs__active-bar) {
  background-color: #667eea;
  height: 2px;
}

.notification-tabs :deep(.el-tabs__content) {
  padding: 0;
}

.tab-content {
  min-height: 600px;
  padding: 24px;
}

.config-section {
  padding: 20px 0;
}

.config-section h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}


.section-title h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}


.form-item-hint {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.form-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  text-align: right;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .notification-configs-container {
    padding: 16px;
  }

  .page-header {
    padding: 24px 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .notification-tabs :deep(.el-tabs__item) {
    padding: 12px 20px;
    font-size: 14px;
  }

  .tab-content {
    padding: 16px;
  }
}
</style>