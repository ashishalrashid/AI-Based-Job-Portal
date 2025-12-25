<template>
  <div class="hr-profile-page">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">My Profile</h1>
      <button class="edit-mode-btn" @click="toggleEditMode" v-if="!isEditMode">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
        </svg>
        Edit Profile
      </button>
      <div v-else class="edit-mode-actions">
        <button class="btn-save" @click="saveProfile">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          Save
        </button>
        <button class="btn-cancel" @click="cancelEdit">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
          Cancel
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-grid">
      <!-- Left Section -->
      <div class="left-section">
        <!-- Profile Picture Card -->
        <div class="card profile-picture-card">
          <div class="profile-avatar">
            <img
              v-if="profileData.profileImage"
              :src="profileData.profileImage"
              :alt="profileData.firstName"
            />
            <div v-else class="avatar-placeholder">
              {{ profileData.firstName.charAt(0) }}{{ profileData.lastName.charAt(0) }}
            </div>
          </div>
          <div class="profile-actions">
            <button class="btn-small-primary" v-if="isEditMode" @click="uploadPhoto">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
              </svg>
              Upload Photo
            </button>
            <input
              type="file"
              ref="photoInput"
              @change="handlePhotoChange"
              accept="image/*"
              style="display: none"
            />
            <p class="photo-hint">JPG, PNG (Max 5MB) - Editable</p>
          </div>
        </div>

        <!-- Editable Contact Information Card -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Editable Information</h2>
            <span class="editable-badge">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
              Can Edit
            </span>
          </div>
          <div class="form-group">
            <label class="form-label">
              Phone Number
              <span class="editable-indicator">✓ Editable</span>
            </label>
            <input
              v-model="profileData.phone"
              type="tel"
              class="form-input"
              :disabled="!isEditMode"
              placeholder="Enter phone number"
            />
          </div>
          <div class="form-group">
            <label class="form-label">
              LinkedIn Profile
              <span class="editable-indicator">✓ Editable</span>
            </label>
            <input
              v-model="profileData.linkedin"
              type="url"
              class="form-input"
              :disabled="!isEditMode"
              placeholder="https://linkedin.com/in/yourprofile"
            />
          </div>
        </div>
      </div>

      <!-- Right Section -->
      <div class="right-section">
        <!-- Personal Information Card -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Personal Information</h2>
            <span class="locked-badge">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
              </svg>
              Admin Only
            </span>
          </div>
          <div class="form-group">
            <label class="form-label">
              First Name
              <span class="locked-indicator">🔒 Locked</span>
            </label>
            <input
              v-model="profileData.firstName"
              type="text"
              class="form-input locked"
              disabled
              placeholder="Enter first name"
            />
          </div>
          <div class="form-group">
            <label class="form-label">
              Last Name
              <span class="locked-indicator">🔒 Locked</span>
            </label>
            <input
              v-model="profileData.lastName"
              type="text"
              class="form-input locked"
              disabled
              placeholder="Enter last name"
            />
          </div>
          <div class="form-group">
            <label class="form-label">
              Email Address
              <span class="locked-indicator">🔒 Locked</span>
            </label>
            <input
              v-model="profileData.email"
              type="email"
              class="form-input locked"
              disabled
              placeholder="Enter email"
            />
            <p class="email-hint">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
              Email cannot be changed. Contact admin for changes.
            </p>
          </div>
          <div class="form-group">
            <label class="form-label">
              Employee ID
              <span class="locked-indicator">🔒 Locked</span>
            </label>
            <input
              v-model="profileData.employeeId"
              type="text"
              class="form-input locked"
              disabled
              placeholder="Employee ID"
            />
          </div>
        </div>

        <!-- Professional Details Card -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Professional Details</h2>
            <span class="locked-badge">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
              </svg>
              Admin Only
            </span>
          </div>
          <div class="form-group">
            <label class="form-label">
              Job Title
              <span class="locked-indicator">🔒 Locked</span>
            </label>
            <input
              v-model="profileData.jobTitle"
              type="text"
              class="form-input locked"
              disabled
              placeholder="Enter job title"
            />
          </div>
          <div class="form-group">
            <label class="form-label">
              Department
              <span class="locked-indicator">🔒 Locked</span>
            </label>
            <input
              v-model="profileData.department"
              type="text"
              class="form-input locked"
              disabled
              placeholder="Enter department"
            />
          </div>
          <div class="form-group">
            <label class="form-label">
              Office Location
              <span class="locked-indicator">🔒 Locked</span>
            </label>
            <input
              v-model="profileData.office"
              type="text"
              class="form-input locked"
              disabled
              placeholder="Enter office location"
            />
          </div>
          <div class="form-group">
            <label class="form-label">
              Years of Experience
              <span class="locked-indicator">🔒 Locked</span>
            </label>
            <input
              v-model="profileData.experience"
              type="number"
              class="form-input locked"
              disabled
              placeholder="Enter years"
              min="0"
            />
          </div>
          <div class="form-group">
            <label class="form-label">
              Specialization
              <span class="locked-indicator">🔒 Locked</span>
            </label>
            <textarea
              v-model="profileData.specialization"
              class="form-textarea locked"
              disabled
              placeholder="Describe your specialization areas"
            ></textarea>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import api from '@/services/api'

const store = useStore()

// State
const isEditMode = ref(false)
const photoInput = ref(null)
const loading = ref(false)

// Get HR user from store/localStorage
const hrUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
const hrId = hrUser?.hr_id

const profileData = ref({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  employeeId: '',
  department: '',
  office: '',
  profileImage: null,
  profileImageFile: null, // Store file for upload
  linkedin: '',
  jobTitle: '',
  experience: 0,
  specialization: '',
})

// Store original values for cancel
const originalData = ref({})

// Fetch HR profile data
const fetchProfile = async () => {
  if (!hrId) {
    console.error('HR ID not found')
    return
  }

  loading.value = true
  try {
    const res = await api.get(`/hr/${hrId}`)
    const hr = res.data

    profileData.value = {
      firstName: hr.first_name || '',
      lastName: hr.last_name || '',
      email: hr.contact_email || '',
      phone: hr.contact_phone || '',
      employeeId: hr.staff_id || '',
      department: '', // Not in HR model
      office: '', // Not in HR model
      profileImage: null, // Will be loaded from backend if photo URL exists
      profileImageFile: null,
      linkedin: hr.linkedin_url || '',
      jobTitle: '', // Not in HR model
      experience: 0, // Not in HR model
      specialization: '', // Not in HR model
    }

    originalData.value = JSON.parse(JSON.stringify(profileData.value))
  } catch (err) {
    console.error('Failed to fetch HR profile:', err)
    alert('Failed to load profile data')
  } finally {
    loading.value = false
  }
}

// Methods
const toggleEditMode = () => {
  isEditMode.value = true
  originalData.value = JSON.parse(JSON.stringify(profileData.value))
}

const saveProfile = async () => {
  if (!hrId) {
    alert('HR ID not found')
    return
  }

  loading.value = true
  try {
    const formData = new FormData()
    
    // Only send editable fields
    if (profileData.value.phone) {
      formData.append('phone', profileData.value.phone)
    }
    // Note: HRProfile model doesn't have linkedin_url field
    // If needed, this can be added to the model later
    
    // Add profile photo if uploaded
    if (profileData.value.profileImageFile instanceof File) {
      formData.append('profile_photo', profileData.value.profileImageFile)
    }

    await api.put(`/hr/${hrId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    alert('Profile updated successfully!')
    isEditMode.value = false
    
    // Reload profile to get updated data
    await fetchProfile()
  } catch (err) {
    console.error('Failed to save profile:', err)
    alert(err.response?.data?.message || 'Failed to update profile')
  } finally {
    loading.value = false
  }
}

const cancelEdit = () => {
  // Restore original values
  profileData.value = JSON.parse(JSON.stringify(originalData.value))
  isEditMode.value = false
}

const uploadPhoto = () => {
  photoInput.value.click()
}

const handlePhotoChange = (event) => {
  const file = event.target.files[0]
  if (!file) return

  // Validate file size
  if (file.size > 5 * 1024 * 1024) {
    alert('File size must be less than 5MB')
    return
  }

  // Validate file type
  if (!file.type.startsWith('image/')) {
    alert('Please select an image file')
    return
  }

  // Store file for upload
  profileData.value.profileImageFile = file

  // Preview the image
  const reader = new FileReader()
  reader.onload = (e) => {
    profileData.value.profileImage = e.target.result
  }
  reader.readAsDataURL(file)
}

onMounted(fetchProfile)
</script>

<style scoped>
.hr-profile-page {
  background: #f5f7fa;
  min-height: 100vh;
  padding: 2rem 1.5rem;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.edit-mode-btn,
.edit-mode-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.edit-mode-btn {
  padding: 0.75rem 1.5rem;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.edit-mode-btn:hover {
  background: #4f46e5;
  transform: translateY(-2px);
}

.btn-save,
.btn-cancel {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-save {
  background: #10b981;
  color: white;
}

.btn-save:hover {
  background: #059669;
}

.btn-cancel {
  background: #ef4444;
  color: white;
}

.btn-cancel:hover {
  background: #dc2626;
}

/* Main Grid */
.main-grid {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.left-section,
.right-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Card */
.card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.editable-badge,
.locked-badge {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.editable-badge {
  background: #dcfce7;
  color: #16a34a;
}

.locked-badge {
  background: #fee2e2;
  color: #dc2626;
}

.editable-indicator {
  font-size: 0.75rem;
  color: #16a34a;
  font-weight: 600;
  margin-left: 0.5rem;
}

.locked-indicator {
  font-size: 0.75rem;
  color: #dc2626;
  font-weight: 600;
  margin-left: 0.5rem;
}

/* Profile Picture Card */
.profile-picture-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  border: 2px solid #10b981;
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
}

.profile-avatar {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: #dbeafe;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border: 4px solid white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 3rem;
  font-weight: 700;
  color: #6366f1;
}

.profile-actions {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
}

.photo-hint {
  font-size: 0.8rem;
  color: #16a34a;
  margin: 0;
  font-weight: 600;
}

/* Form Elements */
.form-group {
  margin-bottom: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e3a5f;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.form-input,
.form-textarea {
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
  font-family: inherit;
  color: #1e3a5f;
  background: white;
  transition: all 0.2s;
}

.form-input:not(:disabled):not(.locked):focus,
.form-textarea:not(:disabled):not(.locked):focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.form-input.locked,
.form-textarea.locked {
  background: #fef2f2;
  color: #991b1b;
  cursor: not-allowed;
  border-color: #fecaca;
}

.form-textarea {
  min-height: 100px;
  resize: vertical;
}

.email-hint {
  font-size: 0.8rem;
  color: #dc2626;
  margin: 0;
  font-style: italic;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  background: #fef2f2;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  border-left: 3px solid #dc2626;
}

/* Buttons */
.btn-small-primary {
  padding: 0.6rem 1rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-small-primary:hover {
  background: #059669;
  transform: translateY(-2px);
}

/* Responsive */
@media (max-width: 1024px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .hr-profile-page {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .edit-mode-btn,
  .edit-mode-actions {
    width: 100%;
  }

  .btn-save,
  .btn-cancel {
    flex: 1;
    justify-content: center;
  }

  .card {
    padding: 1rem;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
}

@media (max-width: 480px) {
  .hr-profile-page {
    padding: 0.75rem;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .profile-avatar {
    width: 120px;
    height: 120px;
  }

  .avatar-placeholder {
    font-size: 2.5rem;
  }
}
</style>
