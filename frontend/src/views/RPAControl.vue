<template>
  <div class="rpa-control">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>🤖 RPA 控制面板</span>
          <el-button
            :type="rpaStatus.running ? 'success' : 'danger'"
            :icon="rpaStatus.running ? 'CircleCheck' : 'CircleClose'"
            size="small"
            circle
          />
        </div>
      </template>

      <!-- RPA 状态 -->
      <el-row :gutter="20" class="status-section">
        <el-col :span="24">
          <el-alert
            :title="rpaStatus.message"
            :type="rpaStatus.running ? 'success' : 'warning'"
            show-icon
            :closable="false"
          />
        </el-col>
      </el-row>

      <!-- 定时任务列表 -->
      <el-row :gutter="20" class="jobs-section" v-if="rpaStatus.running">
        <el-col :span="24">
          <h3>📅 定时任务</h3>
          <el-table :data="rpaStatus.jobs" style="width: 100%">
            <el-table-column prop="name" label="任务名称" />
            <el-table-column prop="next_run_time" label="下次执行时间" width="220">
              <template #default="scope">
                {{ formatTime(scope.row.next_run_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="trigger" label="触发器" />
          </el-table>
        </el-col>
      </el-row>

      <!-- 快捷操作按钮 -->
      <el-row :gutter="20" class="actions-section">
        <el-col :span="24">
          <h3>⚡ 快捷操作</h3>
          <el-space wrap>
            <el-button
              type="primary"
              :icon="testLoading ? 'Loading' : 'View'"
              @click="testWeWork"
              :loading="testLoading"
            >
              测试企业微信连接
            </el-button>

            <el-button
              type="success"
              :icon="collectLoading ? 'Loading' : 'Download'"
              @click="collectNow"
              :loading="collectLoading"
            >
              立即采集消息
            </el-button>

            <el-button
              type="warning"
              :icon="executeLoading ? 'Loading' : 'VideoPlay'"
              @click="showExecuteDialog"
              :loading="executeLoading"
            >
              执行规则
            </el-button>

            <el-button
              type="info"
              icon="Refresh"
              @click="restartScheduler"
              :loading="restartLoading"
            >
              重启调度器
            </el-button>
          </el-space>
        </el-col>
      </el-row>

      <!-- 测试打开群聊 -->
      <el-row :gutter="20" class="test-section">
        <el-col :span="24">
          <h3>🧪 测试功能</h3>
          <el-input
            v-model="testChatName"
            placeholder="输入群聊名称测试打开"
            style="width: 300px; margin-right: 10px"
          />
          <el-button
            type="primary"
            @click="testOpenChat"
            :loading="chatTestLoading"
          >
            测试打开群聊
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 执行规则对话框 -->
    <el-dialog v-model="executeDialogVisible" title="执行规则" width="500px">
      <el-form :model="executeForm" label-width="120px">
        <el-form-item label="执行模式">
          <el-radio-group v-model="executeForm.dryRun">
            <el-radio :label="true">模拟运行（推荐）</el-radio>
            <el-radio :label="false">实际执行</el-radio>
          </el-radio-group>
          <div class="form-tip">
            <el-alert
              title="模拟运行不会真正踢人，只会显示会被影响的用户"
              type="info"
              :closable="false"
              show-icon
            />
          </div>
        </el-form-item>

        <el-form-item label="执行范围">
          <el-radio-group v-model="executeForm.executeAll">
            <el-radio :label="true">执行所有规则</el-radio>
            <el-radio :label="false">执行指定规则</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="规则ID" v-if="!executeForm.executeAll">
          <el-input-number v-model="executeForm.ruleId" :min="1" />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="executeDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            @click="executeRules"
            :loading="executeLoading"
          >
            执行
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const API_BASE = '/api/rpa'

// RPA 状态
const rpaStatus = ref({
  running: false,
  message: '正在加载...',
  jobs: []
})

// 加载状态
const testLoading = ref(false)
const collectLoading = ref(false)
const executeLoading = ref(false)
const restartLoading = ref(false)
const chatTestLoading = ref(false)

// 测试群聊名称
const testChatName = ref('')

// 执行规则对话框
const executeDialogVisible = ref(false)
const executeForm = ref({
  dryRun: true,
  executeAll: true,
  ruleId: null
})

// 定时刷新状态
let statusTimer = null

// 获取 RPA 状态
const fetchStatus = async () => {
  try {
    const response = await axios.get(`${API_BASE}/status`)
    rpaStatus.value = response.data
  } catch (error) {
    console.error('获取 RPA 状态失败:', error)
    rpaStatus.value = {
      running: false,
      message: '获取状态失败',
      jobs: []
    }
  }
}

// 测试企业微信连接
const testWeWork = async () => {
  testLoading.value = true
  try {
    const response = await axios.post(`${API_BASE}/test-wework`)
    if (response.data.success) {
      ElMessage.success(response.data.message)
      if (response.data.details?.screenshot) {
        ElMessage.info(`截图已保存: ${response.data.details.screenshot}`)
      }
    } else {
      ElMessage.warning(response.data.message)
    }
  } catch (error) {
    ElMessage.error('测试失败: ' + error.message)
  } finally {
    testLoading.value = false
  }
}

// 立即采集消息
const collectNow = async () => {
  const confirmed = await ElMessageBox.confirm(
    '确定要立即采集所有监控群聊的消息吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).catch(() => false)

  if (!confirmed) return

  collectLoading.value = true
  try {
    const response = await axios.post(`${API_BASE}/collect-now`)
    if (response.data.success) {
      ElMessage.success(response.data.message)
    } else {
      ElMessage.warning('采集失败')
    }
  } catch (error) {
    ElMessage.error('采集失败: ' + error.message)
  } finally {
    collectLoading.value = false
  }
}

// 显示执行规则对话框
const showExecuteDialog = () => {
  executeDialogVisible.value = true
}

// 执行规则
const executeRules = async () => {
  executeLoading.value = true
  try {
    const params = {
      dry_run: executeForm.value.dryRun,
      rule_id: executeForm.value.executeAll ? null : executeForm.value.ruleId
    }

    const response = await axios.post(`${API_BASE}/execute-rules`, params)

    if (response.data.success) {
      ElMessage.success(response.data.message)

      // 显示结果详情
      if (response.data.results && response.data.results.length > 0) {
        let detailMsg = '执行结果:\n\n'
        response.data.results.forEach((result, index) => {
          detailMsg += `${index + 1}. ${result.rule_name || '规则' + result.rule_id}\n`
          detailMsg += `   ${result.message}\n`
          if (result.affected_users && result.affected_users.length > 0) {
            detailMsg += `   受影响用户: ${result.affected_users.join(', ')}\n`
          }
          detailMsg += '\n'
        })

        ElMessageBox.alert(detailMsg, '执行结果', {
          confirmButtonText: '确定',
          type: 'info'
        })
      }

      executeDialogVisible.value = false
    } else {
      ElMessage.warning('执行失败')
    }
  } catch (error) {
    ElMessage.error('执行失败: ' + error.message)
  } finally {
    executeLoading.value = false
  }
}

// 重启调度器
const restartScheduler = async () => {
  const confirmed = await ElMessageBox.confirm(
    '确定要重启 RPA 调度器吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).catch(() => false)

  if (!confirmed) return

  restartLoading.value = true
  try {
    const response = await axios.post(`${API_BASE}/restart`)
    if (response.data.success) {
      ElMessage.success(response.data.message)
      // 刷新状态
      setTimeout(fetchStatus, 2000)
    }
  } catch (error) {
    ElMessage.error('重启失败: ' + error.message)
  } finally {
    restartLoading.value = false
  }
}

// 测试打开群聊
const testOpenChat = async () => {
  if (!testChatName.value.trim()) {
    ElMessage.warning('请输入群聊名称')
    return
  }

  chatTestLoading.value = true
  try {
    const response = await axios.post(
      `${API_BASE}/test-chat?chat_name=${encodeURIComponent(testChatName.value)}`
    )

    if (response.data.success) {
      ElMessage.success(response.data.message)
      if (response.data.details?.screenshot) {
        ElMessage.info(`截图已保存: ${response.data.details.screenshot}`)
      }
    } else {
      ElMessage.warning(response.data.message)
    }
  } catch (error) {
    ElMessage.error('测试失败: ' + error.message)
  } finally {
    chatTestLoading.value = false
  }
}

// 格式化时间
const formatTime = (isoString) => {
  if (!isoString) return '-'
  const date = new Date(isoString)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  // 初始加载
  fetchStatus()

  // 每10秒刷新状态
  statusTimer = setInterval(fetchStatus, 10000)
})

onUnmounted(() => {
  if (statusTimer) {
    clearInterval(statusTimer)
  }
})
</script>

<style scoped>
.rpa-control {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-section {
  margin-bottom: 20px;
}

.jobs-section {
  margin-bottom: 20px;
}

.jobs-section h3 {
  margin-bottom: 10px;
}

.actions-section {
  margin-bottom: 20px;
}

.actions-section h3 {
  margin-bottom: 10px;
}

.test-section h3 {
  margin-bottom: 10px;
}

.form-tip {
  margin-top: 10px;
}
</style>
