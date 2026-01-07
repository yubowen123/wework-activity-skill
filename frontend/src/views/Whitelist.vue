<template>
  <div class="whitelist-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>白名单管理</span>
          <div>
            <el-select
              v-model="selectedChatId"
              placeholder="选择群聊"
              @change="loadWhitelist"
              style="width: 200px; margin-right: 10px;"
            >
              <el-option
                v-for="chat in chats"
                :key="chat.id"
                :label="chat.chat_name"
                :value="chat.id"
              />
            </el-select>
            <el-button type="success" @click="showBatchDialog" :disabled="!selectedChatId">
              <el-icon><Upload /></el-icon>
              批量导入
            </el-button>
            <el-button type="primary" @click="showAddDialog" :disabled="!selectedChatId">
              <el-icon><Plus /></el-icon>
              添加用户
            </el-button>
          </div>
        </div>
      </template>

      <el-alert
        v-if="!selectedChatId"
        title="请先选择一个群聊"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      />

      <el-table v-else :data="whitelist" v-loading="loading" style="width: 100%">
        <el-table-column prop="user_name" label="用户名" min-width="150" />
        <el-table-column prop="user_id" label="用户ID" min-width="150" />
        <el-table-column prop="reason" label="原因" min-width="200" />
        <el-table-column prop="added_by" label="添加人" width="120" />
        <el-table-column label="添加时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="removeFromWhitelist(row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Add Single User Dialog -->
    <el-dialog
      v-model="dialogVisible"
      title="添加白名单用户"
      width="500px"
    >
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="用户名" prop="user_name">
          <el-input v-model="form.user_name" placeholder="请输入用户名（必填）" />
        </el-form-item>
        <el-form-item label="用户ID">
          <el-input v-model="form.user_id" placeholder="选填：企业微信用户ID" />
        </el-form-item>
        <el-form-item label="原因">
          <el-input
            v-model="form.reason"
            type="textarea"
            :rows="3"
            placeholder="选填：添加到白名单的原因"
          />
        </el-form-item>
        <el-form-item label="添加人">
          <el-input v-model="form.added_by" placeholder="选填：添加人" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- Batch Import Dialog -->
    <el-dialog
      v-model="batchDialogVisible"
      title="批量导入白名单"
      width="600px"
    >
      <el-form :model="batchForm" ref="batchFormRef" label-width="100px">
        <el-form-item label="用户列表" required>
          <el-input
            v-model="batchForm.user_names_text"
            type="textarea"
            :rows="10"
            placeholder="每行一个用户名，例如：&#10;张三&#10;李四&#10;王五"
          />
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">
            每行输入一个用户名，支持批量粘贴
          </div>
        </el-form-item>
        <el-form-item label="原因">
          <el-input
            v-model="batchForm.reason"
            placeholder="选填：批量添加的原因"
          />
        </el-form-item>
        <el-form-item label="添加人">
          <el-input v-model="batchForm.added_by" placeholder="选填：添加人" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitBatchForm">确定导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload } from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const chats = ref([])
const whitelist = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const batchDialogVisible = ref(false)
const formRef = ref(null)
const batchFormRef = ref(null)
const selectedChatId = ref(null)

const form = ref({
  user_name: '',
  user_id: '',
  reason: '',
  added_by: ''
})

const batchForm = ref({
  user_names_text: '',
  reason: '',
  added_by: ''
})

const formRules = {
  user_name: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ]
}

watch(() => route.query.chat_id, (chatId) => {
  if (chatId) {
    selectedChatId.value = parseInt(chatId)
    loadWhitelist()
  }
}, { immediate: true })

async function loadChats() {
  try {
    const response = await axios.get('/api/chats')
    chats.value = response.data
  } catch (error) {
    ElMessage.error('加载群聊列表失败')
  }
}

async function loadWhitelist() {
  if (!selectedChatId.value) return

  loading.value = true
  try {
    const response = await axios.get(`/api/whitelist/chat/${selectedChatId.value}`)
    whitelist.value = response.data
  } catch (error) {
    ElMessage.error('加载白名单失败')
  } finally {
    loading.value = false
  }
}

function showAddDialog() {
  form.value = {
    chat_id: selectedChatId.value,
    user_name: '',
    user_id: '',
    reason: '',
    added_by: ''
  }
  dialogVisible.value = true
}

function showBatchDialog() {
  batchForm.value = {
    chat_id: selectedChatId.value,
    user_names_text: '',
    reason: '',
    added_by: ''
  }
  batchDialogVisible.value = true
}

async function submitForm() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await axios.post('/api/whitelist', form.value)
        ElMessage.success('添加成功')
        dialogVisible.value = false
        loadWhitelist()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '添加失败')
      }
    }
  })
}

async function submitBatchForm() {
  if (!batchForm.value.user_names_text.trim()) {
    ElMessage.warning('请输入用户名列表')
    return
  }

  const userNames = batchForm.value.user_names_text
    .split('\n')
    .map(name => name.trim())
    .filter(name => name.length > 0)

  if (userNames.length === 0) {
    ElMessage.warning('请输入有效的用户名')
    return
  }

  try {
    const response = await axios.post('/api/whitelist/batch', {
      chat_id: selectedChatId.value,
      user_names: userNames,
      reason: batchForm.value.reason,
      added_by: batchForm.value.added_by
    })

    ElMessage.success(response.data.message)
    batchDialogVisible.value = false
    loadWhitelist()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '批量导入失败')
  }
}

function removeFromWhitelist(item) {
  ElMessageBox.confirm(
    `确定要将"${item.user_name}"从白名单移除吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await axios.delete(`/api/whitelist/${item.id}`)
      ElMessage.success('移除成功')
      loadWhitelist()
    } catch (error) {
      ElMessage.error('移除失败')
    }
  }).catch(() => {})
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadChats()
})
</script>

<style scoped>
.whitelist-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}
</style>
