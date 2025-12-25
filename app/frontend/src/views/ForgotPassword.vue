<template>
  <div class="forgot-password-page">
    <div class="forgot-password-container">
      <!-- Left Side - Form -->
      <div class="form-section">
        <div class="form-wrapper">
          <div class="form-header">
            <p class="subtitle">Password recovery.</p>
            <h1 class="title">Forgot your password?</h1>
            <p class="description">
              Kindly enter the email address linked to this account and we will send you a code to
              enable you change your password.
            </p>
          </div>

          <form @submit.prevent="handleSubmit" class="recovery-form">
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

            <button type="submit" class="submit-btn" :disabled="isLoading">
              {{ isLoading ? 'Sending...' : 'Send' }}
            </button>

            <div class="back-to-login">
              <router-link to="/login" class="back-link"> ← Back to Sign In </router-link>
            </div>
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const email = ref('')
const isLoading = ref(false)

const handleSubmit = async () => {
  isLoading.value = true

  // Simulate API call
  setTimeout(() => {
    console.log('Password recovery email sent to:', email.value)
    isLoading.value = false

    // Redirect to password reset page
    router.push('/password-reset')
  }, 2000)
}
</script>

<style scoped>
.forgot-password-page {
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

.forgot-password-container {
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
}

.form-wrapper {
  width: 100%;
  max-width: 480px;
}

.form-header {
  margin-bottom: 2.5rem;
}

.subtitle {
  font-size: 0.95rem;
  color: #64748b;
  margin: 0 0 0.5rem 0;
  font-weight: 400;
}

.title {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 1rem 0;
  line-height: 1.2;
}

.description {
  font-size: 0.95rem;
  color: #64748b;
  line-height: 1.6;
  margin: 0;
}

.recovery-form {
  margin-top: 2rem;
}

.form-group {
  margin-bottom: 2rem;
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
  margin-bottom: 1.5rem;
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

.back-to-login {
  text-align: center;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  color: #6366f1;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
  padding: 0.5rem;
}

.back-link:hover {
  color: #4f46e5;
  transform: translateX(-4px);
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
  .forgot-password-container {
    grid-template-columns: 1fr;
  }

  .illustration-section {
    display: none;
  }

  .form-section {
    min-height: 100vh;
  }
}

@media (max-width: 480px) {
  .title {
    font-size: 1.75rem;
  }

  .form-section {
    padding: 2rem 1.5rem;
  }
}
</style>
