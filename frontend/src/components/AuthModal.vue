<template>
  <div v-if="show" class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
    <div class="bg-gray-900 border border-gray-800 rounded-2xl w-full max-w-md p-8 shadow-2xl">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-blue-500/20">
          <svg class="w-9 h-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/>
          </svg>
        </div>
        <h2 class="text-2xl font-bold text-white mb-2">{{ isLogin ? 'Welcome Back' : 'Create Account' }}</h2>
        <p class="text-gray-400 text-sm">{{ isLogin ? 'Sign in to continue coding' : 'Join DevAssist today' }}</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Name (Signup only) -->
        <div v-if="!isLogin">
          <label class="block text-sm font-medium text-gray-300 mb-2">Full Name</label>
          <input
            v-model="name"
            type="text"
            required
            placeholder="John Doe"
            class="w-full bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 
                   focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                   placeholder-gray-500"
          />
        </div>

        <!-- Email -->
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Email</label>
          <input
            v-model="email"
            type="email"
            required
            placeholder="you@example.com"
            class="w-full bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 
                   focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                   placeholder-gray-500"
          />
        </div>

        <!-- Password -->
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Password</label>
          <input
            v-model="password"
            type="password"
            required
            :placeholder="isLogin ? '••••••••' : 'Min. 6 characters'"
            class="w-full bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 
                   focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                   placeholder-gray-500"
          />
        </div>

        <!-- Error Message -->
        <div v-if="error" class="p-3 bg-red-950/50 border border-red-800 rounded-lg text-red-400 text-sm">
          {{ error }}
        </div>

        <!-- Success Message -->
        <div v-if="success" class="p-3 bg-emerald-950/50 border border-emerald-800 rounded-lg text-emerald-400 text-sm">
          {{ success }}
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700
                 disabled:from-gray-700 disabled:to-gray-700 disabled:cursor-not-allowed
                 text-white font-semibold py-3 rounded-lg shadow-lg shadow-blue-500/20 transition-all"
        >
          <span v-if="!loading">{{ isLogin ? 'Sign In' : 'Sign Up' }}</span>
          <span v-else class="flex items-center justify-center gap-2">
            <svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
              ircle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-widthth="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
            </svg>
            Processing...
          </span>
        </button>
      </form>

      <!-- Toggle -->
      <div class="mt-6 text-center">
        <button
          @click="toggleMode"
          class="text-sm text-gray-400 hover:text-white transition"
        >
          {{ isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  show: Boolean
})

const emit = defineEmits(['close', 'authenticated'])

const isLogin = ref(true)
const name = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(null)
const success = ref(null)

const toggleMode = () => {
  isLogin.value = !isLogin.value
  error.value = null
  success.value = null
  name.value = ''
}

const handleSubmit = async () => {
  loading.value = true
  error.value = null
  success.value = null

  try {
    const endpoint = isLogin.value ? '/api/login' : '/api/signup'
    
    const body = {
      email: email.value,
      password: password.value
    }
    
    if (!isLogin.value) {
      body.name = name.value
    }
    
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Authentication failed')
    }

    if (isLogin.value) {
      // Login success
      success.value = 'Login successful!'
      localStorage.setItem('access_token', data.session.access_token)
      localStorage.setItem('user_id', data.user.id)
      localStorage.setItem('user_email', data.user.email)
      localStorage.setItem('user_name', data.user.user_metadata?.name || email.value.split('@')[0])
      
      setTimeout(() => {
        emit('authenticated', data.user.id)
        emit('close')
      }, 1000)
    } else {
      // Signup success
      success.value = '✅ Account created! Please sign in.'
      setTimeout(() => {
        isLogin.value = true
        success.value = null
        password.value = ''
      }, 2000)
    }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>
