<template>
  <div class="schedule-container">
    <el-card class="schedule-card">
      <div class="header-row">
        <h2 class="page-title">我的日程</h2>
        <div class="controls">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            size="small"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            :disabled-date="limitMax30Days"
            @change="saveDateRange"
          />
          <el-color-picker
            v-model="baseColor"
            :predefine="presetColors"
            size="small"
            @change="saveColor"
          />
          <el-button size="small" type="primary" @click="showAddEvent = true">添加事件</el-button>
          <el-button size="small" @click="showImportExcel = true">导入Excel</el-button>
          <el-button size="small" @click="showImportSchool = true">学校课表导入</el-button>
          <el-button size="small" @click="showAddRecurring = true">添加长期事件</el-button>
        </div>
      </div>

      <div class="heatmap-wrapper">
        <div class="heatmap-grid" :style="gridColumnStyle">
          <div class="heatmap-header" :style="gridColumnStyle">
            <div class="heatmap-cell time-label"></div>
            <div class="heatmap-cell header" v-for="day in dateLabels" :key="day.date">
              <div>{{ day.date }}</div>
              <div>{{ day.weekday }}</div>
            </div>
          </div>
          <div class="heatmap-body">
            <div class="heatmap-row" v-for="(time, rowIndex) in timeLabels" :key="time" :style="gridColumnStyle">
              <div class="heatmap-cell time-label">{{ time }}</div>
              <div
                class="heatmap-cell"
                v-for="(day, colIndex) in dateLabels"
                :key="day.date + '-' + time"
              >
                <div
                  v-for="evt in getEventsAt(day.date, time)"
                  :key="evt.id"
                  class="event-block"
                  :style="getEventStyle(evt)"
                  @contextmenu.prevent="openContextMenu($event, evt)"
                  @mouseenter="showTooltip(evt, $event)"
                  @mouseleave="hideTooltip"
                >
                  <div class="event-content">{{ evt.title }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div
          v-if="hoverTooltip.visible"
          class="hover-tooltip"
          :style="{ top: hoverTooltip.y + 'px', left: hoverTooltip.x + 'px' }"
        >
          <div>{{ hoverTooltip.title }}</div>
          <div>{{ hoverTooltip.time }}</div>
        </div>
      </div>

      <!-- 弹窗：添加事件 -->
      <el-dialog v-model="showAddEvent" title="添加事件" :close-on-click-modal="false" @close="resetAddEvent">
        <el-form>
          <el-form-item label="事件名称">
            <el-input v-model="addEventForm.title" />
          </el-form-item>
          <el-form-item label="选择日期">
            <el-date-picker v-model="addEventForm.date" type="date" placeholder="选择日期" />
          </el-form-item>
          <el-form-item label="开始时间">
            <el-time-picker v-model="addEventForm.start" placeholder="选择开始时间" />
          </el-form-item>
          <el-form-item label="结束时间">
            <el-time-picker v-model="addEventForm.end" placeholder="选择结束时间" />
          </el-form-item>
          <el-form-item label="颜色">
            <el-color-picker v-model="addEventForm.color" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showAddEvent = false">取消</el-button>
          <el-button type="primary" @click="confirmAddEvent">确定</el-button>
        </template>
      </el-dialog>

      <!-- 弹窗：导入Excel -->
      <el-dialog v-model="showImportExcel" title="导入Excel" :close-on-click-modal="false">
        <el-upload drag>
          <i class="el-icon-upload"></i>
          <div class="el-upload__text">拖拽文件到此或点击上传</div>
        </el-upload>
        <template #footer>
          <el-button @click="showImportExcel = false">取消</el-button>
          <el-button type="primary" @click="confirmImportExcel">确定</el-button>
        </template>
      </el-dialog>

      <!-- 弹窗：学校课表导入 -->
      <el-dialog v-model="showImportSchool" title="学校课表导入" :close-on-click-modal="false">
        <el-select v-model="importSchoolName" placeholder="请选择...">
          <el-option label="清华大学" value="清华大学" />
          <el-option label="北京大学" value="北京大学" />
          <el-option label="复旦大学" value="复旦大学" />
        </el-select>
        <template #footer>
          <el-button @click="showImportSchool = false">取消</el-button>
          <el-button type="primary" @click="confirmImportSchool">确定</el-button>
        </template>
      </el-dialog>

      <!-- 弹窗：添加长期事件 -->
      <el-dialog v-model="showAddRecurring" title="添加长期事件" :close-on-click-modal="false">
        <el-form>
          <el-form-item label="事件名称">
            <el-input v-model="addRecurringForm.title" />
          </el-form-item>
          <el-form-item label="开始时间">
            <el-time-picker v-model="addRecurringForm.start" placeholder="选择开始时间" />
          </el-form-item>
          <el-form-item label="结束时间">
            <el-time-picker v-model="addRecurringForm.end" placeholder="选择结束时间" />
          </el-form-item>
          <el-form-item label="频次">
            <el-select v-model="addRecurringForm.frequency">
              <el-option label="每天" value="daily" />
              <el-option label="每周" value="weekly" />
              <el-option label="每月" value="monthly" />
              <el-option label="自定义" value="custom" />
            </el-select>
          </el-form-item>
          <el-form-item v-if="addRecurringForm.frequency === 'custom'" label="自定义日期">
            <el-date-picker v-model="addRecurringForm.customDates" type="dates" placeholder="选择多个日期" />
          </el-form-item>
          <el-form-item label="颜色">
            <el-color-picker v-model="addRecurringForm.color" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showAddRecurring = false">取消</el-button>
          <el-button type="primary" @click="confirmAddRecurring">确定</el-button>
        </template>
      </el-dialog>
      <el-dialog v-model="showEditEvent" title="编辑事件" :close-on-click-modal="false" @close="resetEditEvent">
        <el-form>
          <el-form-item label="事件名称">
            <el-input v-model="editEventForm.title" />
          </el-form-item>
          <el-form-item label="选择日期">
            <el-date-picker v-model="editEventForm.date" type="date" placeholder="选择日期" />
          </el-form-item>
          <el-form-item label="开始时间">
            <el-time-picker v-model="editEventForm.start" placeholder="选择开始时间" />
          </el-form-item>
          <el-form-item label="结束时间">
            <el-time-picker v-model="editEventForm.end" placeholder="选择结束时间" />
          </el-form-item>
          <el-form-item label="颜色">
            <el-color-picker v-model="editEventForm.color" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showEditEvent = false">取消</el-button>
          <el-button type="primary" @click="confirmEditEvent">确定</el-button>
        </template>
      </el-dialog>

      <!-- 弹窗：删除事件 -->
      <el-dialog v-model="showDeleteEvent" title="删除事件" :close-on-click-modal="false">
        <div style="color: red; font-weight: bold; margin-bottom: 20px;">
          您确定要删除事件 "{{ deleteEventForm.title }}" 吗？
        </div>
        <template #footer>
          <el-button @click="showDeleteEvent = false">取消</el-button>
          <el-button type="primary" @click="confirmDeleteEvent">确定</el-button>
        </template>
      </el-dialog>

      <el-dropdown
        v-if="contextMenuVisible"
        ref="contextDropdown"
        :style="contextMenuStyle"
        trigger="manual"
        @command="handleMenuCommand"
      >
        <span></span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="edit">编辑</el-dropdown-item>
            <el-dropdown-item command="delete">删除</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </el-card>
  </div>
  
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import dayjs from 'dayjs'
import {
  getUserScheduleApi,
  addEventApi,
  editEventApi,
  deleteEventApi,
  importScheduleExcelApi,
  importScheduleSchoolApi,
  addRecurringEventApi
} from '@/api/user.js'

onMounted(async () => {
  try {
    const res = await getUserScheduleApi()
    events.value = res.data || []
  } catch (e) {
    console.error('获取日程失败：', e)
  }
})

const baseColor = ref(localStorage.getItem('schedule_color') || '#409EFF')
const presetColors = ['#409EFF', '#67C23A', '#F56C6C', '#E6A23C']

const today = dayjs().format('YYYY-MM-DD')
const nextWeek = dayjs().add(6, 'day').format('YYYY-MM-DD')
const dateRange = ref([
  localStorage.getItem('schedule_start') || today,
  localStorage.getItem('schedule_end') || nextWeek
])

const weekDaysMap = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

const showAddEvent = ref(false)
const showEditEvent = ref(false)
const showDeleteEvent = ref(false)
const showImportExcel = ref(false)
const showImportSchool = ref(false)
const showAddRecurring = ref(false)

const addEventForm = ref({ title: '', date: '', start: '', end: '', color: '' })
const editEventForm = ref({ id: '', title: '', date: '', start: '', end: '', color: '' })
const deleteEventForm = ref({ id: '', title: '' })
const addRecurringForm = ref({ title: '', start: '', end: '', frequency: '', customDates: [], color: '' })
const importSchoolName = ref('')
const events = ref([])

const contextDropdown = ref(null)

const confirmAddEvent = async () => {
  try {
    const payload = {
      ...addEventForm.value,
      start: dayjs(addEventForm.value.start).format('HH:mm'),
      end: dayjs(addEventForm.value.end).format('HH:mm')
    }
    await addEventApi(payload)
    events.value.push({ id: Date.now(), ...payload, day: payload.date })
    showAddEvent.value = false
    addEventForm.value = { title: '', date: '', start: '', end: '', color: '' }
  } catch (e) {
    console.error('添加事件失败：', e)
  }
}

const confirmEditEvent = async () => {
  try {
    const payload = {
      id: editEventForm.value.id,
      title: editEventForm.value.title,
      date: editEventForm.value.date,
      start: dayjs(editEventForm.value.start).format('HH:mm'),
      end: dayjs(editEventForm.value.end).format('HH:mm'),
      color: editEventForm.value.color
    }
    await editEventApi(payload)
    events.value = events.value.map(evt => evt.id === payload.id ? { ...evt, ...payload, day: payload.date } : evt)
    showEditEvent.value = false
    editEventForm.value = { id: '', title: '', date: '', start: '', end: '', color: '' }
  } catch (e) {
    console.error('编辑事件失败：', e)
  }
}

const confirmDeleteEvent = async () => {
  try {
    await deleteEventApi({ id: deleteEventForm.value.id })
    events.value = events.value.filter(evt => evt.id !== deleteEventForm.value.id)
    showDeleteEvent.value = false
    deleteEventForm.value = { id: '', title: '' }
  } catch (e) {
    console.error('删除事件失败：', e)
  }
}

const confirmImportExcel = async () => {
  try {
    await importScheduleExcelApi()
    showImportExcel.value = false
  } catch (e) {
    console.error('导入 Excel 失败：', e)
  }
}

const confirmImportSchool = async () => {
  try {
    await importScheduleSchoolApi({ school: importSchoolName.value })
    showImportSchool.value = false
    importSchoolName.value = ''
  } catch (e) {
    console.error('学校导入失败：', e)
  }
}

const confirmAddRecurring = async () => {
  try {
    await addRecurringEventApi({ ...addRecurringForm.value })
    showAddRecurring.value = false
    addRecurringForm.value = { title: '', start: '', end: '', frequency: '', customDates: [], color: '' }
  } catch (e) {
    console.error('添加长期事件失败：', e)
  }
}

const resetAddEvent = () => {
  addEventForm.value = { title: '', date: '', start: '', end: '', color: '' }
}

const saveColor = () => {
  localStorage.setItem('schedule_color', baseColor.value)
}

const saveDateRange = () => {
  localStorage.setItem('schedule_start', dateRange.value[0])
  localStorage.setItem('schedule_end', dateRange.value[1])
}

const limitMax30Days = (date) => {
  const start = dayjs(dateRange.value[0])
  const target = dayjs(date)
  return target.diff(start, 'day') > 29
}

const timeLabels = Array.from({ length: 24 }, (_, i) => {
  const hour = Math.floor(i / 2) + 8
  const minute = i % 2 === 0 ? '00' : '30'
  return `${hour.toString().padStart(2, '0')}:${minute}`
})

const dateLabels = computed(() => {
  const start = dayjs(dateRange.value[0])
  const end = dayjs(dateRange.value[1])
  const days = Math.min(end.diff(start, 'day') + 1, 30)
  return Array.from({ length: days }, (_, i) => {
    const d = start.add(i, 'day')
    return { date: d.format('MM/DD'), weekday: weekDaysMap[d.day()] }
  })
})

const gridColumnStyle = computed(() => {
  return {
    gridTemplateColumns: `100px repeat(${dateLabels.value.length}, 1fr)`
  }
})

const getEventsAt = (dayLabel, time) => {
  const fullDate = dateRangeToFull(dayLabel)
  return events.value.filter(evt => evt.day === fullDate && evt.start === time)
}

const dateRangeToFull = (shortDate) => {
  const start = dayjs(dateRange.value[0])
  const target = start.add(dateLabels.value.findIndex(d => d.date === shortDate), 'day')
  return target.format('YYYY-MM-DD')
}

const getEventStyle = (evt) => {  // 不用管这个报错
  const [sh, sm] = evt.start.split(':').map(Number)
  const [eh, em] = evt.end.split(':').map(Number)
  const slots = (eh * 60 + em - (sh * 60 + sm)) / 30
  return {
    height: `${slots * 40 - 6}px`,
    backgroundColor: evt.color || baseColor.value,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    textAlign: 'center'
  }
}

const hoverTooltip = ref({ visible: false, title: '', time: '', x: 0, y: 0 })

const showTooltip = (evt, e) => {
  hoverTooltip.value = {
    visible: true,
    title: evt.title,
    time: `${evt.day} ${evt.start}~${evt.end}`,
    x: e.clientX + 12,
    y: e.clientY + 12
  }
}

const hideTooltip = () => {
  hoverTooltip.value.visible = false
}

const contextMenuVisible = ref(false)
const contextMenuStyle = ref({})
const contextMenuEvent = ref(null)

const openContextMenu = async (event, evtData) => {
  event.preventDefault()
  contextMenuVisible.value = true
  contextMenuStyle.value = {
    position: 'fixed',
    top: `${event.clientY}px`,
    left: `${event.clientX}px`
  }
  contextMenuEvent.value = evtData

  await nextTick()  // 等待 DOM 渲染
  contextDropdown.value?.handleOpen()  // ✅ 手动打开 dropdown
}

const handleMenuCommand = (command) => {
  if (!contextMenuEvent.value) return
  if (command === 'edit') {
    editEventForm.value = {
      ...contextMenuEvent.value,
      start: dayjs(`2023-01-01 ${contextMenuEvent.value.start}`).toDate(),
      end: dayjs(`2023-01-01 ${contextMenuEvent.value.end}`).toDate()
    }
    showEditEvent.value = true
  } else if (command === 'delete') {
    deleteEventForm.value = {
      id: contextMenuEvent.value.id,
      title: contextMenuEvent.value.title
    }
    showDeleteEvent.value = true
  }
  contextMenuVisible.value = false
}

</script>

<style scoped>
.schedule-container {
  padding: 16px;
}

.schedule-card {
  background-color: var(--card-bg);
  border: 1px solid var(--input-border-color);  /* 统一边框颜色 */
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
  color: var(--text-color);
}

.controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.heatmap-wrapper {
  overflow-x: auto;
}

.heatmap-grid {
  min-width: 700px;
}

.heatmap-header {
  display: grid;
  grid-template-columns: 100px repeat(auto-fit, minmax(80px, 1fr));
  margin-bottom: 6px;
}

.heatmap-body {
  display: grid;
  grid-template-rows: repeat(24, 1fr);
  gap: 1px;
}

.heatmap-row {
  display: grid;
  grid-template-columns: 100px repeat(auto-fit, minmax(80px, 1fr));
  gap: 1px;
}

.heatmap-cell {
  height: 40px;
  background-color: var(--input-bg);
  border-radius: 2px;
  position: relative;
}

.time-label {
  font-weight: bold;
  text-align: center;
  font-size: 12px;
  color: var(--text-color);
  background-color: var(--input-bg);
}

.header {
  font-weight: bold;
  text-align: center;
  font-size: 12px;
  background-color: var(--input-bg);
  color: var(--text-color);
}

.event-block {
  background-color: #409EFF;
  color: #fff;
  font-size: 12px;
  padding: 2px 5px;
  border-radius: 6px;
  position: absolute;
  left: 2px;
  right: 2px;
  top: 4px;
  z-index: 10;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
}

.event-content {
  width: 100%;
  text-align: center;
  word-break: break-word; /* 超过宽度自动换行 */
  white-space: normal;    /* 允许正常换行，不强制一行 */
  padding: 0 2px;         /* 加一点点内边距防止贴边 */
  font-size: 12px;
  line-height: 1.2;
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
  padding: 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  margin-top: 4px;
  white-space: nowrap;
  z-index: 99;
}

.event-block:hover .tooltip {
  display: block;
}

.hover-tooltip {
  position: fixed;
  background-color: var(--input-bg);
  color: var(--text-color);
  padding: 6px 10px;
  font-size: 12px;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  z-index: 9999;
  white-space: nowrap;
  pointer-events: none;
}
</style>
