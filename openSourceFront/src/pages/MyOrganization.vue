<template>
  <div class="org-container">
    <el-card class="org-card">
      <div class="header-row">
        <h2 class="page-title">我的组织</h2>
        <div class="header-actions">
          <!-- 添加收到的邀请通知按钮 -->
          <el-badge :value="pendingInvitations.length" :hidden="pendingInvitations.length === 0" class="invitation-badge">
            <el-button type="info" size="small" @click="showInvitationModal = true">
              <el-icon><Message /></el-icon> 邀请通知
            </el-button>
          </el-badge>
          <el-button type="success" size="small" @click="showJoinOrgModal = true">
            <el-icon><Link /></el-icon> 申请加入
          </el-button>
          <el-button type="primary" size="small" @click="showCreateModal = true">
            <el-icon><Plus /></el-icon> 创建组织
          </el-button>
        </div>
      </div>

      <!-- 组织列表 -->
      <div class="org-list-container">
        <el-collapse v-model="expandedOrgId">
          <el-collapse-item v-for="org in organizations" :key="org.id" :name="org.id">
            <template #title>
              <div class="org-title" @contextmenu.prevent="openContextMenu($event, org)">
                {{ org.name }}
                <div class="org-members-count">{{ org.members.length }}人</div>
              </div>
            </template>
            <div class="org-content">
              <div class="org-actions">
                <el-button type="primary" size="small" plain @click="openRenameDialog(org)">
                  <el-icon><EditPen /></el-icon> 修改组织名称
                </el-button>
                <el-button type="warning" size="small" plain @click="setAdmins(org)">
                  <el-icon><UserFilled /></el-icon> 设置管理员
                </el-button>
                <el-button type="success" size="small" plain @click="addMember(org)">
                  <el-icon><Plus /></el-icon> 添加成员
                </el-button>
                <el-button type="danger" size="small" plain @click="confirmDelete(org)">
                  <el-icon><Delete /></el-icon> 删除组织
                </el-button>
              </div>
              <el-divider content-position="left">成员列表</el-divider>
              <div class="members-list">
                <div v-for="member in org.members" :key="member.id" class="member-item">
                  <el-avatar :size="32" :src="member.avatarUrl || defaultAvatar"></el-avatar>
                  <div class="member-info">
                    <div class="member-name">
                      <span v-if="member.role === 'creator'" class="role-badge creator">创建者</span>
                      <span v-else-if="member.role === 'admin'" class="role-badge admin">管理员</span>
                      {{ member.name }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>

    <!-- 右键菜单 -->
    <el-dropdown
      v-if="contextMenu.visible"
      ref="contextDropdown"
      :style="contextMenuStyle"
      trigger="manual"
      @command="handleContextMenuCommand"
    >
      <span></span>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="rename">✏️ 修改组织名称</el-dropdown-item>
          <el-dropdown-item command="delete">🗑️ 删除组织</el-dropdown-item>
          <el-dropdown-item command="setAdmins">👥 设置管理员</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <!-- 设置管理员弹窗 -->
    <el-dialog v-model="showAdminModal" title="设置管理员（最多 5 人）" width="400px">
      <div class="admin-list">
        <div v-for="member in currentOrg?.members" :key="member.id" class="admin-item">
          <!-- 修复这里：使用单独的布尔变量而不是数组来控制每个成员的管理员状态 -->
          <el-checkbox 
            v-if="member.role !== 'creator'" 
            v-model="adminStatusMap[member.id]"
            :disabled="countAdmins() >= 5 && !adminStatusMap[member.id]"
            @change="updateAdminStatus"
          >
            <div class="admin-name">
              <el-avatar :size="24" :src="member.avatarUrl || defaultAvatar"></el-avatar>
              {{ member.name }}
            </div>
          </el-checkbox>
          <div v-else class="creator-item">
            <el-avatar :size="24" :src="member.avatarUrl || defaultAvatar"></el-avatar>
            {{ member.name }}
            <el-tag size="small" type="danger">创建者</el-tag>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAdminModal = false">取消</el-button>
          <el-button type="primary" @click="saveAdmins">确认</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 创建组织弹窗 -->
    <el-dialog v-model="showCreateModal" title="创建新组织" width="500px">
      <el-form :model="newOrgForm" ref="createFormRef" :rules="orgRules">
        <el-form-item label="组织名称" prop="name">
          <el-input v-model="newOrgForm.name" placeholder="请输入组织名称"></el-input>
        </el-form-item>
        
        <!-- 添加成员搜索部分 -->
        <el-divider content-position="left">邀请成员（可选）</el-divider>
        
        <el-form-item label="搜索成员">
          <el-input 
            v-model="newOrgForm.searchText" 
            placeholder="输入用户ID或用户名"
            @keyup.enter="searchUserForNewOrg"
          >
            <template #append>
              <el-button @click="searchUserForNewOrg">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        
        <!-- 搜索结果 -->
        <div v-if="newOrgSearchResults.length > 0" class="search-results">
          <h4>搜索结果</h4>
          <div v-for="user in newOrgSearchResults" :key="user.id" class="search-result-item">
            <el-checkbox v-model="user.selected" @change="() => updateSelectedUsersCount()">
              <div class="search-user-item">
                <el-avatar :size="28" :src="user.avatarUrl || defaultAvatar"></el-avatar>
                <div class="user-info">
                  <div class="user-name">{{ user.name }}</div>
                  <div class="user-id">ID: {{ user.id }}</div>
                </div>
              </div>
            </el-checkbox>
          </div>
        </div>
        
        <!-- 没有搜索结果 -->
        <div v-else-if="newOrgSearchAttempted" class="no-results">
          <el-empty description="未找到用户" :image-size="60"></el-empty>
        </div>
        
        <!-- 已选成员摘要 -->
        <div v-if="getSelectedUsers().length > 0" class="selected-users-summary">
          <div class="selected-users-label">已选择 {{ getSelectedUsers().length }} 位成员</div>
          <div class="selected-users-tags">
            <el-tag 
              v-for="user in getSelectedUsers()" 
              :key="user.id"
              size="small"
              closable
              @close="unselectUser(user.id)"
            >
              {{ user.name }}
            </el-tag>
          </div>
        </div>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelCreateOrg">取消</el-button>
          <el-button type="primary" @click="submitNewOrg">
            创建组织{{ getSelectedUsers().length > 0 ? ` (+ ${getSelectedUsers().length} 名成员)` : '' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 重命名弹窗 -->
    <el-dialog v-model="showRenameModal" title="修改组织名称" width="400px">
      <el-form :model="renameForm" ref="renameFormRef" :rules="orgRules">
        <el-form-item label="组织名称" prop="name">
          <el-input v-model="renameForm.name" placeholder="请输入新的组织名称"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showRenameModal = false">取消</el-button>
          <el-button type="primary" @click="confirmRename">确认</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 新增：添加成员弹窗 -->
    <el-dialog v-model="showAddMemberModal" title="添加成员" width="400px">
      <el-form :model="addMemberForm">
        <el-form-item label="查找用户">
          <el-input 
            v-model="addMemberForm.searchText" 
            placeholder="输入用户ID或用户名"
            @keyup.enter="searchUser"
          >
            <template #append>
              <el-button @click="searchUser">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
        </el-form-item>

        <div class="search-results" v-if="searchResults.length > 0">
          <h4>搜索结果</h4>
          <div v-for="user in searchResults" :key="user.id" class="search-result-item">
            <el-avatar :size="32" :src="user.avatarUrl || defaultAvatar"></el-avatar>
            <div class="user-info">
              <div class="user-name">{{ user.name }}</div>
              <div class="user-id">ID: {{ user.id }}</div>
            </div>
            <el-button 
              size="small" 
              type="primary" 
              :disabled="isUserInOrg(user.id)"
              @click="inviteUser(user)"
            >
              {{ isUserInOrg(user.id) ? '已是成员' : '邀请' }}
            </el-button>
          </div>
        </div>

        <div class="no-results" v-else-if="searchAttempted">
          <el-empty description="未找到用户"></el-empty>
        </div>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddMemberModal = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 确认邀请弹窗 -->
    <el-dialog v-model="showInviteConfirmModal" title="发送邀请" width="360px">
      <p>确定邀请 <strong>{{ pendingInvite?.name }}</strong> 加入到组织 <strong>{{ currentOrg?.name }}</strong> 吗？</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showInviteConfirmModal = false">取消</el-button>
          <el-button type="primary" @click="confirmInvite">确定邀请</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 新增：申请加入组织弹窗 -->
    <el-dialog v-model="showJoinOrgModal" title="申请加入组织" width="400px">
      <el-form :model="joinOrgForm" ref="joinOrgFormRef" :rules="joinOrgRules">
        <el-form-item label="组织ID" prop="orgId">
          <el-input 
            v-model="joinOrgForm.orgId" 
            placeholder="请输入组织ID"
            @keyup.enter="searchOrg"
          >
            <template #append>
              <el-button @click="searchOrg">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        
        <!-- 搜索结果展示 -->
        <div v-if="orgSearchResult" class="org-search-result">
          <div class="org-info">
            <h4>{{ orgSearchResult.name }}</h4>
            <div class="org-details">
              <span>ID: {{ orgSearchResult.id }}</span>
              <span>{{ orgSearchResult.members.length }}人</span>
              <span>创建者: {{ getCreatorName(orgSearchResult) }}</span>
            </div>
            <div class="join-message" v-if="isUserInSearchOrg">
              <el-alert type="info" :closable="false" show-icon>您已是该组织成员</el-alert>
            </div>
            <el-input
              v-if="!isUserInSearchOrg"
              v-model="joinOrgForm.message"
              type="textarea"
              placeholder="申请加入理由（选填）"
              rows="2"
              maxlength="200"
              show-word-limit
            ></el-input>
          </div>
        </div>

        <div v-else-if="orgSearchAttempted" class="no-org-result">
          <el-empty description="未找到该组织" :image-size="80"></el-empty>
        </div>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showJoinOrgModal = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitJoinRequest"
            :disabled="!orgSearchResult || isUserInSearchOrg"
          >
            提交申请
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 新增：收到的组织邀请弹窗 -->
    <el-dialog v-model="showInvitationModal" title="收到的组织邀请" width="500px">
      <div v-if="pendingInvitations.length > 0" class="invitation-list">
        <div v-for="invitation in pendingInvitations" :key="invitation.id" class="invitation-item">
          <div class="invitation-content">
            <h4 class="invitation-title">{{ invitation.orgName }}</h4>
            <div class="invitation-info">
              <span>组织ID: {{ invitation.orgId }}</span>
              <span>邀请人: {{ invitation.inviter }}</span>
              <span>邀请时间: {{ formatDate(invitation.inviteTime) }}</span>
            </div>
            <div class="invitation-message" v-if="invitation.message">
              <el-text type="info">留言: {{ invitation.message }}</el-text>
            </div>
          </div>
          <div class="invitation-actions">
            <el-button 
              type="success" 
              size="small" 
              @click="acceptInvitation(invitation)"
              :loading="invitation.processing"
            >接受</el-button>
            <el-button 
              type="danger" 
              size="small" 
              plain
              @click="rejectInvitation(invitation)"
              :loading="invitation.processing"
            >拒绝</el-button>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无邀请" :image-size="100"></el-empty>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showInvitationModal = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { EditPen, Delete, UserFilled, Plus, Search, Link, Message } from '@element-plus/icons-vue'
import defaultAvatarImg from '@/assets/default_icon.jpg'

const expandedOrgId = ref([])
const defaultAvatar = defaultAvatarImg // 直接使用导入的图片，不需要再用ref包装
const showAdminModal = ref(false)
const showCreateModal = ref(false)
const showRenameModal = ref(false)
const tempAdminIds = ref([])
const currentOrg = ref(null)
const contextMenu = ref({ visible: false })
const contextDropdown = ref(null)
const contextMenuStyle = ref({})
const renameForm = ref({ name: '', id: '' })
const newOrgForm = ref({
  name: '',
  searchText: '' // 直接在初始声明中添加 searchText 字段
})
const createFormRef = ref(null)
const renameFormRef = ref(null)

const organizations = ref([
  {
    id: 'org1',
    name: '数据科学研究组',
    members: [
      { id: 'u1', name: '张教授', role: 'creator', avatarUrl: null },
      { id: 'u2', name: '李研究员', role: 'admin', avatarUrl: null },
      { id: 'u3', name: '王博士', role: 'admin', avatarUrl: null },
      { id: 'u4', name: '陈同学', role: '', avatarUrl: null },
      { id: 'u5', name: '林同学', role: '', avatarUrl: null }
    ]
  },
  {
    id: 'org2',
    name: '软件开发小组',
    members: [
      { id: 'u6', name: '刘组长', role: 'creator', avatarUrl: null },
      { id: 'u7', name: '杨开发', role: 'admin', avatarUrl: null },
      { id: 'u8', name: '吴测试', role: '', avatarUrl: null },
      { id: 'u9', name: '赵设计', role: '', avatarUrl: null }
    ]
  },
  {
    id: 'org3',
    name: '学生会',
    members: [
      { id: 'u10', name: '朱主席', role: 'creator', avatarUrl: null },
      { id: 'u11', name: '钱副主席', role: 'admin', avatarUrl: null },
      { id: 'u12', name: '孙部长', role: 'admin', avatarUrl: null },
      { id: 'u13', name: '周干事', role: '', avatarUrl: null },
      { id: 'u14', name: '吴干事', role: '', avatarUrl: null },
      { id: 'u15', name: '郑干事', role: '', avatarUrl: null }
    ]
  }
])

// 表单校验规则
const orgRules = {
  name: [
    { required: true, message: '请输入组织名称', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ]
}

// 打开右键菜单
const openContextMenu = async (event, org) => {
  event.preventDefault()
  contextMenu.value.visible = true
  contextMenu.value.org = org
  contextMenuStyle.value = {
    position: 'fixed',
    top: `${event.clientY}px`,
    left: `${event.clientX}px`
  }
  
  await nextTick()
  contextDropdown.value?.handleOpen()
}

// 处理右键菜单命令
const handleContextMenuCommand = (command) => {
  const org = contextMenu.value.org
  if (command === 'rename') {
    openRenameDialog(org)
  } else if (command === 'delete') {
    confirmDelete(org)
  } else if (command === 'setAdmins') {
    setAdmins(org)
  }
  contextMenu.value.visible = false
}

// 打开重命名对话框
const openRenameDialog = (org) => {
  renameForm.value = { name: org.name, id: org.id }
  showRenameModal.value = true
}

// 确认重命名
const confirmRename = async () => {
  if (!renameForm.value.name.trim()) {
    ElMessage.warning('组织名称不能为空')
    return
  }
  
  try {
    // 模拟API请求
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 更新本地数据
    const org = organizations.value.find(o => o.id === renameForm.value.id)
    if (org) {
      org.name = renameForm.value.name
      ElMessage.success('组织名称已更新')
      showRenameModal.value = false
    }
  } catch (error) {
    ElMessage.error('更新失败，请重试')
  }
}

// 确认删除组织
const confirmDelete = (org) => {
  ElMessageBox.confirm(
    `确定要删除组织 "${org.name}" 吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 模拟API请求
    setTimeout(() => {
      organizations.value = organizations.value.filter(item => item.id !== org.id)
      ElMessage.success('组织已删除')
    }, 500)
  }).catch(() => {
    // 用户取消删除
  })
}

const adminStatusMap = ref({})
const showAddMemberModal = ref(false)
const showInviteConfirmModal = ref(false)
const addMemberForm = ref({ searchText: '' })
const searchResults = ref([])
const searchAttempted = ref(false)
const pendingInvite = ref(null)

// 申请加入组织相关变量
const showJoinOrgModal = ref(false)
const joinOrgForm = ref({
  orgId: '',
  message: ''
})
const joinOrgFormRef = ref(null)
const joinOrgRules = {
  orgId: [
    { required: true, message: '请输入组织ID', trigger: 'blur' },
    { min: 4, message: '组织ID长度至少为4个字符', trigger: 'blur' }
  ]
}
const orgSearchResult = ref(null)
const orgSearchAttempted = ref(false)

// 收到的邀请相关变量
const showInvitationModal = ref(false)
const pendingInvitations = ref([
  {
    id: 'inv1',
    orgId: 'org4',
    orgName: '人工智能实验室',
    inviter: '黄教授',
    inviteTime: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1天前
    message: '我们正在组建AI研究团队，希望你能加入我们的组织。',
    processing: false
  },
  {
    id: 'inv2',
    orgId: 'org5',
    orgName: '数据分析小组',
    inviter: '赵分析师',
    inviteTime: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2小时前
    message: '',
    processing: false
  },
  {
    id: 'inv3',
    orgId: 'org6',
    orgName: '前端开发团队',
    inviter: '李工程师',
    inviteTime: new Date(Date.now() - 30 * 60 * 1000), // 30分钟前
    message: '看到你有Vue的经验，想邀请你加入我们的前端团队。',
    processing: false
  }
])

// 格式化日期
const formatDate = (date) => {
  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  
  if (diffDays > 0) {
    return `${diffDays}天前`
  } else if (diffHours > 0) {
    return `${diffHours}小时前`
  } else if (diffMinutes > 0) {
    return `${diffMinutes}分钟前`
  } else {
    return '刚刚'
  }
}

// 接受邀请
const acceptInvitation = async (invitation) => {
  try {
    invitation.processing = true
    // 模拟API请求
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // 在实际应用中，这里应该调用API将用户添加到组织
    // 添加一个新的组织到用户的组织列表
    const newOrg = {
      id: invitation.orgId,
      name: invitation.orgName,
      members: [
        { id: 'u100', name: invitation.inviter, role: 'creator', avatarUrl: null },
        // 假设当前用户ID是u1，名称是"当前用户"
        { id: 'u1', name: '当前用户', role: '', avatarUrl: null }
      ]
    }
    
    // 检查是否已存在该组织
    const existingOrgIndex = organizations.value.findIndex(org => org.id === invitation.orgId)
    if (existingOrgIndex === -1) {
      organizations.value.push(newOrg)
    }
    
    // 从邀请列表中移除
    pendingInvitations.value = pendingInvitations.value.filter(item => item.id !== invitation.id)
    
    ElMessage.success(`已加入组织: ${invitation.orgName}`)
  } catch (error) {
    ElMessage.error('加入组织失败，请重试')
  } finally {
    invitation.processing = false
  }
}

// 拒绝邀请
const rejectInvitation = async (invitation) => {
  try {
    invitation.processing = true
    // 模拟API请求
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 从邀请列表中移除
    pendingInvitations.value = pendingInvitations.value.filter(item => item.id !== invitation.id)
    
    ElMessage.success('已拒绝邀请')
  } catch (error) {
    ElMessage.error('操作失败，请重试')
  } finally {
    invitation.processing = false
  }
}

// 计算当前选择的管理员数量
const countAdmins = () => {
  let count = 0
  for (const id in adminStatusMap.value) {
    if (adminStatusMap.value[id]) {
      count++
    }
  }
  return count
}

// 更新管理员状态
const updateAdminStatus = () => {
  // 这个函数主要用于在UI上提供反馈，实际逻辑已经由v-model和:disabled处理
}

// 设置管理员
const setAdmins = (org) => {
  currentOrg.value = org
  // 初始化管理员状态映射
  adminStatusMap.value = {}
  org.members.forEach(member => {
    if (member.role !== 'creator') {
      adminStatusMap.value[member.id] = member.role === 'admin'
    }
  })
  showAdminModal.value = true
}

// 保存管理员设置
const saveAdmins = async () => {
  try {
    // 模拟API请求
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 更新本地数据
    if (currentOrg.value) {
      currentOrg.value.members.forEach(member => {
        if (member.role !== 'creator') {
          member.role = adminStatusMap.value[member.id] ? 'admin' : ''
        }
      })
      ElMessage.success('管理员设置已更新')
      showAdminModal.value = false
    }
  } catch (error) {
    ElMessage.error('设置失败，请重试')
  }
}

// 添加成员按钮点击
const addMember = (org) => {
  currentOrg.value = org
  addMemberForm.value.searchText = ''
  searchResults.value = []
  searchAttempted.value = false
  showAddMemberModal.value = true
}

// 搜索用户
const searchUser = async () => {
  if (!addMemberForm.value.searchText.trim()) {
    ElMessage.warning('请输入用户ID或用户名')
    return
  }

  try {
    // 模拟API请求
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 模拟搜索结果
    searchResults.value = [
      { id: 'u20', name: '张三', avatarUrl: null },
      { id: 'u21', name: '李四', avatarUrl: null },
      { id: 'u22', name: '王五', avatarUrl: null }
    ].filter(user => 
      user.name.includes(addMemberForm.value.searchText) || 
      user.id.includes(addMemberForm.value.searchText)
    )
    searchAttempted.value = true
  } catch (error) {
    ElMessage.error('搜索用户失败，请重试')
  }
}

// 检查用户是否已在组织中
const isUserInOrg = (userId) => {
  return currentOrg.value?.members.some(member => member.id === userId) || false
}

// 邀请用户
const inviteUser = (user) => {
  pendingInvite.value = user
  showInviteConfirmModal.value = true
}

// 确认邀请
const confirmInvite = async () => {
  try {
    // 模拟API请求
    await new Promise(resolve => setTimeout(resolve, 700))
    
    // 添加用户到组织
    if (currentOrg.value && pendingInvite.value) {
      currentOrg.value.members.push({
        id: pendingInvite.value.id,
        name: pendingInvite.value.name,
        role: '',
        avatarUrl: pendingInvite.value.avatarUrl
      })
      
      ElMessage.success(`已成功邀请 ${pendingInvite.value.name} 加入组织`)
      showInviteConfirmModal.value = false
      // 关闭搜索弹窗
      showAddMemberModal.value = false
    }
  } catch (error) {
    ElMessage.error('邀请失败，请重试')
  }
}

// 搜索组织
const searchOrg = async () => {
  if (!joinOrgForm.value.orgId.trim()) {
    ElMessage.warning('请输入组织ID')
    return
  }

  try {
    // 模拟API请求
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 根据ID查找组织（模拟数据）
    const orgId = joinOrgForm.value.orgId.trim()
    const foundOrg = organizations.value.find(org => org.id === orgId)
    
    orgSearchResult.value = foundOrg
    orgSearchAttempted.value = true
    
    if (!foundOrg) {
      ElMessage.info('未找到该组织，请检查ID是否正确')
    }
  } catch (error) {
    ElMessage.error('搜索组织失败，请重试')
  }
}

// 获取创建者名称
const getCreatorName = (org) => {
  const creator = org?.members.find(m => m.role === 'creator')
  return creator?.name || '未知'
}

// 检查用户是否已在搜索到的组织中
const isUserInSearchOrg = computed(() => {
  // 假设当前用户ID为"u1"（在实际应用中应该从用户状态获取）
  const currentUserId = 'u1'
  return orgSearchResult.value?.members.some(member => member.id === currentUserId) || false
})

// 提交加入申请
const submitJoinRequest = async () => {
  if (!orgSearchResult.value) return
  
  try {
    // 模拟API请求
    await new Promise(resolve => setTimeout(resolve, 800))
    
    ElMessage.success({
      message: `已向 ${orgSearchResult.value.name} 提交加入申请，请等待管理员审核`,
      duration: 3000
    })
    
    // 重置表单和搜索结果
    joinOrgForm.value.orgId = ''
    joinOrgForm.value.message = ''
    orgSearchResult.value = null
    orgSearchAttempted.value = false
    showJoinOrgModal.value = false
  } catch (error) {
    ElMessage.error('提交申请失败，请重试')
  }
}

// 组织创建相关变量增强
// 注意：不要重复声明 newOrgForm，只需要在上面已有的声明中包含所有字段
const newOrgSearchResults = ref([])
const newOrgSearchAttempted = ref(false)

// 搜索用户（创建组织时）
const searchUserForNewOrg = async () => {
  if (!newOrgForm.value.searchText.trim()) {
    ElMessage.warning('请输入用户ID或用户名')
    return
  }

  try {
    // 模拟API请求
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 模拟搜索结果
    const searchText = newOrgForm.value.searchText.toLowerCase()
    const possibleUsers = [
      { id: 'u20', name: '张三', avatarUrl: null, selected: false },
      { id: 'u21', name: '李四', avatarUrl: null, selected: false },
      { id: 'u22', name: '王五', avatarUrl: null, selected: false },
      { id: 'u23', name: '赵六', avatarUrl: null, selected: false },
      { id: 'u24', name: '孙七', avatarUrl: null, selected: false }
    ]
    
    const results = possibleUsers.filter(user => 
      user.name.toLowerCase().includes(searchText) || 
      user.id.toLowerCase().includes(searchText)
    )
    
    // 保留已选中的用户
    const selectedUserIds = newOrgSearchResults.value
      .filter(u => u.selected)
      .map(u => u.id)
    
    results.forEach(user => {
      if (selectedUserIds.includes(user.id)) {
        user.selected = true
      }
    })
    
    // 将新结果与已有结果合并，去重
    const existingIds = newOrgSearchResults.value.map(u => u.id)
    const newUsers = results.filter(user => !existingIds.includes(user.id))
    
    newOrgSearchResults.value = [...newOrgSearchResults.value, ...newUsers]
    newOrgSearchAttempted.value = true
    
    if (results.length === 0) {
      ElMessage.info('未找到匹配的用户')
    }
  } catch (error) {
    ElMessage.error('搜索用户失败，请重试')
  }
}

// 获取已选择的用户
const getSelectedUsers = () => {
  return newOrgSearchResults.value.filter(user => user.selected)
}

// 更新选中用户数量（可用于其他逻辑）
const updateSelectedUsersCount = () => {
  // 可以在这里添加额外逻辑，如限制最大选择人数等
}

// 取消选择用户
const unselectUser = (userId) => {
  const user = newOrgSearchResults.value.find(u => u.id === userId)
  if (user) {
    user.selected = false
  }
}

// 取消创建组织
const cancelCreateOrg = () => {
  // 重置表单和搜索结果
  newOrgForm.value.name = ''
  newOrgForm.value.searchText = ''
  newOrgSearchResults.value = []
  newOrgSearchAttempted.value = false
  showCreateModal.value = false
}

// 创建新组织（修改为包含邀请成员）
const submitNewOrg = async () => {
  if (!newOrgForm.value.name.trim()) {
    ElMessage.warning('组织名称不能为空')
    return
  }
  
  try {
    // 模拟API请求
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // 获取选中的用户
    const selectedUsers = getSelectedUsers()
    
    // 创建新组织并添加到列表
    const newOrg = {
      id: 'org' + (organizations.value.length + 1),
      name: newOrgForm.value.name,
      members: [
        { id: 'u' + Date.now(), name: '当前用户', role: 'creator', avatarUrl: null }
      ]
    }
    
    // 添加选中的成员
    selectedUsers.forEach(user => {
      newOrg.members.push({
        id: user.id,
        name: user.name,
        role: '',
        avatarUrl: user.avatarUrl
      })
    })
    
    organizations.value.push(newOrg)
    
    // 显示成功消息
    if (selectedUsers.length > 0) {
      ElMessage.success(`组织创建成功，已邀请 ${selectedUsers.length} 名成员`)
    } else {
      ElMessage.success('组织创建成功')
    }
    
    // 重置表单和关闭弹窗
    cancelCreateOrg()
  } catch (error) {
    ElMessage.error('创建失败，请重试')
  }
}
</script>

<style scoped>
.org-container {
  padding: 16px;
}
.el-collapse-item__wrap{
  background-color: var(--card-bg);
}
.org-card {
  background-color: var(--card-bg);
  border: 1px solid var(--input-border-color);
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
  color: var(--text-color);
  margin: 0;
}

.org-list-container :deep(.el-collapse) {
  border: none;
  background-color: transparent;
}

.org-list-container :deep(.el-collapse-item__wrap) {
  background-color: var(--input-bg);
  border-radius: 6px;
}

.org-list-container :deep(.el-collapse-item__header) {
  background-color: var(--input-bg);
  color: var(--text-color);
  font-size: 16px;
  font-weight: bold;
  border-radius: 6px;
  padding: 10px 16px;
  margin-bottom: 0;
  border: 1px solid var(--input-border-color);
}

.org-list-container :deep(.el-collapse-item__content) {
  padding: 16px;
  background-color: var(--input-bg);
  border-radius: 6px;
  margin-bottom: 12px;
  color: var(--text-color);
}

.org-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.org-members-count {
  font-size: 12px;
  font-weight: normal;
  /* color: var(--text-secondary);*/
  /* background-color: var(--card-bg); */
  border-radius: 10px;
  padding: 2px 8px;
}

.org-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 16px;
}

.members-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
  margin-top: 8px;
}

.member-item {
  padding: 8px;
  border-radius: 8px;
  background-color: var(--card-bg);
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid var(--input-border-color);
}

.member-info {
  overflow: hidden;
}

.member-name {
  font-size: 14px;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 6px;
}

.role-badge {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
  font-weight: bold;
}

.role-badge.creator {
  background-color: #f56c6c;
  color: white;
}

.role-badge.admin {
  background-color: #409eff;
  color: white;
}

.admin-list {
  max-height: 300px;
  overflow-y: auto;
}

.admin-item {
  padding: 8px 0;
}

.creator-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0 8px 32px; /* 左侧留出与checkbox对齐的空间 */
  color: var(--text-color);
}

.admin-name {
  margin-left: 8px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

/* 搜索结果样式 */
.search-results {
  margin-top: 16px;
  border-top: 1px solid var(--input-border-color);
  padding-top: 10px;
}

.search-results h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: var(--text-color);
}

.search-result-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 8px;
  background-color: var(--card-bg);
  border: 1px solid var(--input-border-color);
}

.user-info {
  margin-left: 12px;
  flex: 1;
}

.user-name {
  font-weight: bold;
  color: var(--text-color);
}

.user-id {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.no-results {
  margin-top: 20px;
  text-align: center;
}

/* 适配夜间模式的元素 */
:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: var(--el-color-primary);
  border-color: var(--el-color-primary);
}

:deep(.el-checkbox__inner) {
  background-color: var(--input-bg);
  border-color: var(--input-border-color);
}

:deep(.el-dialog__title) {
  color: var(--text-color);
}

:deep(.el-dialog) {
  background-color: var(--card-bg);
}

:deep(.el-dialog__body) {
  color: var(--text-color);
}

:deep(.el-form-item__label) {
  color: var(--text-color);
}

:deep(.el-input__inner) {
  background-color: var(--input-bg);
  color: var(--input-text-color);
  border-color: var(--input-border-color);
}

/* 额外添加的夜间模式适配样式 */
:deep(.el-divider__text) {
  background-color: var(--input-bg);
  color: var(--text-color);
}

:deep(.el-divider) {
  background-color: var(--input-border-color);
}

:deep(.el-collapse-item__content) {
  background-color: var(--input-bg);
}

/* 修复折叠面板全局背景色 */
:deep(.el-collapse) {
  --el-bg-color: transparent !important;
  --el-fill-color-blank: transparent !important;
}

:deep(.el-collapse-item__wrap) {
  background-color: var(--input-bg) !important;
  border-bottom: none;
}

/* 修复下拉菜单颜色 */
:deep(.el-dropdown-menu) {
  background-color: var(--card-bg);
  border-color: var(--input-border-color);
}

:deep(.el-dropdown-menu__item) {
  color: var(--text-color);
}

:deep(.el-dropdown-menu__item:hover) {
  background-color: var(--input-bg);
}

/* 确保标签和输入框正确显示 */
:deep(.el-tag) {
  background-color: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary-light-8);
  color: var(--el-color-primary);
}

:deep(.el-tag--danger) {
  background-color: var(--el-color-danger-light-9);
  border-color: var(--el-color-danger-light-8);
  color: var(--el-color-danger);
}

/* 修改头部操作区样式 */
.header-actions {
  display: flex;
  gap: 10px;
  align-items: center; /* 确保按钮垂直居中对齐 */
}

.invitation-badge {
  margin-right: 0;
  display: inline-flex; /* 使用 inline-flex 确保徽章和按钮在同一行 */
  vertical-align: middle; /* 保持与其他按钮垂直对齐 */
}

/* 使按钮保持一致的高度 */
.header-actions .el-button {
  height: 32px; /* 固定高度确保对齐 */
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 确保徽章内的按钮样式一致 */
.invitation-badge :deep(.el-button) {
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 邀请通知相关样式 */
.invitation-badge {
  margin-right: 0;
}

.invitation-list {
  max-height: 400px;
  overflow-y: auto;
}

.invitation-item {
  padding: 16px;
  border-radius: 8px;
  background-color: var(--card-bg);
  margin-bottom: 12px;
  border: 1px solid var(--input-border-color);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.invitation-content {
  flex: 1;
}

.invitation-title {
  font-size: 16px;
  margin: 0 0 8px 0;
  color: var(--text-color);
}

.invitation-info {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.invitation-message {
  padding: 6px 0;
  color: var(--text-color-light);
  font-size: 13px;
}

.invitation-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-left: 16px;
}
</style>
