<template>
  <div class="flex flex-col h-full bg-gray-900">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-gray-800 bg-gray-950">
      <div class="flex items-center justify-between">
        <h2 class="font-semibold text-white">Chat</h2>
        <button 
          v-if="messages.length > 0"
          @click="clearChat"
          class="text-sm text-gray-400 hover:text-white transition px-3 py-1.5 hover:bg-gray-800 rounded-lg">
          Clear
        </button>
      </div>
    </div>
    
    <!-- Messages -->
    <div class="flex-1 overflow-y-auto p-6" ref="chatContainer">
      <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full">
        <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center mb-4 shadow-lg shadow-blue-500/20">
          <svg class="w-9 h-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/>
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-white mb-2">Ready to help you code</h3>
        <p class="text-gray-400 text-sm">Ask about algorithms, debugging, or system design</p>
      </div>
      
      <div v-else class="space-y-6 max-w-4xl">
        <div v-for="(msg, idx) in messages" :key="idx">
          <!-- User -->
          <div v-if="msg.role === 'user'" class="flex justify-end">
            <div class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl px-4 py-3 max-w-2xl shadow-lg">
              <p class="text-sm leading-relaxed">{{ msg.content }}</p>
            </div>
          </div>
          
          <!-- Assistant -->
          <div v-else class="flex justify-start">
            <div class="bg-gray-800 border border-gray-700 rounded-2xl px-4 py-3 max-w-3xl">
              <div v-html="renderMarkdown(msg.content)" class="prose prose-invert prose-sm max-w-none"></div>
            </div>
          </div>
        </div>
        
        <!-- Streaming -->
        <div v-if="streaming" class="flex justify-start">
          <div class="bg-gray-800 border border-gray-700 rounded-2xl px-4 py-3 max-w-3xl">
            <div v-html="renderMarkdown(currentResponse)" class="prose prose-invert prose-sm max-w-none"></div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Input -->
    <div class="border-t border-gray-800 p-4 bg-gray-950">
      <div class="flex gap-3 max-w-4xl">
        <textarea
          v-model="userInput"
          @keydown.enter.exact.prevent="sendMessage"
          placeholder="Ask about code, algorithms, debugging..."
          class="flex-1 bg-gray-800 text-white border border-gray-700 rounded-xl px-4 py-3 resize-none 
                 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                 placeholder-gray-500"
          rows="2"
        ></textarea>
        <button
          @click="sendMessage"
          :disabled="!userInput.trim() || streaming"
          class="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl 
                 hover:from-blue-700 hover:to-indigo-700
                 disabled:from-gray-700 disabled:to-gray-700 disabled:cursor-not-allowed 
                 font-semibold shadow-lg shadow-blue-500/20 transition-all"
        >
          <svg v-if="!streaming" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
          </svg>
          <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
          </svg>
        </button>
      </div>
      <p class="text-xs text-gray-500 mt-2 text-center">Press Enter to send</p>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { marked } from 'marked'

const messages = ref([])
const userInput = ref('')
const streaming = ref(false)
const currentResponse = ref('')
const chatContainer = ref(null)
let ws = null

const renderMarkdown = (text) => {
  return marked(text, { breaks: true })
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

const clearChat = () => {
  messages.value = []
  currentResponse.value = ''
  streaming.value = false
}

const connectWebSocket = () => {
  if (ws?.readyState === WebSocket.OPEN) return
  
  ws = new WebSocket('ws://localhost:8000/ws/chat')
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    
    if (data.status === 'streaming' && data.token) {
      currentResponse.value += data.token
      scrollToBottom()
    } else if (data.status === 'done') {
      if (currentResponse.value) {
        messages.value.push({
          role: 'assistant',
          content: currentResponse.value
        })
      }
      currentResponse.value = ''
      streaming.value = false
      scrollToBottom()
    } else if (data.status === 'error') {
      messages.value.push({
        role: 'assistant',
        content: `⚠️ ${data.message}`
      })
      streaming.value = false
      currentResponse.value = ''
    }
  }
}

const sendMessage = () => {
  if (!userInput.value.trim() || streaming.value) return
  
  const messageText = userInput.value
  
  messages.value.push({
    role: 'user',
    content: messageText
  })
  
  connectWebSocket()
  
  setTimeout(() => {
    if (ws?.readyState === WebSocket.OPEN) {
      streaming.value = true
      currentResponse.value = ''
      
      ws.send(JSON.stringify({
        message: messageText
      }))
      
      scrollToBottom()
    }
  }, 100)
  
  userInput.value = ''
}
</script>

<style>
.prose {
  @apply text-gray-200;
}
.prose code {
  @apply bg-gray-900 px-2 py-1 rounded text-sm font-mono text-blue-400 border border-gray-700;
}
.prose pre {
  @apply bg-black text-gray-100 p-4 rounded-lg overflow-x-auto border border-gray-800;
}
.prose pre code {
  @apply bg-transparent border-0 text-gray-100;
}
.prose h1, .prose h2, .prose h3 {
  @apply text-white font-bold;
}
.prose p {
  @apply leading-relaxed;
}
.prose a {
  @apply text-blue-400 hover:text-blue-300;
}
.prose strong {
  @apply text-white font-semibold;
}
.prose ul, .prose ol {
  @apply text-gray-300;
}
</style>
