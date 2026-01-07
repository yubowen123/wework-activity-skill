<template>
  <div class="history-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>执行历史</span>
          <div>
            <el-select
              v-model="filterType"
              placeholder="筛选类型"
              style="width: 150px; margin-right: 10px;"
              @change="loadHistory"
            >
              <el-option label="全部" value="" />
              <el-option label="成功" value="success" />
              <el-option label="失败" value="failed" />
              <el-option label="警告" value="warning" />
            </el-select>
            <el-button @click="loadHistory">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="history" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="执行时间" width="180">
          <template #default="{ row }">
            {{ row.execution_time }}
          </template>
        </el-table-column>
        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.type)">
              {{ getTypeName(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="chat_name" label="群聊" width="150" />
        <el-table-column prop="rule_name" label="规则" width="150" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="affected_users" label="影响用户数" width="120" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadHistory"
        @current-change="loadHistory"
        style="margin-top: 20px; text-align: right;"
      />
    </el-card>

    <!-- Detail Dialog -->
    <el-dialog
      v-model="detailVisible"
      title="执行详情"
      width="700px"
    >
      <el-descriptions :column="2" border v-if="selectedRecord">
        <el-descriptions-item label="执行ID">{{ selectedRecord.id }}</el-descriptions-item>
        <el-descriptions-item label="执行时间">{{ selectedRecord.execution_time }}</el-descriptions-item>
        <el-descriptions-item label="类型">
          <el-tag :type="getTypeColor(selectedRecord.type)">
            {{ getTypeName(selectedRecord.type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusColor(selectedRecord.status)">
            {{ selectedRecord.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="群聊">{{ selectedRecord.chat_name }}</el-descriptions-item>
        <el-descriptions-item label="规则">{{ selectedRecord.rule_name }}</el-descriptions-item>
        <el-descriptions-item label="影响用户数" :span="2">{{ selectedRecord.affected_users }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ selectedRecord.description }}</el-descriptions-item>
        <el-descriptions-item label="详细信息" :span="2">
          <pre style="max-height: 200px; overflow-y: auto;">{{ selectedRecord.details }}</pre>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button type="primary" @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-alert
      title="执行历史说明"
      type="info"
      style="margin-top: 20px;"
      :closable="false"
    >
      <p>此页面记录所有自动化操作的执行历史，包括：</p>
      <ul>
        <li>规则检查 - 定期检查群聊用户是否满足规则条件</li>
        <li>自动移除 - 根据规则自动移除不活跃用户</li>
        <li>数据同步 - 从企业微信同步群聊消息数据</li>
        <li>手动操作 - 管理员手动执行的操作</li>
      </ul>
      <p style="margin-top: 10px; color: #E6A23C;">
        注意：当前显示的是模拟数据，实际数据由RPA模块生成
      </p>
    </el-alert>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'

const history = ref([])
const loading = ref(false)
const filterType = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const detailVisible = ref(false)
const selectedRecord = ref(null)

function loadHistory() {
  loading.value = true

  // Simulate data
  setTimeout(() => {
    history.value = [
      {
        id: 1,
        execution_time: '2024-01-07 14:30:25',
        type: 'rule_check',
        chat_name: '技术交流群',
        rule_name: '连续7天不活跃',
        status: '成功',
        affected_users: 5,
        description: '检查到5名用户连续7天未发送消息',
        details: JSON.stringify({
          users: ['用户A', '用户B', '用户C', '用户D', '用户E'],
          rule_config: { days: 7 }
        }, null, 2)
      },
      {
        id: 2,
        execution_time: '2024-01-07 14:32:10',
        type: 'auto_remove',
        chat_name: '技术交流群',
        rule_name: '连续7天不活跃',
        status: '成功',
        affected_users: 3,
        description: '自动移除3名不活跃用户',
        details: JSON.stringify({
          removed_users: ['用户A', '用户C', '用户E'],
          skipped_users: ['用户B（白名单）', '用户D（白名单）']
        }, null, 2)
      },
      {
        id: 3,
        execution_time: '2024-01-07 13:00:00',
        type: 'data_sync',
        chat_name: '产品讨论组',
        rule_name: '-',
        status: '成功',
        affected_users: 0,
        description: '同步最近24小时消息数据',
        details: JSON.stringify({
          messages_synced: 342,
          time_range: '2024-01-06 13:00 - 2024-01-07 13:00'
        }, null, 2)
      },
      {
        id: 4,
        execution_time: '2024-01-07 10:15:30',
        type: 'manual',
        chat_name: '运营策划群',
        rule_name: '-',
        status: '成功',
        affected_users: 1,
        description: '管理员手动添加白名单用户',
        details: JSON.stringify({
          user: '王经理',
          operator: '管理员A',
          reason: '核心成员'
        }, null, 2)
      },
      {
        id: 5,
        execution_time: '2024-01-07 09:00:15',
        type: 'rule_check',
        chat_name: '客户服务群',
        rule_name: '月度最少消息数',
        status: '警告',
        affected_users: 12,
        description: '检查到12名用户本月消息数不足10条',
        details: JSON.stringify({
          threshold: 10,
          users_below_threshold: 12
        }, null, 2)
      }
    ]
    total.value = history.value.length
    loading.value = false
  }, 500)
}

function viewDetail(record) {
  selectedRecord.value = record
  detailVisible.value = true
}

function getTypeColor(type) {
  const colors = {
    'rule_check': '',
    'auto_remove': 'danger',
    'data_sync': 'success',
    'manual': 'warning'
  }
  return colors[type] || ''
}

function getTypeName(type) {
  const names = {
    'rule_check': '规则检查',
    'auto_remove': '自动移除',
    'data_sync': '数据同步',
    'manual': '手动操作'
  }
  return names[type] || type
}

function getStatusColor(status) {
  const colors = {
    '成功': 'success',
    '失败': 'danger',
    '警告': 'warning'
  }
  return colors[status] || ''
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.history-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
}

ul {
  padding-left: 20px;
}

ul li {
  margin: 5px 0;
}
</style>
