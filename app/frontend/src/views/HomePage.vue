<template>
  <div class="home-page">
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">Welcome to JobShalah</h1>
        <p class="hero-subtitle">Your Gateway to Smart Recruitment & Career Growth</p>
        <p class="hero-description">
          Connect talented candidates with leading organizations through our intelligent Human
          Resources Management System
        </p>

        <div class="cta-buttons">
          <router-link to="/login" class="cta-btn primary">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
              <polyline points="10 17 15 12 10 7"></polyline>
              <line x1="15" y1="12" x2="3" y2="12"></line>
            </svg>
            Sign In
          </router-link>

          <router-link to="/register/role-selection" class="cta-btn secondary">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="8.5" cy="7" r="4"></circle>
              <line x1="20" y1="8" x2="20" y2="14"></line>
              <line x1="23" y1="11" x2="17" y2="11"></line>
            </svg>
            Register
          </router-link>
        </div>
      </div>

      <div class="hero-illustration">
        <svg viewBox="0 0 700 600" xmlns="http://www.w3.org/2000/svg" class="illustration">
          <!-- Background elements -->
          <circle cx="350" cy="300" r="250" fill="#e8e8f0" opacity="0.4" />
          <circle cx="150" cy="150" r="80" fill="#065eb5" opacity="0.1" />
          <circle cx="580" cy="450" r="100" fill="#FFD700" opacity="0.15" />

          <!-- Main illustration - People at work -->
          <g id="workspace">
            <!-- Desk -->
            <rect x="200" y="380" width="300" height="10" fill="#2d2d44" rx="5" />

            <!-- Person 1 (Recruiter) -->
            <g id="recruiter">
              <circle cx="280" cy="280" r="40" fill="#f4b5a4" />
              <path
                d="M 250 270 Q 250 240 280 235 Q 310 240 310 270 Q 310 280 280 280 Q 250 280 250 270"
                fill="#2d2d44"
              />
              <path
                d="M 280 320 Q 260 325 250 370 L 250 390 L 310 390 L 310 370 Q 300 325 280 320"
                fill="#065eb5"
              />
              <path d="M 280 335 Q 240 345 230 365 L 235 375 Q 250 355 280 350" fill="#f4b5a4" />
              <path d="M 280 335 Q 320 345 330 365 L 325 375 Q 310 355 280 350" fill="#f4b5a4" />
            </g>

            <!-- Laptop -->
            <rect x="320" y="350" width="90" height="60" fill="#065eb5" rx="4" />
            <rect x="325" y="355" width="80" height="45" fill="#4f46e5" rx="2" />

            <!-- Person 2 (Candidate) -->
            <g id="candidate">
              <circle cx="420" cy="290" r="38" fill="#8b6f5c" />
              <path
                d="M 392 280 Q 392 252 420 247 Q 448 252 448 280 Q 448 290 420 290 Q 392 290 392 280"
                fill="#2d2d44"
              />
              <path
                d="M 420 328 Q 400 333 390 375 L 390 390 L 450 390 L 450 375 Q 440 333 420 328"
                fill="#6366f1"
              />
              <path d="M 420 340 Q 380 350 370 375 L 375 385 Q 395 360 420 355" fill="#8b6f5c" />
              <path d="M 420 340 Q 460 350 470 375 L 465 385 Q 445 360 420 355" fill="#8b6f5c" />
            </g>

            <!-- Documents/Resume -->
            <rect
              x="180"
              y="340"
              width="60"
              height="50"
              fill="white"
              stroke="#065eb5"
              stroke-width="2"
              rx="3"
            />
            <line x1="190" y1="355" x2="230" y2="355" stroke="#065eb5" stroke-width="2" />
            <line x1="190" y1="365" x2="230" y2="365" stroke="#065eb5" stroke-width="2" />
            <line x1="190" y1="375" x2="220" y2="375" stroke="#065eb5" stroke-width="2" />

            <!-- Coffee cup -->
            <ellipse cx="530" cy="370" rx="15" ry="5" fill="#2d2d44" />
            <path
              d="M 515 370 L 515 350 Q 515 345 520 345 L 540 345 Q 545 345 545 350 L 545 370"
              fill="#FFD700"
              stroke="#2d2d44"
              stroke-width="2"
            />
          </g>

          <!-- Floating elements -->
          <g id="floating-icons">
            <circle cx="120" cy="400" r="25" fill="#065eb5" opacity="0.8" />
            <path d="M 110 400 L 120 390 L 130 400" stroke="white" stroke-width="2" fill="none" />

            <circle cx="600" cy="200" r="25" fill="#FFD700" opacity="0.8" />
            <text x="590" y="208" font-size="20" fill="white">✓</text>
          </g>
        </svg>
      </div>
    </div>

    <!-- Features Section -->
    <div class="features-section">
      <h2 class="features-title">Why Choose JobShalah?</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
          </div>
          <h3>Smart Matching</h3>
          <p>AI-powered candidate matching for efficient recruitment</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
          </div>
          <h3>Easy Scheduling</h3>
          <p>Streamlined interview booking and management</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
          </div>
          <h3>Real-time Updates</h3>
          <p>Stay informed throughout the hiring process</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// No additional logic needed for now
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8e8f0 100%);
}

/* Hero Section */
.hero-section {
  min-height: 100vh; /* Changed from calc(100vh - 60px) */
  margin-top: 0; /* Changed from 60px */
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  padding: 3rem 5rem;
  align-items: center;
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  color: #1e3a5f;
  line-height: 1.2;
  margin: 0;
  animation: fadeInUp 0.8s ease-out;
}

.hero-subtitle {
  font-size: 1.5rem;
  font-weight: 600;
  color: #065eb5;
  margin: 0;
  animation: fadeInUp 0.8s ease-out 0.2s backwards;
}

.hero-description {
  font-size: 1.1rem;
  color: #64748b;
  line-height: 1.6;
  margin: 0;
  animation: fadeInUp 0.8s ease-out 0.4s backwards;
}

.cta-buttons {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
  animation: fadeInUp 0.8s ease-out 0.6s backwards;
}

.cta-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1.25rem 2rem;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.cta-btn.primary {
  background: #065eb5;
  color: white;
}

.cta-btn.primary:hover {
  background: #054a94;
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(6, 94, 181, 0.4);
}

.cta-btn.secondary {
  background: white;
  color: #065eb5;
  border: 2px solid #065eb5;
}

.cta-btn.secondary:hover {
  background: #065eb5;
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(6, 94, 181, 0.3);
}

.hero-illustration {
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 1s ease-out 0.4s backwards;
}

.illustration {
  width: 100%;
  max-width: 600px;
  height: auto;
  filter: drop-shadow(0 10px 30px rgba(0, 0, 0, 0.1));
  animation: float 6s ease-in-out infinite;
}

/* Features Section */
.features-section {
  padding: 5rem;
  background: white;
}

.features-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e3a5f;
  margin-bottom: 3rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  background: #f8f9fa;
  padding: 2rem;
  border-radius: 16px;
  text-align: center;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
  border-color: #065eb5;
}

.feature-icon {
  width: 70px;
  height: 70px;
  margin: 0 auto 1.5rem;
  background: linear-gradient(135deg, #065eb5 0%, #0a7dd4 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.feature-card h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 1rem 0;
}

.feature-card p {
  font-size: 1rem;
  color: #64748b;
  line-height: 1.6;
  margin: 0;
}

/* Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
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
@media (max-width: 1024px) {
  .hero-section {
    grid-template-columns: 1fr;
    padding: 2rem 3rem;
  }

  .hero-illustration {
    order: -1;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .features-section {
    padding: 3rem 2rem;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 2rem 1.5rem;
  }

  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1.2rem;
  }

  .cta-btn {
    padding: 1rem 1.5rem;
    font-size: 1rem;
  }

  .features-section {
    padding: 2rem 1.5rem;
  }

  .features-title {
    font-size: 2rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>
