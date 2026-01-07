<template>
  <el-container class="layout-container">
    <el-aside width="200px">
      <div class="logo">
        <h2>企微管理</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/chats">
          <el-icon><ChatDotRound /></el-icon>
          <span>群聊管理</span>
        </el-menu-item>
        <el-menu-item index="/rules">
          <el-icon><Setting /></el-icon>
          <span>规则配置</span>
        </el-menu-item>
        <el-menu-item index="/whitelist">
          <el-icon><User /></el-icon>
          <span>白名单</span>
        </el-menu-item>
        <el-menu-item index="/analytics">
          <el-icon><TrendCharts /></el-icon>
          <span>数据分析</span>
        </el-menu-item>
        <el-menu-item index="/history">
          <el-icon><Clock /></el-icon>
          <span>执行历史</span>
        </el-menu-item>
        <el-menu-item index="/rpa">
          <el-icon><Monitor /></el-icon>
          <span>RPA 控制</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header>
        <div class="header-content">
          <h3>{{ pageTitle }}</h3>
          <div class="header-right">
            <el-tag type="success">系统运行中</el-tag>
          </div>
        </div>
      </el-header>

      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { DataAnalysis, ChatDotRound, Setting, User, TrendCharts, Clock, Monitor } from '@element-plus/icons-vue'

const route = useRoute()

const activeMenu = computed(() => route.path)

const pageTitle = computed(() => route.meta.title || '企业微信活跃度管理')
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.el-aside {
  background-color: #304156;
  color: #fff;
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #444;
}

.logo h2 {
  color: #fff;
  margin: 0;
  font-size: 20px;
}

.el-menu-vertical {
  border-right: none;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
