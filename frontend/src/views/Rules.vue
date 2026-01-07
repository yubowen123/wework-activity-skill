<template>
  <div class="rules-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>规则配置</span>
          <div>
            <el-select
              v-model="selectedChatId"
              placeholder="选择群聊"
              @change="loadRules"
              style="width: 200px; margin-right: 10px;"
            >
              <el-option
                v-for="chat in chats"
                :key="chat.id"
                :label="chat.chat_name"
                :value="chat.id"
              />
            </el-select>
            <el-button type="primary" @click="showAddDialog" :disabled="!selectedChatId">
              <el-icon><Plus /></el-icon>
              添加规则
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

      <el-table v-else :data="rules" v-loading="loading" style="width: 100%">
        <el-table-column prop="rule_name" label="规则名称" min-width="150" />
        <el-table-column label="规则类型" min-width="150">
          <template #default="{ row }">
            {{ getRuleTypeName(row.rule_type) }}
          </template>
        </el-table-column>
        <el-table-column label="配置" min-width="200">
          <template #default="{ row }">
            <el-tag v-for="(value, key) in row.rule_config" :key="key" size="small" style="margin-right: 5px;">
              {{ key }}: {{ value }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.enabled"
              @change="toggleRule(row)"
              active-color="#13ce66"
              inactive-color="#dcdfe6"
            />
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="editRule(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteRule(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Add/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'add' ? '添加规则' : '编辑规则'"
      width="600px"
    >
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="规则名称" prop="rule_name">
          <el-input v-model="form.rule_name" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="规则模板" prop="rule_type" v-if="dialogMode === 'add'">
          <el-select v-model="form.rule_type" placeholder="选择规则类型" @change="onRuleTypeChange" style="width: 100%;">
            <el-option
              v-for="template in ruleTemplates"
              :key="template.type"
              :label="template.name"
              :value="template.type"
            >
              <div>
                <div>{{ template.name }}</div>
                <div style="font-size: 12px; color: #909399;">{{ template.description }}</div>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <!-- Dynamic config fields -->
        <div v-if="currentTemplate">
          <el-form-item
            v-for="(config, key) in currentTemplate.config_schema"
            :key="key"
            :label="config.label"
          >
            <el-input-number
              v-model="form.rule_config[key]"
              :min="config.min"
              :max="config.max"
              style="width: 100%;"
            />
          </el-form-item>
        </div>

        <el-form-item label="优先级" prop="priority">
          <el-input-number v-model="form.priority" :min="0" :max="100" style="width: 100%;" />
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">
            数字越大优先级越高
          </div>
        </el-form-item>
        <el-form-item label="启用规则" prop="enabled">
          <el-switch v-model="form.enabled" />
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
import { ref, onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const chats = ref([])
const rules = ref([])
const ruleTemplates = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref('add')
const formRef = ref(null)
const selectedChatId = ref(null)

const form = ref({
  rule_name: '',
  rule_type: '',
  rule_config: {},
  priority: 0,
  enabled: true
})

const formRules = {
  rule_name: [
    { required: true, message: '请输入规则名称', trigger: 'blur' }
  ],
  rule_type: [
    { required: true, message: '请选择规则类型', trigger: 'change' }
  ]
}

const currentTemplate = computed(() => {
  return ruleTemplates.value.find(t => t.type === form.value.rule_type)
})

watch(() => route.query.chat_id, (chatId) => {
  if (chatId) {
    selectedChatId.value = parseInt(chatId)
    loadRules()
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

async function loadRules() {
  if (!selectedChatId.value) return

  loading.value = true
  try {
    const response = await axios.get(`/api/rules/chat/${selectedChatId.value}`)
    rules.value = response.data
  } catch (error) {
    ElMessage.error('加载规则列表失败')
  } finally {
    loading.value = false
  }
}

async function loadTemplates() {
  try {
    const response = await axios.get('/api/rules/templates/list')
    ruleTemplates.value = response.data
  } catch (error) {
    ElMessage.error('加载规则模板失败')
  }
}

function showAddDialog() {
  dialogMode.value = 'add'
  form.value = {
    chat_id: selectedChatId.value,
    rule_name: '',
    rule_type: '',
    rule_config: {},
    priority: 0,
    enabled: true
  }
  dialogVisible.value = true
}

function editRule(rule) {
  dialogMode.value = 'edit'
  form.value = {
    id: rule.id,
    rule_name: rule.rule_name,
    rule_type: rule.rule_type,
    rule_config: { ...rule.rule_config },
    priority: rule.priority,
    enabled: rule.enabled
  }
  dialogVisible.value = true
}

function onRuleTypeChange() {
  // Initialize config with default values
  const template = currentTemplate.value
  if (template) {
    const config = {}
    for (const [key, schema] of Object.entries(template.config_schema)) {
      config[key] = schema.default
    }
    form.value.rule_config = config
  }
}

async function submitForm() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (dialogMode.value === 'add') {
          await axios.post('/api/rules', form.value)
          ElMessage.success('添加成功')
        } else {
          await axios.put(`/api/rules/${form.value.id}`, form.value)
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        loadRules()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '操作失败')
      }
    }
  })
}

async function toggleRule(rule) {
  try {
    await axios.post(`/api/rules/${rule.id}/toggle`)
    ElMessage.success(rule.enabled ? '已启用' : '已禁用')
  } catch (error) {
    rule.enabled = !rule.enabled
    ElMessage.error('操作失败')
  }
}

function deleteRule(rule) {
  ElMessageBox.confirm(
    `确定要删除规则"${rule.rule_name}"吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await axios.delete(`/api/rules/${rule.id}`)
      ElMessage.success('删除成功')
      loadRules()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

function getRuleTypeName(type) {
  const template = ruleTemplates.value.find(t => t.type === type)
  return template ? template.name : type
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadChats()
  loadTemplates()
})
</script>

<style scoped>
.rules-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}
</style>
