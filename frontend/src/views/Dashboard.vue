<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #409EFF;">
              <el-icon size="40"><ChatDotRound /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_chats }}</div>
              <div class="stat-label">监控群聊</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #67C23A;">
              <el-icon size="40"><Setting /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_rules }}</div>
              <div class="stat-label">活跃规则</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #E6A23C;">
              <el-icon size="40"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.whitelist_count }}</div>
              <div class="stat-label">白名单用户</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #F56C6C;">
              <el-icon size="40"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pending_actions }}</div>
              <div class="stat-label">待处理</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快速操作</span>
            </div>
          </template>
          <el-space direction="vertical" :size="15" style="width: 100%;">
            <el-button type="primary" @click="$router.push('/chats')" style="width: 100%;">
              <el-icon><Plus /></el-icon>
              添加监控群聊
            </el-button>
            <el-button type="success" @click="$router.push('/rules')" style="width: 100%;">
              <el-icon><Setting /></el-icon>
              配置活跃规则
            </el-button>
            <el-button @click="$router.push('/whitelist')" style="width: 100%;">
              <el-icon><User /></el-icon>
              管理白名单
            </el-button>
            <el-button @click="$router.push('/analytics')" style="width: 100%;">
              <el-icon><TrendCharts /></el-icon>
              查看数据分析
            </el-button>
          </el-space>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统信息</span>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="系统状态">
              <el-tag type="success">运行中</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="后端服务">
              <el-tag :type="backendStatus ? 'success' : 'danger'">
                {{ backendStatus ? '正常' : '异常' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="版本">v1.0.0</el-descriptions-item>
            <el-descriptions-item label="最后更新">{{ new Date().toLocaleDateString() }}</el-descriptions-item>
          </el-descriptions>

          <div style="margin-top: 15px;">
            <el-button type="primary" link @click="openDocs">
              <el-icon><Document /></el-icon>
              查看API文档
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>监控群聊列表</span>
              <el-button type="primary" size="small" @click="$router.push('/chats')">
                查看全部
              </el-button>
            </div>
          </template>
          <el-table :data="recentChats" style="width: 100%">
            <el-table-column prop="chat_name" label="群聊名称" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.enabled ? 'success' : 'info'">
                  {{ row.enabled ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="rules_count" label="规则数" width="100" />
            <el-table-column prop="whitelist_count" label="白名单" width="100" />
            <el-table-column label="自动移除" width="100">
              <template #default="{ row }">
                <el-tag :type="row.auto_remove ? 'warning' : 'info'" size="small">
                  {{ row.auto_remove ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatDotRound, Setting, User, Warning, Plus, TrendCharts, Document } from '@element-plus/icons-vue'
import axios from 'axios'

const stats = ref({
  total_chats: 0,
  total_rules: 0,
  whitelist_count: 0,
  pending_actions: 0
})

const recentChats = ref([])
const backendStatus = ref(false)

async function loadData() {
  try {
    // Load chats
    const chatsRes = await axios.get('/api/chats')
    recentChats.value = chatsRes.data.slice(0, 5)

    // Calculate stats
    stats.value.total_chats = chatsRes.data.filter(c => c.enabled).length
    stats.value.total_rules = chatsRes.data.reduce((sum, c) => sum + (c.active_rules || 0), 0)
    stats.value.whitelist_count = chatsRes.data.reduce((sum, c) => sum + (c.whitelist_count || 0), 0)

    // Check backend
    const healthRes = await axios.get('/api/health')
    backendStatus.value = healthRes.data.status === 'ok'
  } catch (error) {
    ElMessage.error('加载数据失败')
    console.error(error)
  }
}

function openDocs() {
  window.open('http://localhost:8000/docs', '_blank')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.stat-card {
  cursor: default;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 80px;
  height: 80px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}
</style>
