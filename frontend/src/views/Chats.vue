<template>
  <div class="chats-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>群聊管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            添加群聊
          </el-button>
        </div>
      </template>

      <el-table :data="chats" v-loading="loading" style="width: 100%">
        <el-table-column prop="chat_name" label="群聊名称" min-width="200" />
        <el-table-column prop="chat_id" label="群聊ID" width="150" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.enabled"
              @change="toggleChat(row)"
              active-color="#13ce66"
              inactive-color="#dcdfe6"
            />
          </template>
        </el-table-column>
        <el-table-column label="自动移除" width="100">
          <template #default="{ row }">
            <el-tag :type="row.auto_remove ? 'warning' : 'info'" size="small">
              {{ row.auto_remove ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="rules_count" label="规则数" width="100" />
        <el-table-column prop="active_rules" label="活跃规则" width="100" />
        <el-table-column prop="whitelist_count" label="白名单" width="100" />
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewRules(row)">规则</el-button>
            <el-button size="small" @click="viewWhitelist(row)">白名单</el-button>
            <el-button size="small" type="primary" @click="editChat(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteChat(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Add/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'add' ? '添加群聊' : '编辑群聊'"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="群聊名称" prop="chat_name">
          <el-input v-model="form.chat_name" placeholder="请输入群聊名称" />
        </el-form-item>
        <el-form-item label="群聊ID" prop="chat_id">
          <el-input v-model="form.chat_id" placeholder="选填：企业微信群聊ID" />
        </el-form-item>
        <el-form-item label="启用监控" prop="enabled">
          <el-switch v-model="form.enabled" />
        </el-form-item>
        <el-form-item label="自动移除" prop="auto_remove">
          <el-switch v-model="form.auto_remove" />
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">
            开启后，满足规则条件的用户将被自动移除
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const chats = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref('add')
const formRef = ref(null)

const form = ref({
  chat_name: '',
  chat_id: '',
  enabled: true,
  auto_remove: false
})

const rules = {
  chat_name: [
    { required: true, message: '请输入群聊名称', trigger: 'blur' }
  ]
}

async function loadChats() {
  loading.value = true
  try {
    const response = await axios.get('/api/chats')
    chats.value = response.data
  } catch (error) {
    ElMessage.error('加载群聊列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

function showAddDialog() {
  dialogMode.value = 'add'
  form.value = {
    chat_name: '',
    chat_id: '',
    enabled: true,
    auto_remove: false
  }
  dialogVisible.value = true
}

function editChat(chat) {
  dialogMode.value = 'edit'
  form.value = {
    id: chat.id,
    chat_name: chat.chat_name,
    chat_id: chat.chat_id || '',
    enabled: chat.enabled,
    auto_remove: chat.auto_remove
  }
  dialogVisible.value = true
}

async function submitForm() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (dialogMode.value === 'add') {
          await axios.post('/api/chats', form.value)
          ElMessage.success('添加成功')
        } else {
          await axios.put(`/api/chats/${form.value.id}`, form.value)
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        loadChats()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '操作失败')
      }
    }
  })
}

async function toggleChat(chat) {
  try {
    await axios.post(`/api/chats/${chat.id}/toggle`)
    ElMessage.success(chat.enabled ? '已启用' : '已禁用')
  } catch (error) {
    chat.enabled = !chat.enabled
    ElMessage.error('操作失败')
  }
}

function deleteChat(chat) {
  ElMessageBox.confirm(
    `确定要删除群聊"${chat.chat_name}"吗？删除后相关规则和白名单也将被删除。`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await axios.delete(`/api/chats/${chat.id}`)
      ElMessage.success('删除成功')
      loadChats()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

function viewRules(chat) {
  router.push({ path: '/rules', query: { chat_id: chat.id } })
}

function viewWhitelist(chat) {
  router.push({ path: '/whitelist', query: { chat_id: chat.id } })
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadChats()
})
</script>

<style scoped>
.chats-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}
</style>
