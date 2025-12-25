<template>
  <div class="registration-page">
    <div class="registration-container">
      <!-- Left: Form -->
      <div class="form-section">
        <div class="form-wrapper">
          <div class="form-header">
            <p class="welcome-text">Welcome to Jobshala</p>
            <h1 class="form-title">Register your company</h1>
          </div>

          <form class="registration-form" @submit.prevent="handleRegister">
            <div class="form-group">
              <label for="companyName" class="form-label">Company Name</label>
              <input
                type="text"
                id="companyName"
                v-model="companyName"
                placeholder="Enter your company name"
                class="form-input"
                required
              />
            </div>

            <div class="form-group">
              <label for="cin" class="form-label">CIN</label>
              <input
                type="text"
                id="cin"
                v-model="cin"
                placeholder="Enter your company CIN"
                class="form-input"
                required
              />
            </div>

            <div class="form-group">
              <label for="email" class="form-label">Email</label>
              <input
                type="email"
                id="email"
                v-model="email"
                placeholder="Enter your email"
                class="form-input"
                required
              />
            </div>

            <div class="form-group">
              <label for="password" class="form-label">Password</label>
              <input
                type="password"
                id="password"
                v-model="password"
                placeholder="Enter your password"
                class="form-input"
                required
              />
            </div>

            <div class="form-group">
              <label for="confirmPassword" class="form-label">Retype Password</label>
              <input
                type="password"
                id="confirmPassword"
                v-model="confirmPassword"
                placeholder="Retype your password"
                class="form-input"
                required
              />
              <p v-if="passwordMismatch" class="error-text">Passwords do not match</p>
            </div>

            <!-- Error Message -->
            <div v-if="errorMessage" class="error-message">
              {{ errorMessage }}
            </div>

            <button type="submit" class="submit-btn" :disabled="isLoading">
              {{ isLoading ? 'Registering...' : 'Register' }}
            </button>
          </form>

          <p class="login-link">
            Already a member?
            <router-link to="/login" class="login-btn">Login here</router-link>
          </p>
        </div>
      </div>

      <!-- Right: Illustration -->
      <div class="illustration-section">
        <div class="illustration-wrapper">
          <svg viewBox="0 0 600 600" xmlns="http://www.w3.org/2000/svg" class="login-illustration">
            <circle cx="300" cy="300" r="280" fill="#f0f0f5" opacity="0.5" />
            <rect x="180" y="380" width="240" height="8" fill="#2d2d44" rx="4" />
            <g id="person1">
              <circle cx="230" cy="240" r="35" fill="#8b6f5c" />
              <path
                d="M 200 230 Q 200 200 230 195 Q 260 200 260 230 Q 260 240 230 240 Q 200 240 200 230"
                fill="#2d2d44"
              />
              <path
                d="M 230 275 Q 210 280 200 340 L 200 380 L 260 380 L 260 340 Q 250 280 230 275"
                fill="#3a3a52"
              />
              <path d="M 230 290 Q 190 300 180 320 L 190 330 Q 200 315 230 310" fill="#8b6f5c" />
              <path d="M 230 290 Q 270 300 300 330 L 305 325 Q 285 305 230 310" fill="#8b6f5c" />
              <rect x="270" y="340" width="80" height="50" fill="#6366f1" rx="3" />
              <rect x="275" y="345" width="70" height="35" fill="#4f46e5" rx="2" />
            </g>

            <g id="person2">
              <circle cx="370" cy="250" r="35" fill="#f4b5a4" />
              <path
                d="M 340 240 Q 340 210 370 205 Q 400 210 400 240 Q 400 250 370 250 Q 340 250 340 240"
                fill="#2d2d44"
              />
              <path
                d="M 370 285 Q 350 290 340 350 L 340 380 L 400 380 L 400 350 Q 390 290 370 285"
                fill="#6366f1"
              />
              <path d="M 370 300 Q 330 310 320 335 L 325 345 Q 340 325 370 315" fill="#f4b5a4" />
              <path d="M 370 300 Q 340 315 305 330" fill="#f4b5a4" />
            </g>

            <rect x="200" y="380" width="60" height="80" fill="#2d2d44" opacity="0.8" />
            <circle cx="210" cy="470" r="8" fill="#2d2d44" />
            <circle cx="250" cy="470" r="8" fill="#2d2d44" />
            <rect x="340" y="380" width="60" height="80" fill="#2d2d44" opacity="0.8" />
            <circle cx="350" cy="470" r="8" fill="#2d2d44" />
            <circle cx="390" cy="470" r="8" fill="#2d2d44" />
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()

const companyName = ref('')
const cin = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const isLoading = ref(false)
const errorMessage = ref('')

const passwordMismatch = computed(
  () => password.value && confirmPassword.value && password.value !== confirmPassword.value,
)

const handleRegister = async () => {
  console.log('handleRegister called for organization')
  errorMessage.value = ''

  // Validation
  if (!companyName.value.trim()) {
    errorMessage.value = 'Please enter your company name!'
    return
  }

  if (!cin.value.trim()) {
    errorMessage.value = 'Please enter your company CIN!'
    return
  }

  if (password.value.length < 8) {
    errorMessage.value = 'Password must be at least 8 characters long'
    return
  }

  if (passwordMismatch.value) {
    errorMessage.value = 'Passwords do not match!'
    return
  }

  console.log('Validation passed, setting loading to true')
  isLoading.value = true

  try {
    console.log('Attempting organization registration with:', {
      company_name: companyName.value,
      email: email.value,
      cin: cin.value,
    })

    console.log('Making API call to /auth/register')
    const response = await api.post('/auth/register', {
      name: companyName.value,
      company_name: companyName.value,
      email: email.value,
      password: password.value,
      cin: cin.value,
      phone: '',
      role: 'admin', // Backend expects 'admin' role for company/organization users
    })

    console.log('Registration successful:', response.data)
    alert('Company registered successfully! Please login.')
    // Redirect to login page
    router.push({ name: 'login' })
  } catch (error) {
    console.error('Registration error:', error)
    console.error('Error response:', error.response?.data)
    console.error('Error status:', error.response?.status)
    const errorMessageText =
      error.response?.data?.message || error.message || 'Registration failed. Please try again.'
    errorMessage.value = errorMessageText
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.registration-page {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  overflow: hidden;
  margin: 0;
  padding: 0;
}

.registration-container {
  width: 100%;
  height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: #fff;
}

/* Left: Form */
.form-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  overflow-y: auto;
}

.form-wrapper {
  width: 100%;
  max-width: 420px;
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.welcome-text {
  font-size: 0.95rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.form-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.registration-form {
  margin-top: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.form-input {
  width: 100%;
  padding: 0.875rem 1rem;
  font-size: 0.95rem;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  outline: none;
  transition: all 0.3s ease;
  background: #fff;
  color: #1e293b;
}

.form-input::placeholder {
  color: #cbd5e1;
}

.form-input:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.error-text {
  font-size: 0.85rem;
  color: #dc2626;
  margin-top: 0.25rem;
}

.error-message {
  padding: 0.75rem 1rem;
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 8px;
  color: #c33;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  text-align: center;
}

.submit-btn {
  width: 100%;
  padding: 0.875rem;
  background: #6366f1;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.submit-btn:hover {
  background: #4f46e5;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
}

.login-link {
  margin-top: 1.5rem;
  font-size: 0.9rem;
  color: #475569;
  text-align: center;
}

.login-btn {
  color: #6366f1;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}

.login-btn:hover {
  color: #4f46e5;
  text-decoration: underline;
}

/* Right: Illustration */
.illustration-section {
  background: linear-gradient(135deg, #f0f0f5 0%, #e8e8f0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
}

.illustration-wrapper {
  width: 100%;
  max-width: 500px;
  animation: float 6s ease-in-out infinite;
}

.login-illustration {
  width: 100%;
  height: auto;
  filter: drop-shadow(0 10px 30px rgba(0, 0, 0, 0.1));
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

/* Responsive */
@media (max-width: 968px) {
  .registration-container {
    grid-template-columns: 1fr;
  }
  .illustration-section {
    display: none;
  }
}
</style>
