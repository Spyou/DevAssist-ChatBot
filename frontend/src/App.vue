<template>
  <div>
    <AuthModal 
      :show="!isAuthenticated" 
      @authenticated="handleAuthenticated"
    />

    <div v-if="isAuthenticated" class="h-screen flex bg-gray-900">
      <!-- Left Sidebar -->
      <aside class="w-80 bg-gray-950 border-r border-gray-800 flex flex-col">
        <div class="p-4 border-b border-gray-800">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/>
                </svg>
              </div>
              <div>
                <h1 class="text-base font-bold text-white">DevAssist</h1>
                <p class="text-xs text-gray-400">{{ userName || userEmail }}</p>
              </div>
            </div>
            <button 
              @click="logout"
              class="text-gray-400 hover:text-white transition p-2 hover:bg-gray-800 rounded-lg"
              title="Logout"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Tabs -->
        <div class="flex border-b border-gray-800">
          <button
            @click="activeTab = 'upload'"
            :class="activeTab === 'upload' ? 'bg-gray-900 text-white' : 'text-gray-400 hover:text-white'"
            class="flex-1 py-3 text-sm font-medium transition"
          >
            Documents
          </button>
          <button
            @click="activeTab = 'history'"
            :class="activeTab === 'history' ? 'bg-gray-900 text-white' : 'text-gray-400 hover:text-white'"
            class="flex-1 py-3 text-sm font-medium transition"
          >
            History
          </button>
        </div>
        
        <FileUpload v-show="activeTab === 'upload'" />
        <ChatHistory 
          ref="chatHistory"
          v-show="activeTab === 'history'" 
          :userId="userId"
          @load-conversation="handleLoadConversation"
        />
      </aside>
      
      <!-- Main Chat Area -->
      <main class="flex-1 flex flex-col">
        <ChatInterface 
          ref="chatInterface"
          :userId="userId" 
        />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import ChatInterface from './components/ChatInterface.vue'
import FileUpload from './components/FileUpload.vue'
import ChatHistory from './components/ChatHistory.vue'
import AuthModal from './components/AuthModal.vue'

const isAuthenticated = ref(false)
const userId = ref(null)
const userEmail = ref(null)
const userName = ref(null)
const activeTab = ref('upload')
const chatInterface = ref(null)
const chatHistory = ref(null)

onMounted(() => {
  const token = localStorage.getItem('access_token')
  const savedUserId = localStorage.getItem('user_id')
  const savedEmail = localStorage.getItem('user_email')
  const savedName = localStorage.getItem('user_name')
  
  // Only authenticate if user has valid token (no guest mode)
  if (token && savedUserId) {
    isAuthenticated.value = true
    userId.value = savedUserId
    userEmail.value = savedEmail
    userName.value = savedName
  }
})

const handleAuthenticated = (id) => {
  userId.value = id
  userEmail.value = localStorage.getItem('user_email')
  userName.value = localStorage.getItem('user_name')
  isAuthenticated.value = true
}

const handleLoadConversation = (messages) => {
  if (chatInterface.value) {
    chatInterface.value.loadMessages(messages)
    activeTab.value = 'upload'
  }
}

watch(activeTab, (newTab) => {
  if (newTab === 'history' && chatHistory.value) {
    chatHistory.value.setVisible(true)
  }
})

const logout = () => {
  localStorage.clear()
  location.reload()
}
</script>
