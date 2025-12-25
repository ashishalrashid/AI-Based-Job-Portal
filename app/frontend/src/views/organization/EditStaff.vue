<template>
  <div class="edit-staff-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="icon-wrapper">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
        </div>
        <div class="header-info">
          <h1 class="page-title">Edit Profile</h1>
          <p class="page-subtitle">Edit HR details</p>
        </div>
      </div>
    </div>

    <!-- Back Button -->
    <router-link to="/organisation/staff" class="back-button">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <line x1="19" y1="12" x2="5" y2="12"></line>
        <polyline points="12 19 5 12 12 5"></polyline>
      </svg>
      <span>Back</span>
    </router-link>

    <!-- Form Section -->
    <div class="form-container">
      <div class="form-wrapper">
        <!-- Photo Section -->
        <div class="photo-section">
          <div class="photo-upload">
            <img
              v-if="photoPreview"
              :src="photoPreview"
              :alt="formData.firstName"
              class="profile-photo"
            />
            <div v-else class="photo-placeholder">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="48"
                height="48"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.5"
              >
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
            </div>
            <p class="photo-text">Update Photo</p>
            <input
              type="file"
              ref="photoInput"
              @change="handlePhotoUpload"
              accept="image/*"
              class="photo-input"
            />
          </div>
          <div class="photo-info">
            <p class="info-title">Allowed format</p>
            <p class="info-text">JPG, JPEG, and PNG</p>
            <p class="info-title">Max file size</p>
            <p class="info-text">2MB</p>
          </div>
        </div>

        <!-- Form Fields -->
        <div class="form-fields">
          <h2 class="form-title">HR Profile</h2>

          <!-- Row 1: First Name & Last Name -->
          <div class="form-row">
            <div class="form-group">
              <label for="firstName" class="form-label">First name</label>
              <input
                type="text"
                id="firstName"
                v-model="formData.firstName"
                placeholder="John"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label for="lastName" class="form-label">Last name</label>
              <input
                type="text"
                id="lastName"
                v-model="formData.lastName"
                placeholder="Doe"
                class="form-input"
              />
            </div>
          </div>

          <!-- Row 2: Email & Phone -->
          <div class="form-row">
            <div class="form-group">
              <label for="email" class="form-label">Email address</label>
              <input
                type="email"
                id="email"
                v-model="formData.email"
                placeholder="xyz@email.com"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label for="phone" class="form-label">Phone number</label>
              <input
                type="tel"
                id="phone"
                v-model="formData.phone"
                placeholder="XXXXXXXXXXX"
                class="form-input"
              />
            </div>
          </div>

          <!-- Row 3: Gender & Status -->
          <div class="form-row">
            <div class="form-group">
              <label for="gender" class="form-label">Gender</label>
              <select id="gender" v-model="formData.gender" class="form-select">
                <option value="">Select gender</option>
                <option value="Male">MALE</option>
                <option value="Female">FEMALE</option>
                <option value="Other">OTHER</option>
              </select>
            </div>
            <div class="form-group">
              <label for="accessToJobshala" class="form-label">Access to Jobshala</label>
              <select id="accessToJobshala" v-model="formData.accessToJobshala" class="form-select">
                <option value="">Select</option>
                <option value="Yes">Yes</option>
                <option value="No">No</option>
              </select>
            </div>
          </div>
          <div class="form-group"></div>
          <div class="form-group"></div>
          <br />
          <br />

          <!-- Submit Button -->
          <button class="submit-btn" @click="handleSaveStaff">Save Changes</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'
import api from '@/services/api'

const router = useRouter()
const route = useRoute()
const store = useStore()
const photoInput = ref(null)
const photoPreview = ref(null)

const formData = ref({
  id: null,
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  gender: '',
  accessToJobshala: '', // new dropdown field (Yes / No)
  photo: null,
})

onMounted(async () => {
  // Get staff ID from route params
  const staffId = route.params.staffId

  if (staffId) {
    try {
      const res = await api.get(`/hr/${staffId}`)
      const hr = res.data
      
      formData.value = {
        id: hr.hr_id || hr.id,
        firstName: hr.first_name || '',
        lastName: hr.last_name || '',
        email: hr.contact_email || hr.email || '',
        phone: hr.contact_phone || hr.phone || '',
        gender: hr.gender || '',
        accessToJobshala: '', // This field doesn't exist in backend
        photo: null,
      }
    } catch (error) {
      console.error('Failed to load HR:', error)
      alert('Failed to load HR details')
    }
  }
})

const handlePhotoUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    formData.value.photo = file

    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      photoPreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const handleSaveStaff = async () => {
  try {
    const staffId = route.params.staffId
    
    if (!staffId) {
      alert('Staff ID not found')
      return
    }

    const payload = {
      first_name: formData.value.firstName,
      last_name: formData.value.lastName,
      email: formData.value.email,
      phone: formData.value.phone,
      gender: formData.value.gender
    }

    await api.put(`/hr/${staffId}`, payload)
    
    alert('HR updated successfully!')
    router.push('/organisation/staff')
  } catch (error) {
    console.error('Failed to update HR:', error)
    const errorMsg = error.response?.data?.message || error.message || 'Failed to update HR'
    alert(errorMsg)
  }
}
</script>

<style scoped>
.edit-staff-page {
  padding: 2rem;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.icon-wrapper {
  width: 48px;
  height: 48px;
  background: #065eb5;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.page-subtitle {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0;
}

/* Back Button */
.back-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #065eb5;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 2rem;
  transition: all 0.2s;
  padding: 0.5rem 0;
}

.back-button:hover {
  gap: 0.75rem;
  color: #054a94;
}

/* Form Container */
.form-container {
  max-width: 1200px;
  margin: 0 auto;
}

.form-wrapper {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 3rem;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* Photo Section */
.photo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
}

.photo-upload {
  width: 100%;
  aspect-ratio: 1;
  border: 2px dashed #cbd5e1;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #c0d4e8;
  position: relative;
  overflow: hidden;
}

.photo-upload:hover {
  border-color: #065eb5;
  background: #b0c5dc;
}

.profile-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.photo-text {
  font-size: 0.95rem;
  color: white;
  margin: 0.5rem 0 0 0;
  font-weight: 500;
  position: absolute;
}

.photo-input {
  display: none;
}

.photo-info {
  width: 100%;
  text-align: center;
}

.info-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0.75rem 0 0.25rem 0;
}

.info-text {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0;
}

/* Form Fields */
.form-fields {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.form-row:has(> .form-group:only-child) {
  grid-template-columns: 1fr;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e3a5f;
}

.form-input,
.form-select {
  padding: 0.875rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  background: white;
  color: #1e3a5f;
  outline: none;
  transition: all 0.2s;
}

.form-input::placeholder,
.form-select::placeholder {
  color: #cbd5e1;
}

.form-input:focus,
.form-select:focus {
  border-color: #065eb5;
  box-shadow: 0 0 0 3px rgba(6, 94, 181, 0.1);
}

.form-input:disabled {
  background: #f9fafb;
  color: #94a3b8;
  cursor: not-allowed;
}

.form-select {
  cursor: pointer;
}

.submit-btn {
  padding: 1rem;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 1rem;
}

.submit-btn:hover {
  background: #4f46e5;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

/* Responsive */
@media (max-width: 1024px) {
  .form-wrapper {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .photo-section {
    max-width: 300px;
  }
}

@media (max-width: 768px) {
  .edit-staff-page {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .form-wrapper {
    padding: 1.5rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
