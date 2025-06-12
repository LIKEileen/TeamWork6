<template>
    <div class="modal-overlay">
      <div class="modal">
        <h3>添加长期事件</h3>
  
        <label>事件名称</label>
        <input v-model="form.title" type="text" />
  
        <label>事件类型</label>
        <input v-model="form.type" type="text" />
  
        <label>重复频率</label>
        <select v-model="form.frequency">
          <option value="每天">每天</option>
          <option value="每周">每周</option>
        </select>
  
        <div v-if="form.frequency === '每周'">
          <label>适用星期（可多选）</label>
          <div class="checkbox-group">
            <label v-for="day in weekOptions" :key="day.value">
              <input
                type="checkbox"
                :value="day.value"
                v-model="form.days"
              />
              {{ day.label }}
            </label>
          </div>
        </div>
  
        <label>开始时间</label>
        <input v-model="form.start" type="time" />
  
        <label>结束时间</label>
        <input v-model="form.end" type="time" />
  
        <label>备注</label>
        <textarea v-model="form.note"></textarea>
  
        <div class="buttons">
          <button @click="submit">确认</button>
          <button class="cancel" @click="$emit('close')">取消</button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { reactive } from 'vue'
  
  const emit = defineEmits(['save', 'close'])
  
  const weekOptions = [
    { value: 'Mon', label: '周一' },
    { value: 'Tue', label: '周二' },
    { value: 'Wed', label: '周三' },
    { value: 'Thu', label: '周四' },
    { value: 'Fri', label: '周五' },
    { value: 'Sat', label: '周六' },
    { value: 'Sun', label: '周日' }
  ]
  
  const form = reactive({
    title: '',
    type: '',
    frequency: '每天',
    days: [],
    start: '',
    end: '',
    note: ''
  })
  
  const submit = () => {
    if (!form.title || !form.start || !form.end) {
      alert('请填写完整信息')
      return
    }
    if (form.frequency === '每周' && form.days.length === 0) {
      alert('请选择重复的星期')
      return
    }
  
    emit('save', { ...form }) // 返回整个对象
  }
  </script>
  
  <style scoped>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.3);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  
  .modal {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    width: 320px;
    max-width: 90vw;
  }
  
  label {
    display: block;
    margin-top: 10px;
    font-weight: bold;
    color: #333;
  }
  
  input,
  select,
  textarea {
    width: 100%;
    margin-top: 4px;
    padding: 8px;
    border-radius: 6px;
    border: 1px solid #ccc;
    margin-bottom: 10px;
    font-size: 14px;
  }
  
  .checkbox-group {
    display: flex;
    flex-wrap: wrap;
    gap: 6px 12px;
    margin: 5px 0 10px;
  }
  
  .checkbox-group label {
    font-weight: normal;
  }
  
  .buttons {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 16px;
  }
  
  button {
    padding: 8px 14px;
    font-size: 14px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    background-color: #4a90e2;
    color: white;
    transition: 0.2s;
  }
  
  button:hover {
    background-color: #357ab8;
  }
  
  .cancel {
    background-color: #aaa;
  }
  
  .cancel:hover {
    background-color: #888;
  }
  </style>
  