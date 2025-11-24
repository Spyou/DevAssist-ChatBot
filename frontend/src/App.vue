<template>
  <div class="h-screen flex bg-gray-900">
    <!-- Left Sidebar -->
    <aside class="w-80 bg-gray-950 border-r border-gray-800 flex flex-col">
      <div class="p-4 border-b border-gray-800">
        <div class="flex items-center gap-2 mb-1">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/>
            </svg>
          </div>
          <div>
            <h1 class="text-base font-bold text-white">DevAssist</h1>
            <p class="text-xs text-gray-400">AI Programming Assistant</p>
          </div>
        </div>
      </div>
      <FileUpload />
    </aside>
    
    <!-- Main Chat Area -->
    <main class="flex-1 flex flex-col">
      <ChatInterface />
    </main>
  </div>
</template>

<script setup>
import ChatInterface from './components/ChatInterface.vue'
import FileUpload from './components/FileUpload.vue'
</script>
