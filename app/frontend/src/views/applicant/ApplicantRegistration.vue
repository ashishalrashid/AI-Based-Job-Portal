<template>
  <div class="registration-page">
    <div class="registration-container">
      <div class="form-section">
        <div class="form-wrapper">
          <div class="form-header">
            <p class="welcome-text">Create your account</p>
            <h1 class="form-title">Candidate Registration</h1>
            <div v-if="backendStatus" class="status-indicator success">✅ Backend Connected</div>
            <div v-else class="status-indicator warning">⚠️ Backend Connection Issue</div>
          </div>

          <form class="registration-form" @submit.prevent="handleRegister">
            <div class="form-group">
              <label for="name" class="form-label">Full Name</label>
              <input
                type="text"
                id="name"
                v-model="form.name"
                placeholder="Enter your full name"
                class="form-input"
                :class="{ error: errors.name }"
                required
                :disabled="isLoading"
              />
              <p v-if="errors.name" class="error-text">{{ errors.name }}</p>
            </div>

            <div class="form-group">
              <label for="email" class="form-label">Email</label>
              <input
                type="email"
                id="email"
                v-model="form.email"
                placeholder="Enter your email"
                class="form-input"
                :class="{ error: errors.email }"
                required
                :disabled="isLoading"
              />
              <p v-if="errors.email" class="error-text">{{ errors.email }}</p>
            </div>

            <div class="form-group">
              <label for="password" class="form-label">Password</label>
              <input
                type="password"
                id="password"
                v-model="form.password"
                placeholder="Enter your password"
                class="form-input"
                :class="{ error: errors.password }"
                required
                :disabled="isLoading"
              />
              <p v-if="errors.password" class="error-text">{{ errors.password }}</p>
              
              <p class="help-text" :class="{ warning: form.password.length < 8 }">
                Password must be at least 8 characters long
              </p>
            </div>

            <div class="form-group">
              <label for="confirmPassword" class="form-label">Retype Password</label>
              <input
                type="password"
                id="confirmPassword"
                v-model="confirmPassword"
                placeholder="Retype your password"
                class="form-input"
                :class="{ error: passwordMismatch || errors.confirmPassword }"
                required
                :disabled="isLoading"
              />
              <p v-if="passwordMismatch" class="error-text">Passwords do not match</p>
              <p v-if="errors.confirmPassword" class="error-text">{{ errors.confirmPassword }}</p>
            </div>

            <div class="form-group">
              <label for="phone" class="form-label">Phone Number (Optional)</label>
              <input
                type="tel"
                id="phone"
                v-model="form.phone"
                placeholder="Enter your phone number"
                class="form-input"
                :class="{ error: errors.phone }"
                :disabled="isLoading"
              />
              <p v-if="errors.phone" class="error-text">{{ errors.phone }}</p>
            </div>

            <button type="submit" class="submit-btn" :disabled="isLoading || !isFormValid">
              <span v-if="isLoading" class="loading-spinner"></span>
              <span v-else>Create Account</span>
            </button>

            <div v-if="successMessage" class="success-message">
              <span class="success-icon">✅</span>
              {{ successMessage }}
            </div>

            <div v-if="errorMessage" class="error-message">
              <span class="error-icon">❌</span>
              {{ errorMessage }}
            </div>
          </form>

          <p class="login-link">
            Already a member?
            <router-link to="/login" class="login-btn">Login here</router-link>
          </p>
        </div>
      </div>

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

// Reactive form data
const form = ref({
  name: '',
  email: '',
  password: '',
  phone: '',
})

const confirmPassword = ref('')

// Loading and feedback states
const isLoading = ref(false)
const backendStatus = ref(null)
const successMessage = ref('')
const errorMessage = ref('')
const errors = ref({})

// Computed properties
const passwordMismatch = computed(
  () =>
    form.value.password && confirmPassword.value && form.value.password !== confirmPassword.value,
)

const isFormValid = computed(() => {
  return (
    form.value.name.trim() &&
    form.value.email.trim() &&
    form.value.password.length >= 8 &&
    form.value.password === confirmPassword.value &&
    !Object.values(errors.value).some((error) => error)
  )
})

// Validation functions
const validateForm = () => {
  errors.value = {}

  // Name validation
  if (!form.value.name.trim()) {
    errors.value.name = 'Name is required'
  } else if (form.value.name.trim().length < 2) {
    errors.value.name = 'Name must be at least 2 characters'
  }

  // Email validation
  if (!form.value.email.trim()) {
    errors.value.email = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
    errors.value.email = 'Please enter a valid email address'
  }

  // Password validation
  if (!form.value.password) {
    errors.value.password = 'Password is required'
  } else if (form.value.password.length < 8) {
    errors.value.password = 'Password must be at least 8 characters long'
  }

  // Confirm password validation
  if (!confirmPassword.value) {
    errors.value.confirmPassword = 'Please confirm your password'
  } else if (form.value.password !== confirmPassword.value) {
    errors.value.confirmPassword = 'Passwords do not match'
  }

  // Phone validation (optional but if provided, should be valid)
  if (form.value.phone && !/^[+]?[\d\s-()]+$/.test(form.value.phone)) {
    errors.value.phone = 'Please enter a valid phone number'
  }

  return Object.keys(errors.value).length === 0
}

// API call to register user
const registerUser = async (userData) => {
  const response = await api.post('/auth/register', {
    name: userData.name,
    email: userData.email,
    password: userData.password,
    role: 'applicant', // Since this is ApplicantRegistration
    phone: userData.phone || '',
    company_name: '',
    cin: '',
  })
  return response.data
}

// Main registration handler
const handleRegister = async (event) => {
  // Prevent any form submission
  event.preventDefault()

  // Clear previous messages
  successMessage.value = ''
  errorMessage.value = ''

  // Validate form
  if (!validateForm()) {
    console.log('Form validation failed:', errors.value)
    return
  }

  isLoading.value = true

  try {
    console.log('🚀 Starting applicant registration...', {
      name: form.value.name,
      email: form.value.email,
      role: 'applicant',
    })

    // Call backend API using POST method
    const result = await registerUser(form.value)

    console.log('✅ Registration successful:', result)

    // Show success message
    successMessage.value = 'Registration successful! You can now login with your credentials.'

    // Reset form
    setTimeout(() => {
      form.value = {
        name: '',
        email: '',
        password: '',
        phone: '',
      }
      confirmPassword.value = ''
      errors.value = {}
      successMessage.value = ''

      // Redirect to login
      router.push('/login')
    }, 2000)
  } catch (error) {
    console.error('❌ Registration failed:', error)

    // Handle different types of errors
    if (error.response) {
      // Server responded with error status
      const status = error.response.status
      const message = error.response.data?.message || 'Registration failed'

      if (status === 400) {
        if (message.includes('already exists') || message.includes('already')) {
          errors.value.email = 'An account with this email already exists'
        } else {
          errorMessage.value = message
        }
      } else if (status === 422) {
        errorMessage.value = 'Please check your input and try again'
      } else {
        errorMessage.value = `Registration failed: ${message}`
      }
    } else if (error.request) {
      // Network error
      errorMessage.value =
        'Unable to connect to server. Please check your internet connection and try again.'
    } else {
      // Other error
      errorMessage.value = 'An unexpected error occurred. Please try again.'
    }

    // Clear error message after 5 seconds
    setTimeout(() => {
      errorMessage.value = ''
    }, 5000)
  } finally {
    isLoading.value = false
  }
}

// Check backend connection
const checkBackendConnection = async () => {
  try {
    console.log('🔍 Checking backend connection...')
    const healthResponse = await api.get('/health')
    console.log('✅ Backend is healthy:', healthResponse.data.status)
    backendStatus.value = true
  } catch (error) {
    console.warn('⚠️ Backend health check failed:', error.message)
    backendStatus.value = false
  }
}

// Initialize backend check on component creation
checkBackendConnection()
</script>

<style scoped>
/* identical styling except name field fits seamlessly */
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

/* Left Section */
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

.status-indicator {
  margin-top: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-indicator.success {
  background-color: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.status-indicator.warning {
  background-color: #fef3c7;
  color: #92400e;
  border: 1px solid #fde68a;
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

.form-input.error {
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
}

.form-input:disabled {
  background-color: #f1f5f9;
  cursor: not-allowed;
}

.help-text {
  font-size: 0.8rem;
  color: #64748b;
  margin-top: 0.25rem;
  transition: color 0.3s ease;
}

/* NEW: Added warning style for short passwords */
.help-text.warning {
  color: #dc2626;
}

.error-text {
  font-size: 0.85rem;
  color: #dc2626;
  margin-top: 0.25rem;
}

.success-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  margin-top: 1rem;
  font-size: 0.9rem;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
  border-radius: 8px;
  margin-top: 1rem;
  font-size: 0.9rem;
}

.success-icon,
.error-icon {
  font-size: 1.1rem;
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
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.submit-btn:hover:not(:disabled) {
  background: #4f46e5;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
}

.submit-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 4px 12px rgba(156, 163, 175, 0.3);
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #ffffff;
  border-top: 2px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
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

/* Right Section (Illustration) */
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