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
              :key="member.uid"
              :label="member.name"
              :value="member.uid"
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
              v-for="uid in form.members"
              :key="uid"
              :label="getMemberName(uid)"
              :value="uid"
              :disabled="form.keyMembers.length >= 5 && !form.keyMembers.includes(uid)"
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

        <el-form-item label="会议时段">
          <el-button @click="showHeatmap = true" type="primary">选择时间段</el-button>
          <span v-if="selectedTime">已选：{{ selectedTime }}</span>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleCreate">创建会议</el-button>
        </el-form-item>
      </el-form>

      <el-dialog v-model="showHeatmap" title="选择会议时段" width="90%">
        <div style="text-align:center">（此处显示成员二值热力图，支持点击选择时段）</div>
        <div class="heatmap-placeholder">MOCK HEATMAP INTERFACE                           还没做完
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
          失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した失敗した
        </div>
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
import {
  getOrgMembersApi,
  createMeetingApi
} from '@/api/meeting'
import { getUserOrgs } from '@/api/org'
import { ElMessage } from 'element-plus'

const organizations = ref([])
const members = ref([])
const selectedTime = ref('')
const showHeatmap = ref(false)

const form = reactive({
  organizationId: '',
  members: [],
  keyMembers: [],
  minAttendees: 1,
  duration: 60,
})

watch(() => form.members, (val) => {
  form.minAttendees = Math.max(1, Math.floor(val.length * 0.75))
}, { immediate: true })

onMounted(async () => {
  const res = await getUserOrgs()
  if (res.code === 1) organizations.value = res.data
})

const fetchMembers = async (orgId) => {
  const res = await getOrgMembersApi(orgId)
  if (res.code === 1) members.value = res.data
  form.members = []
  form.keyMembers = []
  form.minAttendees = 1
}

const getMemberName = (uid) => {
  const m = members.value.find(m => m.uid === uid)
  return m ? m.name : uid
}

const confirmHeatmap = () => {
  selectedTime.value = '04/30 10:00~11:00'
  showHeatmap.value = false
  form.duration = 60
}

const handleCreate = async () => {
  const res = await createMeetingApi({ ...form, time: selectedTime.value })
  if (res.code === 1) ElMessage.success('会议创建成功')
  else ElMessage.error(res.message || '创建失败')
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
