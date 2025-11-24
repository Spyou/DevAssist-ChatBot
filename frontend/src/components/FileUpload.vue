<template>
  <div class="p-4 flex-1 flex flex-col overflow-y-auto">
    <h3 class="font-semibold text-white mb-1 text-sm">Upload Documents</h3>
    <p class="text-xs text-gray-400 mb-4">Add technical docs for RAG context</p>
    
    <div class="space-y-3">
      <div class="border-2 border-dashed border-gray-700 rounded-xl p-4 hover:border-blue-500 transition">
        <input
          type="file"
          @change="handleFileChange"
          accept=".txt,.md,.pdf"
          class="block w-full text-sm text-gray-400
                 file:mr-2 file:py-2 file:px-3 
                 file:rounded-lg file:border-0 
                 file:bg-gradient-to-r file:from-blue-600 file:to-indigo-600 
                 file:text-white file:font-medium
                 hover:file:from-blue-700 hover:file:to-indigo-700
                 file:cursor-pointer cursor-pointer file:transition-all file:shadow-lg file:shadow-blue-500/20"
        />
        <p class="text-xs text-gray-500 mt-2">PDF, TXT, MD • Max 5MB</p>
      </div>
      
      <button
        @click="uploadFile"
        :disabled="!selectedFile || uploading"
        class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700
               disabled:from-gray-700 disabled:to-gray-700 disabled:cursor-not-allowed
               text-white py-2.5 rounded-lg font-semibold text-sm shadow-lg shadow-blue-500/20 transition-all"
      >
        {{ uploading ? 'Uploading...' : 'Upload' }}
      </button>
      
      <button
        @click="clearDocuments"
        class="w-full bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 py-2 rounded-lg font-medium text-sm transition-all"
      >
        Clear Documents
      </button>
      
      <div v-if="status" 
           class="p-3 rounded-lg text-sm border"
           :class="status.type === 'success' 
             ? 'bg-emerald-950/50 border-emerald-800 text-emerald-400' 
             : 'bg-red-950/50 border-red-800 text-red-400'">
        {{ status.message }}
      </div>
      
      <div class="mt-6 p-3 bg-gray-800/50 rounded-lg border border-gray-700">
        <div class="flex items-start gap-2">
          <svg class="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <div>
            <p class="text-xs text-gray-400 font-medium mb-1">RAG System</p>
            <p class="text-xs text-gray-500 leading-relaxed">
              Docs are chunked (500 chars) and embedded. Top 3 relevant chunks added to queries.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const selectedFile = ref(null)
const uploading = ref(false)
const status = ref(null)

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0]
  status.value = null
}

const uploadFile = async () => {
  if (!selectedFile.value) return
  
  uploading.value = true
  status.value = null
  
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  
  try {
    const response = await fetch('http://localhost:8000/upload', {
      method: 'POST',
      body: formData
    })
    
    const result = await response.json()
    
    if (result.status === 'success') {
      status.value = {
        type: 'success',
        message: `✓ ${result.filename} (${result.chunks_processed} chunks)`
      }
    } else {
      status.value = {
        type: 'error',
        message: result.message
      }
    }
  } catch (error) {
    status.value = {
      type: 'error',
      message: 'Upload failed'
    }
  } finally {
    uploading.value = false
  }
}

const clearDocuments = async () => {
  try {
    const response = await fetch('http://localhost:8000/clear', {
      method: 'POST'
    })
    
    const result = await response.json()
    
    if (result.status === 'success') {
      status.value = {
        type: 'success',
        message: '✓ Documents cleared'
      }
      selectedFile.value = null
    }
  } catch (error) {
    status.value = {
      type: 'error',
      message: 'Clear failed'
    }
  }
}
</script>
