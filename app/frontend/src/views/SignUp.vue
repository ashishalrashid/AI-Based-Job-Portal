<template>
  <div class="signup-page">
    <div class="signup-container">
      <!-- Left Side - Form -->
      <div class="form-section">
        <div class="form-wrapper">
          <div class="form-header">
            <p class="welcome-text">Welcome!</p>
            <h1 class="form-title">Please Register</h1>
          </div>

          <!-- Sign In Button in Top Right -->
          <div class="sign-in-link">
            <router-link to="/login" class="signin-btn"> Sign In </router-link>
          </div>

          <form @submit.prevent="handleSignUp" class="signup-form">
            <!-- Email Address -->
            <div class="form-group">
              <label for="email" class="form-label">Email address</label>
              <input
                type="email"
                id="email"
                v-model="email"
                placeholder="Enter email address"
                class="form-input"
                required
              />
            </div>

            <!-- Password -->
            <div class="form-group">
              <label for="password" class="form-label">Password</label>
              <div class="password-input-wrapper">
                <input
                  :type="showPassword ? 'text' : 'password'"
                  id="password"
                  v-model="password"
                  placeholder="••••••••••"
                  class="form-input"
                  required
                  minlength="8"
                />
                <button
                  type="button"
                  @click="togglePassword"
                  class="password-toggle"
                  aria-label="Toggle password visibility"
                >
                  <svg
                    v-if="!showPassword"
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path
                      d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"
                    />
                    <line x1="1" y1="1" x2="23" y2="23" />
                  </svg>
                  <svg
                    v-else
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Confirm Password -->
            <div class="form-group">
              <label for="confirm-password" class="form-label">Confirm Password</label>
              <div class="password-input-wrapper">
                <input
                  :type="showConfirmPassword ? 'text' : 'password'"
                  id="confirm-password"
                  v-model="confirmPassword"
                  placeholder="••••••••••"
                  class="form-input"
                  required
                  minlength="8"
                />
                <button
                  type="button"
                  @click="toggleConfirmPassword"
                  class="password-toggle"
                  aria-label="Toggle password visibility"
                >
                  <svg
                    v-if="!showConfirmPassword"
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path
                      d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"
                    />
                    <line x1="1" y1="1" x2="23" y2="23" />
                  </svg>
                  <svg
                    v-else
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Error Message -->
            <div v-if="errorMessage" class="error-message">
              {{ errorMessage }}
            </div>

            <!-- Submit Button -->
            <button type="submit" class="submit-btn" :disabled="isLoading">
              {{ isLoading ? 'Signing Up...' : 'Sign Up' }}
            </button>
          </form>
        </div>
      </div>

      <!-- Right Side - Illustration -->
      <div class="illustration-section">
        <div class="illustration-wrapper">
          <svg viewBox="0 0 600 600" xmlns="http://www.w3.org/2000/svg" class="illustration">
            <!-- Background Circle -->
            <circle cx="300" cy="300" r="280" fill="#f0f0f5" opacity="0.5" />

            <!-- Desk -->
            <rect x="180" y="380" width="240" height="8" fill="#2d2d44" rx="4" />

            <!-- Person 1 (Left - Darker skin tone) -->
            <g id="person1">
              <!-- Head -->
              <circle cx="230" cy="240" r="35" fill="#8b6f5c" />
              <!-- Hair -->
              <path
                d="M 200 230 Q 200 200 230 195 Q 260 200 260 230 Q 260 240 230 240 Q 200 240 200 230"
                fill="#2d2d44"
              />
              <!-- Body -->
              <path
                d="M 230 275 Q 210 280 200 340 L 200 380 L 260 380 L 260 340 Q 250 280 230 275"
                fill="#3a3a52"
              />
              <!-- Arms -->
              <path d="M 230 290 Q 190 300 180 320 L 190 330 Q 200 315 230 310" fill="#8b6f5c" />
              <path d="M 230 290 Q 270 300 300 330 L 305 325 Q 285 305 230 310" fill="#8b6f5c" />

              <!-- Laptop being shared -->
              <rect x="270" y="340" width="80" height="50" fill="#6366f1" rx="3" />
              <rect x="275" y="345" width="70" height="35" fill="#4f46e5" rx="2" />
            </g>

            <!-- Person 2 (Right - Lighter skin tone) -->
            <g id="person2">
              <!-- Head -->
              <circle cx="370" cy="250" r="35" fill="#f4b5a4" />
              <!-- Hair -->
              <path
                d="M 340 240 Q 340 210 370 205 Q 400 210 400 240 Q 400 250 370 250 Q 340 250 340 240"
                fill="#2d2d44"
              />
              <!-- Body -->
              <path
                d="M 370 285 Q 350 290 340 350 L 340 380 L 400 380 L 400 350 Q 390 290 370 285"
                fill="#6366f1"
              />
              <!-- Arms -->
              <path d="M 370 300 Q 330 310 320 335 L 325 345 Q 340 325 370 315" fill="#f4b5a4" />
              <path d="M 370 300 Q 340 315 305 330" fill="#f4b5a4" />
            </g>

            <!-- Chair 1 -->
            <rect x="200" y="380" width="60" height="80" fill="#2d2d44" opacity="0.8" />
            <circle cx="210" cy="470" r="8" fill="#2d2d44" />
            <circle cx="250" cy="470" r="8" fill="#2d2d44" />

            <!-- Chair 2 -->
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')

const togglePassword = () => {
  showPassword.value = !showPassword.value
}

const toggleConfirmPassword = () => {
  showConfirmPassword.value = !showConfirmPassword.value
}

const handleSignUp = async () => {
  console.log('handleSignUp called')
  errorMessage.value = ''

  // Validation
  if (password.value.length < 8) {
    console.log('Password validation failed')
    errorMessage.value = 'Password must be at least 8 characters long'
    return
  }

  if (password.value !== confirmPassword.value) {
    console.log('Password confirmation failed')
    errorMessage.value = 'Passwords do not match'
    return
  }

  console.log('Validation passed, setting loading to true')
  isLoading.value = true

  try {
    const name = email.value.split('@')[0] // Extract name from email
    console.log('Attempting registration with:', {
      name,
      email: email.value,
      password: password.value,
    })

    console.log('Making API call to /auth/register')
    const response = await api.post('/auth/register', {
      name: name,
      email: email.value,
      password: password.value,
      role: 'hr', // Automatic role for HR/Recruiter registration
      phone: '', // Optional phone field
      company_name: '',
      cin: '',
    })

    console.log('Registration successful:', response.data)
    alert('Registration successful! Please login.')
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
.signup-page {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  margin: 0;
  padding: 0;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.signup-container {
  width: 100%;
  height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: #fff;
  margin: 0;
}

/* Left Side - Form Section */
.form-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  position: relative;
}

.form-wrapper {
  width: 100%;
  max-width: 480px;
}

.form-header {
  margin-bottom: 2.5rem;
}

.welcome-text {
  font-size: 0.95rem;
  color: #64748b;
  margin: 0 0 0.5rem 0;
  font-weight: 400;
}

.form-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
  line-height: 1.2;
}

.sign-in-link {
  position: absolute;
  top: 2rem;
  right: 2rem;
}

.signin-btn {
  padding: 0.625rem 1.75rem;
  background: transparent;
  color: #6366f1;
  border: 1.5px solid #6366f1;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  text-decoration: none;
  display: inline-block;
  transition: all 0.3s ease;
}

.signin-btn:hover {
  background: #6366f1;
  color: #fff;
}

.signup-form {
  margin-top: 2rem;
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

.password-input-wrapper {
  position: relative;
}

.password-toggle {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.password-toggle:hover {
  color: #64748b;
}

.error-message {
  padding: 0.75rem 1rem;
  background: #fee2e2;
  color: #dc2626;
  border-radius: 8px;
  font-size: 0.9rem;
  margin-bottom: 1rem;
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

.submit-btn:hover:not(:disabled) {
  background: #4f46e5;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

/* Right Side - Illustration Section */
.illustration-section {
  background: linear-gradient(135deg, #f0f0f5 0%, #e8e8f0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  position: relative;
  overflow: hidden;
}

.illustration-wrapper {
  width: 100%;
  max-width: 500px;
  animation: float 6s ease-in-out infinite;
}

.illustration {
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

/* Responsive Design */
@media (max-width: 968px) {
  .signup-container {
    grid-template-columns: 1fr;
  }

  .illustration-section {
    display: none;
  }

  .sign-in-link {
    position: static;
    text-align: right;
    margin-bottom: 2rem;
  }

  .form-section {
    min-height: 100vh;
  }
}

@media (max-width: 480px) {
  .form-title {
    font-size: 1.75rem;
  }

  .form-section {
    padding: 2rem 1.5rem;
  }
}
</style>
