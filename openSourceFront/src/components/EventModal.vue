<template>
    <div class="modal-overlay">
      <div class="modal">
        <h3>添加事件</h3>
  
        <label>事件名称</label>
        <input v-model="form.title" type="text" placeholder="如：项目会议" />
  
        <label>事件类型</label>
        <input v-model="form.type" type="text" placeholder="如：课程 / 工作 / 自习" />
  
        <label>星期</label>
        <select v-model="form.day">
          <option value="Mon">周一</option>
          <option value="Tue">周二</option>
          <option value="Wed">周三</option>
          <option value="Thu">周四</option>
          <option value="Fri">周五</option>
          <option value="Sat">周六</option>
          <option value="Sun">周日</option>
        </select>
  
        <label>开始时间</label>
        <input v-model="form.start" type="time" />
  
        <label>结束时间</label>
        <input v-model="form.end" type="time" />
  
        <label>备注</label>
        <textarea v-model="form.note" placeholder="可选补充说明"></textarea>
  
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
  
  const form = reactive({
    title: '',
    type: '',
    day: 'Mon',
    start: '',
    end: '',
    note: ''
  })
  
  const submit = () => {
    if (!form.title || !form.start || !form.end) {
      alert('请填写完整信息')
      return
    }
  
    emit('save', { ...form }) // 向父组件传递新事件对象
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
  