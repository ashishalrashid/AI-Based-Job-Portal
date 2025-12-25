<template>
  <div class="role-selection-page">
    <div class="role-selection-container">
      <!-- Header Section -->
      <div class="header-section">
        <div class="breadcrumb">
          <router-link to="/" class="breadcrumb-link">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
            Home
          </router-link>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            class="breadcrumb-separator"
          >
            <path d="M9 18l6-6-6-6"></path>
          </svg>
          <span class="breadcrumb-current">Choose Your Role</span>
        </div>

        <h1 class="page-title">Choose Your Role</h1>
        <p class="page-subtitle">Select how you'd like to use JobShalah</p>
      </div>

      <!-- Role Cards Grid -->
      <div class="roles-grid">
        <!-- Candidate Role Card -->
        <div class="role-card candidate-card" @click="selectRole('applicant')">
          <div class="role-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="48"
              height="48"
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
          </div>
          <h3 class="role-title">I'm a Candidate</h3>
          <p class="role-description">
            Looking for new career opportunities and want to connect with top companies
          </p>
          <div class="role-features">
            <div class="feature">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
              Browse job postings
            </div>
            <div class="feature">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
              Apply for positions
            </div>
            <div class="feature">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
              Schedule interviews
            </div>
          </div>
          <button class="role-button">Continue as Candidate</button>
        </div>

        <!-- Company Role Card -->
        <div class="role-card company-card" @click="selectRole('company')">
          <div class="role-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
          </div>
          <h3 class="role-title">I'm a Company</h3>
          <p class="role-description">
            Organization looking to manage your HR team and recruitment process
          </p>
          <div class="role-features">
            <div class="feature">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
              Manage HR team
            </div>
            <div class="feature">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
              Oversee recruitment
            </div>
            <div class="feature">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
              Analytics & reports
            </div>
          </div>
          <button class="role-button">Continue as Company</button>
        </div>
      </div>

      <!-- Additional Info Section -->
      <div class="info-section">
        <div class="info-content">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            class="info-icon"
          >
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M12 16v-4"></path>
            <path d="M12 8h.01"></path>
          </svg>
          <div class="info-text">
            <h4>Need Help Choosing?</h4>
            <p>
              If you're unsure about your role, you can always change it later in your profile
              settings.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const selectRole = (role) => {
  console.log('🎯 Selected role:', role)

  // Route mapping - HR option removed
  const roleRoutes = {
    applicant: '/applicant-registration',
    company: '/organisation-registration',
  }

  const targetRoute = roleRoutes[role]
  console.log('🚀 Navigating to:', targetRoute)

  router.push(targetRoute)
}
</script>

<style scoped>
/* Update roles-grid for 2 cards instead of 3 */
.roles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

/* Keep all existing styles below this line */
.role-selection-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8e8f0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.role-selection-container {
  width: 100%;
  max-width: 1200px;
}

/* Header Section */
.header-section {
  text-align: center;
  margin-bottom: 3rem;
}

.breadcrumb {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.breadcrumb-link {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #6366f1;
  text-decoration: none;
  transition: color 0.2s;
}

.breadcrumb-link:hover {
  color: #4f46e5;
}

.breadcrumb-separator {
  color: #cbd5e1;
}

.breadcrumb-current {
  color: #64748b;
  font-weight: 500;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.page-subtitle {
  font-size: 1.1rem;
  color: #64748b;
  margin: 0;
}

/* Role Cards Grid */


.role-card {
  background: white;
  border-radius: 20px;
  padding: 2.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 3px solid transparent;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.role-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--card-color-start), var(--card-color-end));
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.role-card:hover::before {
  transform: scaleX(1);
}

.role-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.15);
  border-color: var(--card-color-start);
}

/* Role Card Variants */
.candidate-card {
  --card-color-start: #6366f1;
  --card-color-end: #8b5cf6;
}

.company-card {
  --card-color-start: #f59e0b;
  --card-color-end: #d97706;
}

.role-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1.5rem;
  background: linear-gradient(135deg, var(--card-color-start), var(--card-color-end));
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: transform 0.3s ease;
}

.role-card:hover .role-icon {
  transform: scale(1.1);
}

.role-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 1rem 0;
}

.role-description {
  font-size: 1rem;
  color: #64748b;
  line-height: 1.6;
  margin: 0 0 2rem 0;
}

.role-features {
  margin-bottom: 2rem;
}

.feature {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #475569;
  margin-bottom: 0.75rem;
  justify-content: center;
}

.feature svg {
  color: var(--card-color-start);
  flex-shrink: 0;
}

.role-button {
  width: 100%;
  padding: 1rem 2rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, var(--card-color-start), var(--card-color-end));
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.role-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
}

.role-button:active {
  transform: translateY(0);
}

/* Info Section */
.info-section {
  background: white;
  border-radius: 16px;
  padding: 1.5rem 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.info-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.info-icon {
  color: #6366f1;
  flex-shrink: 0;
}

.info-text h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.info-text p {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .role-selection-page {
    padding: 1rem;
  }

  .page-title {
    font-size: 2rem;
  }

  .roles-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .role-card {
    padding: 2rem;
  }

  .breadcrumb {
    flex-direction: column;
    gap: 0.25rem;
  }

  .breadcrumb-separator {
    transform: rotate(90deg);
  }

  .info-content {
    flex-direction: column;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.75rem;
  }

  .role-card {
    padding: 1.5rem;
  }

  .role-icon {
    width: 60px;
    height: 60px;
  }
}
</style>

