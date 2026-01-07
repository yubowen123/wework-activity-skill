<template>
  <div class="analytics-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据分析</span>
          <el-button type="primary" @click="loadData">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="12">
          <div class="chart-container">
            <h3>群聊活跃度趋势</h3>
            <div ref="activityChart" style="width: 100%; height: 300px;"></div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="chart-container">
            <h3>规则执行统计</h3>
            <div ref="ruleChart" style="width: 100%; height: 300px;"></div>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <div class="chart-container">
            <h3>用户消息分布</h3>
            <div ref="messageChart" style="width: 100%; height: 300px;"></div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="chart-container">
            <h3>移除原因统计</h3>
            <div ref="removalChart" style="width: 100%; height: 300px;"></div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-alert
      title="数据分析功能"
      type="info"
      style="margin-top: 20px;"
      :closable="false"
    >
      <p>此页面展示群聊活跃度数据分析，包括：</p>
      <ul>
        <li>群聊活跃度趋势 - 展示各群聊每日消息数量变化</li>
        <li>规则执行统计 - 统计各类规则的触发和执行情况</li>
        <li>用户消息分布 - 分析群内用户的消息数量分布</li>
        <li>移除原因统计 - 统计用户被移除的主要原因</li>
      </ul>
      <p style="margin-top: 10px; color: #E6A23C;">
        注意：实际数据需要RPA模块采集群聊消息后才能展示
      </p>
    </el-alert>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const activityChart = ref(null)
const ruleChart = ref(null)
const messageChart = ref(null)
const removalChart = ref(null)

function initCharts() {
  // Activity Chart
  if (activityChart.value) {
    const chart1 = echarts.init(activityChart.value)
    chart1.setOption({
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['群聊A', '群聊B', '群聊C']
      },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      },
      yAxis: {
        type: 'value',
        name: '消息数'
      },
      series: [
        {
          name: '群聊A',
          type: 'line',
          data: [120, 132, 101, 134, 90, 230, 210]
        },
        {
          name: '群聊B',
          type: 'line',
          data: [220, 182, 191, 234, 290, 330, 310]
        },
        {
          name: '群聊C',
          type: 'line',
          data: [150, 232, 201, 154, 190, 330, 410]
        }
      ]
    })
  }

  // Rule Chart
  if (ruleChart.value) {
    const chart2 = echarts.init(ruleChart.value)
    chart2.setOption({
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '规则类型',
          type: 'pie',
          radius: '50%',
          data: [
            { value: 1048, name: '连续N天不活跃' },
            { value: 735, name: '月度最少消息数' },
            { value: 580, name: '周度最少消息数' },
            { value: 484, name: '长期潜水' }
          ]
        }
      ]
    })
  }

  // Message Chart
  if (messageChart.value) {
    const chart3 = echarts.init(messageChart.value)
    chart3.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: ['0-10条', '11-50条', '51-100条', '101-200条', '200+条']
      },
      yAxis: {
        type: 'value',
        name: '用户数'
      },
      series: [
        {
          name: '用户数',
          type: 'bar',
          data: [45, 82, 63, 34, 12],
          itemStyle: {
            color: '#409EFF'
          }
        }
      ]
    })
  }

  // Removal Chart
  if (removalChart.value) {
    const chart4 = echarts.init(removalChart.value)
    chart4.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'value'
      },
      yAxis: {
        type: 'category',
        data: ['连续7天不活跃', '月消息数不足', '长期潜水', '周消息数不足']
      },
      series: [
        {
          name: '移除人数',
          type: 'bar',
          data: [89, 67, 45, 23],
          itemStyle: {
            color: '#F56C6C'
          }
        }
      ]
    })
  }
}

function loadData() {
  ElMessage.info('模拟数据已加载')
  initCharts()
}

onMounted(() => {
  setTimeout(() => {
    initCharts()
  }, 100)
})
</script>

<style scoped>
.analytics-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.chart-container {
  background: white;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chart-container h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #303133;
}

ul {
  padding-left: 20px;
}

ul li {
  margin: 5px 0;
}
</style>
