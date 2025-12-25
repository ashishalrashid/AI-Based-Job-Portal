<template> 
  <div class="login-page">
    <div class="login-container">
      <!-- Left Side - Login Form -->
      <div class="login-form-section">
      <div class="sign-up-link">
          <router-link to="register/role-selection" class="signup-btn"> Register </router-link>
        </div>
        <div class="form-wrapper">
          <div class="form-header">
            <p class="welcome-text">Welcome back!!</p>
            <h1 class="form-title">Please Sign In</h1>
          </div>

          <!-- Error Message -->
          <div v-if="authError" class="error-alert">
            {{ authError }}
          </div>

          <form @submit.prevent="handleLogin" class="login-form">
            <div class="form-group">
              <label for="email" class="form-label">Email address</label>
              <input
                type="email"
                id="email"
                v-model="email"
                placeholder="Enter your email address"
                class="form-input"
                required
              />
            </div>

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
                    ></path>
                    <line x1="1" y1="1" x2="23" y2="23"></line>
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
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                </button>
              </div>
            </div>

            <div class="form-options">
              <label class="remember-me">
                <input type="checkbox" v-model="rememberMe" />
                <span>Remember me</span>
              </label>
              <router-link to="/forgot-password" class="forgot-password">
                I forgot my password
              </router-link>
            </div>

            <button type="submit" class="submit-btn" :disabled="isLoading">
              {{ isLoading ? 'Signing In...' : 'Sign In' }}
            </button>
          </form>
        </div>
      </div>

      <!-- Right Side - Illustration -->
      <div class="illustration-section">
        <div class="illustration-wrapper">
          <svg viewBox="0 0 600 600" xmlns="http://www.w3.org/2000/svg" class="login-illustration">
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
              <!-- Laptop -->
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
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'

const router = useRouter()
const route = useRoute()
const store = useStore()

const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const showPassword = ref(false)
const isLoading = computed(() => store.getters['auth/isLoading'])
const authError = computed(() => store.getters['auth/authError'])

const togglePassword = () => {
  showPassword.value = !showPassword.value
}

const handleLogin = async () => {
  try {
    console.log('🔐 Starting login process...', { email: email.value })

    const result = await store.dispatch('auth/loginUser', {
      email: email.value,
      password: password.value,
    })

    console.log('📋 Login result:', result)

    if (result.success) {
      console.log('✅ Login successful!')

      const dashboardRoutes = {
        applicant: '/applicant/dashboard',
        hr: '/hr/dashboard',
        company: '/organisation/dashboard',
      }

      const userRole = store.getters['auth/userRole']
      console.log('👤 User role:', userRole)

      const redirect = route.query.redirect || dashboardRoutes[userRole]
      console.log('🚀 Redirecting to:', redirect)

      router.push(redirect)
    } else {
      console.error('❌ Login failed:', result.error)
      // The error will be displayed automatically via authError computed property
    }
  } catch (error) {
    console.error('❌ Login exception:', error)
  }
}
</script>

<style scoped>
.login-page {
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

.login-container {
  width: 100%;
  height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: #fff;
  margin: 0;
}

/* Left Side - Form Section */
.login-form-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  position: relative;
  overflow-y: auto;
}

.form-wrapper {
  width: 100%;
  max-width: 420px;
}

.form-header {
  margin-bottom: 2rem;
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

/* Error Alert */
.error-alert {
  background: #fee2e2;
  color: #dc2626;
  padding: 0.875rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  border-left: 4px solid #dc2626;
}

.login-form {
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

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 1.25rem 0 2rem 0;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #475569;
  cursor: pointer;
  user-select: none;
}

.remember-me input[type='checkbox'] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #6366f1;
}

.forgot-password {
  font-size: 0.9rem;
  color: #6366f1;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.forgot-password:hover {
  color: #4f46e5;
  text-decoration: underline;
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

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

/* Responsive Design */
@media (max-width: 968px) {
  .login-container {
    grid-template-columns: 1fr;
  }

  .illustration-section {
    display: none;
  }

  .login-form-section {
    min-height: 100vh;
  }
}

@media (max-width: 480px) {
  .form-title {
    font-size: 1.75rem;
  }

  .login-form-section {
    padding: 2rem 1.5rem;
  }
}

.sign-up-link {
  position: absolute;
  top: 2rem;
  right: 2rem;
}

.signup-btn {
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

.signup-btn:hover {
  background: #6366f1;
  color: #fff;
}

/* ... existing styles ... */

/* UPDATE: Responsive Design Media Query */
@media (max-width: 968px) {
  .login-container {
    grid-template-columns: 1fr;
  }

  .illustration-section {
    display: none;
  }

  .login-form-section {
    min-height: 100vh;
    /* Ensure relative positioning for the button logic */
    display: block; 
  }
  
  /* NEW: Adjust button position on mobile */
  .sign-up-link {
    position: static;
    text-align: right;
    margin-bottom: 2rem;
    padding-top: 2rem; /* Add some spacing from top */
    padding-right: 2rem;
  }
  
  /* Center the form wrapper when display is block */
  .form-wrapper {
    margin: 0 auto;
  }
}
</style>
