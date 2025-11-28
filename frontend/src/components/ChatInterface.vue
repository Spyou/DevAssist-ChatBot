<template>
  <div class="flex flex-col h-full bg-gray-900">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-gray-800 bg-gray-950">
      <div class="flex items-center justify-between">
        <h2 class="font-semibold text-white">Chat</h2>
        <div class="flex items-center gap-2">
          <button 
            @click="newChat"
            class="text-sm text-gray-400 hover:text-white transition px-3 py-1.5 hover:bg-gray-800 rounded-lg flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            New Chat
          </button>
          <button 
            v-if="messages.length > 0"
            @click="clearChat"
            class="text-sm text-gray-400 hover:text-white transition px-3 py-1.5 hover:bg-gray-800 rounded-lg"
          >
            Clear
          </button>
        </div>
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
        
        <!-- Web Search Indicator -->
        <div v-if="searching" class="flex justify-start">
          <div class="bg-blue-900/30 border border-blue-700 rounded-2xl px-4 py-3">
            <div class="flex items-center gap-2 text-blue-400">
              <svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
              <span>🔍 Searching the web with MCP...</span>
            </div>
          </div>
        </div>

        <!-- Qwen Indicator -->
        <div v-if="qwenProcessing" class="flex justify-start">
          <div class="bg-purple-900/30 border border-purple-700 rounded-2xl px-4 py-3">
            <div class="flex items-center gap-2 text-purple-400">
              <svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
              <span>🤖 Querying Qwen AI...</span>
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
      <!-- Web Search & Qwen Toggle -->
      <div class="flex items-center justify-between mb-3 max-w-4xl">
        <div class="flex items-center gap-2">
          <!-- Web Search Toggle -->
          <button
            @click="webSearchEnabled = !webSearchEnabled"
            :class="[
              'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all',
              webSearchEnabled 
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' 
                : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700'
            ]"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            <span v-if="webSearchEnabled">🌐 Web Search: ON</span>
            <span v-else>Web Search: OFF</span>
          </button>

          <!-- Qwen Toggle -->
          <button
            @click="qwenEnabled = !qwenEnabled"
            :class="[
              'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all',
              qwenEnabled 
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/20' 
                : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700'
            ]"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
            <span v-if="qwenEnabled">🤖 Qwen: ON</span>
            <span v-else>Qwen: OFF</span>
          </button>
        </div>
        
        <span v-if="webSearchEnabled || qwenEnabled" class="text-xs">
          <span v-if="webSearchEnabled" class="text-blue-400">Web Search Active</span>
          <span v-if="webSearchEnabled && qwenEnabled" class="text-gray-500"> • </span>
          <span v-if="qwenEnabled" class="text-purple-400">Qwen AI Active</span>
        </span>
      </div>
      
      <div class="flex gap-3 max-w-4xl">
        <textarea
          v-model="userInput"
          @keydown.enter.exact.prevent="sendMessage"
          :placeholder="getPlaceholder()"
          class="flex-1 bg-gray-800 text-white border border-gray-700 rounded-xl px-4 py-3 resize-none 
                 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                 placeholder-gray-500"
          rows="2"
        ></textarea>
        <button
          @click="sendMessage"
          :disabled="!userInput.trim() || streaming || searching || qwenProcessing"
          class="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl 
                 hover:from-blue-700 hover:to-indigo-700
                 disabled:from-gray-700 disabled:to-gray-700 disabled:cursor-not-allowed 
                 font-semibold shadow-lg shadow-blue-500/20 transition-all"
        >
          <svg v-if="!streaming && !searching && !qwenProcessing" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
          </svg>
          <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
          </svg>
        </button>
      </div>
      <p class="text-xs text-gray-500 mt-2 text-center">
        Press Enter to send
        <span v-if="webSearchEnabled" class="text-blue-400"> • Web search active 🔍</span>
        <span v-if="qwenEnabled" class="text-purple-400"> • Qwen AI active 🤖</span>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/atom-one-dark.css'

// Configure marked with syntax highlighting
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value
      } catch (err) {
        console.error('Highlight error:', err)
      }
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true
})

const messages = ref([])
const userInput = ref('')
const streaming = ref(false)
const searching = ref(false)
const qwenProcessing = ref(false)
const currentResponse = ref('')
const chatContainer = ref(null)
const currentSessionId = ref(null)
const webSearchEnabled = ref(false)
const qwenEnabled = ref(false)

const props = defineProps({
  userId: String
})

let ws = null

const renderMarkdown = (text) => {
  return marked.parse(text)
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

const getPlaceholder = () => {
  if (qwenEnabled.value) return 'Ask Qwen AI about code, algorithms...'
  if (webSearchEnabled.value) return 'Search the web about code, APIs, frameworks...'
  return 'Ask about code, algorithms, debugging...'
}

const newChat = () => {
  if (messages.value.length > 0) {
    if (confirm('Start a new chat? Current conversation will be saved in history.')) {
      messages.value = []
      currentResponse.value = ''
      streaming.value = false
      searching.value = false
      qwenProcessing.value = false
      currentSessionId.value = null
    }
  } else {
    currentSessionId.value = null
  }
}

const clearChat = () => {
  messages.value = []
  currentResponse.value = ''
  streaming.value = false
  searching.value = false
  qwenProcessing.value = false
  currentSessionId.value = null
}

const loadMessages = (msgs) => {
  messages.value = []
  streaming.value = false
  searching.value = false
  qwenProcessing.value = false
  currentResponse.value = ''
  currentSessionId.value = null
  
  nextTick(() => {
    messages.value = msgs.map(m => ({
      role: m.role,
      content: m.content
    }))
    scrollToBottom()
  })
}

defineExpose({
  loadMessages
})

const connectWebSocket = () => {
  if (ws?.readyState === WebSocket.OPEN) return
  
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  const wsUrl = `${protocol}//${host}/ws/chat`
  
  console.log('Connecting to:', wsUrl)
  ws = new WebSocket(wsUrl)
  
  ws.onopen = () => {
    console.log('WebSocket connected')
  }
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    
    if (data.session_id) {
      currentSessionId.value = data.session_id
      console.log('Session ID:', data.session_id)
    }
    
    if (data.status === 'searching') {
      searching.value = true
      scrollToBottom()
    } else if (data.status === 'qwen_processing') {
      qwenProcessing.value = true
      scrollToBottom()
    } else if (data.status === 'streaming' && data.token) {
      searching.value = false
      qwenProcessing.value = false
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
      searching.value = false
      qwenProcessing.value = false
      scrollToBottom()
    } else if (data.status === 'error') {
      messages.value.push({
        role: 'assistant',
        content: `⚠️ ${data.message}`
      })
      streaming.value = false
      searching.value = false
      qwenProcessing.value = false
      currentResponse.value = ''
    }
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
    messages.value.push({
      role: 'assistant',
      content: '⚠️ Connection error'
    })
    streaming.value = false
    searching.value = false
    qwenProcessing.value = false
  }
}

const sendMessage = () => {
  if (!userInput.value.trim() || streaming.value || searching.value || qwenProcessing.value) return
  
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
        message: messageText,
        user_id: props.userId,
        session_id: currentSessionId.value,
        web_search_enabled: webSearchEnabled.value,
        qwen_enabled: qwenEnabled.value
      }))
      
      scrollToBottom()
    }
  }, 100)
  
  userInput.value = ''
}
</script>

<style>
@import 'highlight.js/styles/atom-one-dark.css';

.prose {
  @apply text-gray-200;
}

.prose code {
  @apply bg-gray-900 px-2 py-1 rounded text-sm font-mono text-blue-400 border border-gray-700;
}

.prose pre {
  @apply bg-gray-950 text-gray-100 p-4 rounded-lg overflow-x-auto border border-gray-700 my-4;
}

.prose pre code {
  @apply bg-transparent border-0 text-sm;
  display: block;
  padding: 0;
}

.prose h1, .prose h2, .prose h3 {
  @apply text-white font-bold mt-4 mb-2;
}

.prose p {
  @apply leading-relaxed mb-4;
}

.prose a {
  @apply text-blue-400 hover:text-blue-300 underline;
}

.prose strong {
  @apply text-white font-bold;
}

.prose ul, .prose ol {
  @apply text-gray-300 ml-4 mb-4;
}

.prose li {
  @apply mb-2;
}
</style>
