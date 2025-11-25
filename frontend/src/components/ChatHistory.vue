<template>
  <div class="flex flex-col h-full border-t border-gray-800">
    <div class="p-4 border-b border-gray-800">
      <div class="flex items-center justify-between mb-2">
        <h3 class="font-semibold text-white text-sm">Chat History</h3>
        <button
          @click="loadHistory"
          class="text-gray-400 hover:text-white transition p-1 hover:bg-gray-800 rounded"
          title="Refresh"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
        </button>
      </div>
      <p class="text-xs text-gray-500">Recent conversations</p>
    </div>

    <div class="flex-1 overflow-y-auto p-3 space-y-2">
      <div v-if="loading" class="flex justify-center py-8">
        <svg class="animate-spin h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
        </svg>
      </div>

      <div v-else-if="conversations.length === 0" class="text-center py-8">
        <svg class="w-12 h-12 text-gray-700 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
        </svg>
        <p class="text-xs text-gray-500">No conversations yet</p>
        <p class="text-xs text-gray-600 mt-1">Start chatting to see history</p>
      </div>

      <button
        v-for="conv in conversations"
        :key="conv.id"
        @click="loadConversation(conv)"
        class="w-full text-left p-3 rounded-lg bg-gray-800/50 hover:bg-gray-800 border border-gray-700 hover:border-gray-600 transition group"
      >
        <div class="flex items-start justify-between gap-2">
          <div class="flex-1 min-w-0">
            <p class="text-sm text-white font-medium truncate">
              {{ conv.title }}
            </p>
            <p class="text-xs text-gray-400 mt-1 line-clamp-2">
              {{ conv.preview }}
            </p>
            <p class="text-xs text-gray-600 mt-2">
              {{ formatDate(conv.timestamp) }}
            </p>
          </div>
          <button
            @click.stop="deleteConversation(conv.id)"
            class="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-red-400 transition p-1"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
          </button>
        </div>
      </button>
    </div>

    <div class="p-3 border-t border-gray-800">
      <button
        @click="clearAllHistory"
        class="w-full bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 py-2 rounded-lg font-medium text-xs transition-all"
      >
        Clear All History
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  userId: String
})

const emit = defineEmits(['load-conversation'])

const conversations = ref([])
const loading = ref(false)

const setVisible = (visible) => {
  if (visible) {
    loadHistory()
  }
}

defineExpose({
  setVisible
})

const loadHistory = async () => {
  if (!props.userId) {
    console.log('❌ No userId')
    return
  }
  
  console.log('🔍 Loading history for:', props.userId)
  loading.value = true
  
  try {
    const url = `/api/history/${props.userId}`
    console.log('📡 Fetching:', url)
    
    const response = await fetch(url)
    console.log('📥 Status:', response.status)
    
    const data = await response.json()
    console.log('📦 Data:', data)
    
    if (data.status === 'success') {
      conversations.value = data.conversations
      console.log('✅ Loaded:', conversations.value.length, 'conversations')
    }
  } catch (error) {
    console.error('❌ Error:', error)
  } finally {
    loading.value = false
  }
}

const loadConversation = (conv) => {
  emit('load-conversation', conv.messages)
}

const deleteConversation = async (convId) => {
  if (!confirm('Delete this conversation?')) return
  conversations.value = conversations.value.filter(c => c.id !== convId)
}

const clearAllHistory = async () => {
  if (!confirm('Clear all chat history?')) return
  
  try {
    const response = await fetch(`/api/clear-memory?user_id=${props.userId}`, {
      method: 'POST'
    })
    
    if (response.ok) {
      conversations.value = []
    }
  } catch (error) {
    console.error('Error clearing history:', error)
  }
}

const formatDate = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return 'Just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`
  
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

onMounted(() => {
  loadHistory()
})
</script>
