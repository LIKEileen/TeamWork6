<template>
  <div class="board-container">
    <div class="header-row">
      <h2 class="page-title">组织看板</h2>
      <div class="toolbar">
        <el-select v-model="selectedOrgId" placeholder="选择组织" @change="loadHeatmap">
          <el-option
            v-for="org in allOrgs"
            :key="org.id"
            :label="org.name"
            :value="org.id"
          />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          :disabled-date="limitMax15Days"
          @change="loadHeatmap"
        />
        <el-color-picker v-model="baseColor" :predefine="presetColors" @change="saveColor" />
      </div>
    </div>

    <el-card shadow="hover" class="org-card" v-if="currentOrg">
      <div class="org-header">
        <span class="org-name">{{ currentOrg.name }}</span>
        <el-tag size="small" type="success" effect="light">成员：{{ currentOrg.members }}</el-tag>
      </div>
      <HeatmapGrid
        :data="currentOrg.heatmap"
        :color="baseColor"
        :start-date="dateRange[0]"
        :end-date="dateRange[1]"
      />
    </el-card>

    <el-empty v-else description="请选择一个组织" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import HeatmapGrid from '@/components/HeatmapGrid.vue'
import { IS_DEV } from '@/config'
import dayjs from 'dayjs'

import { getUserOrgs, getOrgHeatmap } from '@/api/org'
import { lo } from 'element-plus/es/locale/index.mjs'

const baseColor = ref(localStorage.getItem('heatmap_color') || '#ff4d4f')
const presetColors = ['#ff4d4f', '#409EFF', '#67C23A', '#E6A23C', '#909399']
const allOrgs = ref([])
const selectedOrgId = ref(localStorage.getItem('heatmap_selected_org') || null)
const selectedOrgName = ref(localStorage.getItem('heatmap_selected_org_name') || null)
const currentOrg = ref(null)

const today = dayjs().format('YYYY-MM-DD')
const nextWeek = dayjs().add(6, 'day').format('YYYY-MM-DD')
const dateRange = ref([
  localStorage.getItem('heatmap_start') || today,
  localStorage.getItem('heatmap_end') || nextWeek
])

const saveColor = () => {
  localStorage.setItem('heatmap_color', baseColor.value)
}

const limitMax15Days = (date) => {
  if (!dateRange.value || dateRange.value.length !== 2) return false
  const start = dayjs(dateRange.value[0])
  return dayjs(date).diff(start, 'day') > 29
}

const generateMockHeatmap = () => {
  const rows = 24
  const cols = 30
  const result = []
  for (let i = 0; i < rows; i++) {
    result.push(Array.from({ length: cols }, () => Math.floor(Math.random() * 301)))
  }
  return result
}

const electricResistorHeatmap = [
  ...Array(4).fill(Array(30).fill(0)),
  [0, 0, 0, 0, 255, 80, 80, 255, 255, 48, 48, 48, 48, 48, 255, 255, 255, 255, 80, 80, 0, 0, 0, 144, 144, 144, 144, 0, 0, 0], 
  [0, 0, 0, 0, 255, 80, 80, 48, 5, 5, 5, 5, 5, 5, 5, 5, 80, 80, 80, 80, 0, 0, 144, 144, 144, 144, 144, 144, 0, 0], 
  [0, 0, 0, 0, 80, 80, 5, 5, 5, 5, 5, 5, 48, 48, 5, 5, 5, 5, 80, 80, 0, 0, 144, 144, 0, 0, 144, 144, 0, 0], 
  [0, 0, 0, 0, 80, 5, 5, 5, 48, 48, 48, 48, 48, 48, 48, 5, 5, 5, 5, 80, 0, 0, 0, 0, 0, 144, 144, 144, 0, 0], 
  [0, 0, 0, 0, 5, 5, 48, 210, 210, 210, 210, 210, 210, 210, 210, 48, 48, 48, 5, 48, 0, 0, 0, 0, 144, 144, 144, 0, 0, 0], 
  [0, 0, 0, 0, 5, 48, 210, 48, 48, 48, 48, 48, 48, 48, 48, 48, 210, 48, 48, 5, 0, 0, 0, 0, 144, 144, 0, 0, 0, 0], 
  [0, 0, 0, 0, 48, 210, 48, 14, 48, 14, 14, 48, 48, 48, 14, 14, 68, 210, 48, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
  [0, 0, 0, 0, 210, 14, 14, 79, 14, 14, 14, 14, 48, 14, 14, 14, 14, 167, 210, 48, 0, 0, 0, 0, 144, 144, 0, 0, 0, 0], 
  [0, 0, 0, 0, 48, 14, 14, 28, 14, 14, 14, 48, 48, 14, 14, 14, 14, 167, 167, 210, 0, 0, 0, 0, 144, 144, 0, 0, 0, 0], 
  [0, 0, 0, 0, 48, 29, 79, 28, 48, 14, 29, 48, 28, 48, 14, 14, 29, 210, 210, 210, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
  [0, 0, 0, 0, 29, 79, 28, 136, 6, 29, 29, 6, 136, 28, 48, 29, 29, 48, 210, 210, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
  [0, 0, 0, 0, 48, 79, 6, 136, 6, 6, 6, 6, 136, 6, 48, 48, 68, 210, 48, 210, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
  [0, 0, 0, 0, 48, 79, 6, 136, 6, 6, 6, 6, 136, 6, 48, 48, 68, 48, 48, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
  [0, 0, 0, 0, 48, 79, 6, 6, 6, 6, 6, 6, 6, 6, 48, 48, 68, 48, 48, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
  [0, 0, 0, 0, 48, 79, 96, 6, 6, 6, 6, 6, 6, 28, 48, 48, 79, 119, 48, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
  [0, 0, 0, 0, 255, 48, 79, 96, 119, 119, 207, 207, 58, 48, 48, 109, 119, 96, 96, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
  ...Array(3).fill(Array(30).fill(0))
]

const loadHeatmap = async () => {
  const org = allOrgs.value.find(o => o.id === Number(selectedOrgId.value))
  if (!org) return
  localStorage.setItem('heatmap_selected_org', org.id)
  localStorage.setItem('heatmap_selected_org_name', org.name)

  if (false) {
    if (org.name === '电阻') {
      currentOrg.value = {
        id: org.id,
        name: org.name,
        members: org.members,
        heatmap: electricResistorHeatmap
      }
    } else {
      currentOrg.value = {
        id: org.id,
        name: org.name,
        members: org.members,
        heatmap: generateMockHeatmap()
      }
    }
  } else {
    try {
      const { data: heatmapRes } = await getOrgHeatmap(org.id, dateRange.value)
      currentOrg.value = {
        ...org,
        heatmap: heatmapRes.heatmap
      }
    } catch (err) {
      console.error('热力图获取失败', err)
    }
  }
}

onMounted(async () => {
  if (false) {
    allOrgs.value = [
      { id: 1, name: '开发组', members: 12 },
      { id: 2, name: '运营组', members: 8 },
      { id: 3, name: '电阻', members: 114514 }
    ]
    if (!selectedOrgName.value) selectedOrgName.value = '开发组'
    currentOrg.value = allOrgs.value.find(org => org.name == selectedOrgName.value)
    await loadHeatmap()
  } else {
    try {
      const { data: orgs } = await getUserOrgs()
      allOrgs.value = orgs
      const cachedId = localStorage.getItem('heatmap_selected_org')
      const cachedName = localStorage.getItem('heatmap_selected_org_name')
      const fallbackOrg = orgs.find(org => org.id == cachedId) || orgs[0]
      selectedOrgId.value = fallbackOrg?.id || null;
      selectedOrgName.value = fallbackOrg?.name || null;
      currentOrg.value = allOrgs.value.find(org => org.name == selectedOrgName.value) || fallbackOrg
      if (selectedOrgId.value) await loadHeatmap()
    } catch (err) {
      console.error('组织列表获取失败', err)
    }
  }
})
</script>

<style scoped>
.board-container {
  padding: 16px;
  background-color: var(--bg-color);
  color: var(--text-color);
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
  color: var(--text-color);
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.org-card {
  margin-bottom: 20px;
  background-color: var(--card-bg);
  border: 1px solid var(--input-border-color);  /* 统一边框颜色 */
}

.org-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.org-name {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-color);
}
</style>
