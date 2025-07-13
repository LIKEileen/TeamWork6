<template>
  <div class="create-meeting-container">
    <el-card class="create-meeting-card">
      <h2 class="title">创建会议</h2>

      <el-form label-width="100px" :model="form">
        <el-form-item label="选择组织">
          <el-select v-model="form.organizationId" placeholder="请选择组织" @change="fetchMembers">
            <el-option
              v-for="org in organizations"
              :key="org.id"
              :label="org.name"
              :value="org.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="参会成员">
          <el-select
            v-model="form.members"
            multiple
            filterable
            placeholder="请选择成员"
            :disabled="!form.organizationId"
          >
            <el-option
              v-for="member in members"
              :key="member.id"
              :label="member.name"
              :value="member.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="关键成员">
          <el-select
            v-model="form.keyMembers"
            multiple
            filterable
            placeholder="请选择关键成员"
            :disabled="!form.members.length"
          >
            <el-option
              v-for="id in form.members"
              :key="id"
              :label="getMemberName(id)"
              :value="id"
              :disabled="form.keyMembers.length >= 5 && !form.keyMembers.includes(id)"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="最低人数">
          <el-input-number
            v-model="form.minAttendees"
            :min="1"
            :max="Math.max(1, form.members.length)"
          />
        </el-form-item>

        <el-form-item label="会议标题">
          <el-input v-model="form.title" placeholder="请输入会议标题" />
        </el-form-item>

        <el-form-item label="会议描述">
          <el-input type="textarea" v-model="form.description" placeholder="可选，填写会议描述" />
        </el-form-item>

        <el-form-item label="会议地点">
          <el-input v-model="form.location" placeholder="可选，填写会议地点" />
        </el-form-item>

        <el-form-item label="会议时长 (分钟)">
          <el-input-number v-model="form.duration" :min="15" :max="480" />
        </el-form-item>

        <el-form-item label="选择时间范围">
          <el-date-picker v-model="dateRange" type="datetimerange" range-separator="至" start-placeholder="开始日期时间" end-placeholder="结束日期时间" format="YYYY-MM-DD HH:mm:ss" value-format="YYYY-MM-DD HH:mm:ss" @change="fillDateRange" />
        </el-form-item>

        <el-form-item label="会议开始时间">
          <el-input v-model="form.start_time" readonly />
        </el-form-item>

        <el-form-item label="会议结束时间">
          <el-input v-model="form.end_time" readonly />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="findAvailableTime">查找可用时间</el-button>
          <el-select v-if="availableTimes.length" v-model="selectedAvailableTime" placeholder="选择建议时间">
            <el-option v-for="item in availableTimes" :key="item.start_time" :label="formatTimeRange(item)" :value="item" />
          </el-select>
          <el-button type="primary" @click="handleCreate">创建会议</el-button>
        </el-form-item>

      </el-form>

      <el-dialog v-model="showAvailableTimes" title="可用会议时间">
        <el-table :data="availableTimes" style="width: 100%">
          <el-table-column prop="time" label="可用时间" />
        </el-table>
        <template #footer>
          <el-button @click="showAvailableTimes = false">关闭</el-button>
        </template>
      </el-dialog>
      <el-dialog v-model="showHeatmap" title="选择会议时段" width="90%">
        <heatmap-grid
          v-if="form.organizationId && form.members.length"
          :org-id="form.organizationId"
          :members="form.members"
          @select="handleTimeSelection"
        />
        <template #footer>
          <el-button @click="showHeatmap = false">取消</el-button>
          <el-button type="primary" @click="confirmHeatmap">确认</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>


<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { getOrgMembersApi, createMeetingApi, findAvailableMeetingTimeApi } from '@/api/meeting'
import { getUserOrgs, getOrgDetail } from '@/api/org'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import dayjs from 'dayjs'

const userStore = useUserStore()
const organizations = ref([])
const members = ref([])
const availableTimes = ref([])
const showAvailableTimes = ref(false)
const showHeatmap = ref(false)
const selectedAvailableTime = ref(null)
const dateRange = ref([])

const form = reactive({
  organizationId: '',
  members: [],
  keyMembers: [],
  minAttendees: 1,
  duration: 60,
  title: '',
  description: '',
  location: ''
})

watch(() => form.members, (val) => {
  form.minAttendees = Math.max(1, Math.floor(val.length * 0.75))
}, { immediate: true })

onMounted(async () => {
  const res = await getUserOrgs(userStore.token)
  // console.log(res.data.data)
  organizations.value = res.data.data
  // console.log(organizations.value)
})

const fetchMembers = async (orgId) => {
  const token = userStore.token
  const res = await getOrgDetail(token, orgId)
  console.log(res.data.data.members)
  if (res.data.code === 1) members.value = res.data.data.members
  console.log(members.value)
  form.members = []
  form.keyMembers = []
  form.minAttendees = 1
}

const openHeatmap = () => {
  if (!form.organizationId || form.members.length === 0) {
    ElMessage.warning('请先选择组织和成员')
    return
  }
  showHeatmap.value = true
}

const handleTimeSelection = (time) => {
  selectedTime.value = time
}

const confirmHeatmap = () => {
  if (!selectedTime.value) {
    ElMessage.warning('请在热力图中选择时间段')
    return
  }
  showHeatmap.value = false
}

const fillDateRange = () => {
  if (dateRange.value.length === 2) {
    form.start_time = dateRange.value[0]
    form.end_time = dateRange.value[1]
  }
}

const findAvailableTime = async () => {
  if (!dateRange.value.length) {
    ElMessage.warning('请先选择时间范围')
    return
  }
  const payload = {
    token: userStore.token,
    participant_ids: form.members.map(Number),
    duration: form.duration,
    start_date: dayjs(dateRange.value[0]).format('YYYY-MM-DD'),
    end_date: dayjs(dateRange.value[1]).format('YYYY-MM-DD'),
    key_participant_ids: form.keyMembers.map(Number)
  }
  const res = await findAvailableMeetingTimeApi(payload)
  console.log(res)
  if (res.data.code === 1) {
    availableTimes.value = []
    for (const [date, slots] of Object.entries(res.data.data.available_times)) {
      slots.forEach(slot => {
        availableTimes.value.push({
          date,
          start_time: slot.start_time,
          end_time: slot.end_time
        })
      })
    }
    ElMessage.success('获取可用时间成功')
  } else {
    ElMessage.error(res.message || '获取可用时间失败')
  }
}

watch(selectedAvailableTime, (val) => {
  if (val) {
    form.start_time = dayjs(val.start_time).format('YYYY-MM-DD HH:mm:ss')
    form.end_time = dayjs(val.end_time).format('YYYY-MM-DD HH:mm:ss')
  }
})

const getMemberName = (id) => {
  const m = members.value.find(m => m.id === id)
  return m ? m.name : id
}

// const confirmHeatmap = () => {
//   selectedTime.value = '04/30 10:00~11:00'
//   showHeatmap.value = false
//   form.duration = 60
// }

// const handleCreate = async () => {
//   const res = await createMeetingApi({ ...form, time: selectedTime.value })
//   if (res.code === 1) ElMessage.success('会议创建成功')
//   else ElMessage.error(res.message || '创建失败')
// }
const handleCreate = async () => {
  if (!form.start_time || !form.end_time) {
    ElMessage.warning('请先选择会议时间')
    return
  }
  const payload = {
    token: userStore.token,
    title: form.title,
    start_time: form.start_time,
    end_time: form.end_time,
    participant_ids: form.members.map(Number),
    description: form.description
  }
  const res = await createMeetingApi(payload)
  if (res.data.code === 1) {
    ElMessage.success('会议创建成功')
  } else {
    ElMessage.error(res.data.message || '会议创建失败')
  }
}

const formatTimeRange = (item) => {
  return `${dayjs(item.start_time).format('YYYY-MM-DD HH:mm')} ~ ${dayjs(item.end_time).format('HH:mm')}`
}
</script>

<style scoped>
.create-meeting-container {
  padding: 16px;
}
.create-meeting-card {
  background-color: var(--card-bg);
  border: 1px solid var(--input-border-color);
}
.title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 20px;
  color: var(--text-color);
}
.heatmap-placeholder {
  height: 360px;
  background: repeating-linear-gradient(45deg, #eee, #eee 10px, #ccc 10px, #ccc 20px);
  margin-top: 16px;
  border-radius: 6px;
}
</style>
