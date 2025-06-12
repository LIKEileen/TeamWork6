<template>
  <div class="heatmap-wrapper">
    <!-- 顶部日期行 -->
    <div class="heatmap-header" :style="{ gridTemplateColumns: gridTemplate }">
      <div class="time-label header-cell"></div>
      <div
        class="header-cell"
        v-for="(date, index) in dateLabels"
        :key="index"
      >{{ date }}</div>
    </div>

    <!-- 网格部分 -->
    <div class="heatmap-body">
      <div
        class="heatmap-row"
        v-for="rowIndex in 24"
        :key="rowIndex - 1"
        :style="{ gridTemplateColumns: gridTemplate }"
      >
        <div class="time-label">{{ timeLabels[rowIndex - 1] }}</div>
        <div
          v-for="colIndex in dateLabels.length"
          :key="colIndex - 1"
          class="heatmap-cell"
          :style="{ backgroundColor: getColor((data?.[rowIndex - 1]?.[colIndex - 1]) ?? 0) }"
        >
          <div class="cell-content">
            <span
              class="value"
              v-if="hoveredCell.row === rowIndex - 1 && hoveredCell.col === colIndex - 1"
            >
              {{ data[rowIndex - 1]?.[colIndex - 1] || 0 }}
            </span>
            <div class="tooltip">
              <div>
                {{ dateLabels[colIndex - 1] }} {{ timeLabels[rowIndex - 1] }}~{{
                  timeLabels[rowIndex] || '20:00'
                }}
              </div>
              <div>忙碌人数：{{ getCellValue(rowIndex - 1, colIndex - 1) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watchEffect, watch } from 'vue'
import dayjs from 'dayjs'

const props = defineProps({
  data: Array,
  color: { type: String, default: '#ff4d4f' },
  startDate: String,
  endDate: String
})

const hoveredCell = ref({ row: null, col: null })

const defaultStart = dayjs().format('YYYY-MM-DD')
const defaultEnd = dayjs().add(6, 'day').format('YYYY-MM-DD')

const actualStartDate = ref(props.startDate || localStorage.getItem('heatmap_start') || defaultStart)
const actualEndDate = ref(props.endDate || localStorage.getItem('heatmap_end') || defaultEnd)

watch([actualStartDate, actualEndDate], () => {
  if (actualStartDate.value && actualEndDate.value) {
    localStorage.setItem('heatmap_start', actualStartDate.value)
    localStorage.setItem('heatmap_end', actualEndDate.value)
  }
})

watchEffect(() => {
  if (props.startDate) actualStartDate.value = props.startDate
  if (props.endDate) actualEndDate.value = props.endDate
})

const maxValue = computed(() => {
  if (!Array.isArray(props.data) || props.data.length === 0) return 1
  return Math.max(...props.data.flat()) || 1
})

const getColor = (value) => {
  const intensity = Math.min(value / maxValue.value, 1)
  const [r, g, b] = hexToRgb(props.color)
  const alpha = 0.2 + intensity * 0.6
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

const getCellValue = (row, col) => {
  if (!Array.isArray(props.data)) return 0
  const rowData = props.data[row] || []
  return rowData[col] ?? 0
}

const hexToRgb = (hex) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result
    ? [
        parseInt(result[1], 16),
        parseInt(result[2], 16),
        parseInt(result[3], 16)
      ]
    : [255, 77, 79]
}

const timeLabels = Array.from({ length: 24 }, (_, i) => {
  const hour = Math.floor(i / 2) + 8
  const minute = i % 2 === 0 ? '00' : '30'
  return `${hour.toString().padStart(2, '0')}:${minute}`
})

const dateLabels = computed(() => {
  const start = dayjs(actualStartDate.value)
  const end = dayjs(actualEndDate.value)
  const maxDays = 30
  const days = Math.min(end.diff(start, 'day') + 1, maxDays)
  return Array.from({ length: days }, (_, i) =>
    start.add(i, 'day').format('MM/DD')
  )
})

const gridTemplate = computed(() => {
  return `60px repeat(${dateLabels.value.length}, minmax(40px, 1fr))`
})
</script>


<style scoped>
.heatmap-wrapper {
  width: 100%;
  overflow-x: auto;
  background-color: var(--card-bg);
  color: var(--text-color);
  border-radius: 6px;
  padding: 8px 12px;
  box-sizing: border-box;
}

.heatmap-header {
  display: grid;
  gap: 2px;
  margin-bottom: 6px;
  font-size: 12px;
  font-weight: bold;
  color: var(--text-color);
  text-align: center;
}

.header-cell {
  background-color: var(--input-bg);
  padding: 4px 0;
  border-radius: 4px;
}

.heatmap-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.heatmap-row {
  display: grid;
  gap: 2px;
}

.time-label {
  font-size: 12px;
  color: var(--text-color);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 4px;
}

.heatmap-cell {
  height: 28px;
  background-color: #f0f0f0;
  border-radius: 2px;
  transition: all 0.3s ease;
  position: relative;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 13px;
  color: var(--text-color);
}

.cell-content {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.value {
  display: none;
}

.heatmap-cell:hover .value {
  display: inline;
}

.tooltip {
  display: none;
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: var(--input-bg);
  color: var(--text-color);
  border-radius: 4px;
  font-size: 12px;
  padding: 4px 6px;
  white-space: nowrap;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  margin-top: 2px;
  line-height: 1.4;
  text-align: left;
  z-index: 1;
}

.heatmap-cell:hover .tooltip {
  display: block;
}
</style>
