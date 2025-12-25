<template>
  <div class="applicant-profile">
    <!-- Header -->
    <div class="profile-header">
      <h1 class="page-title">My Profile</h1>
      <div class="header-actions">
        <button v-if="!isEditMode" class="btn-primary" @click="enableEdit">
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
        <template v-else>
          <button class="btn-secondary" @click="cancelEdit">Cancel</button>
          <button class="btn-primary" @click="saveProfile">Save Changes</button>
        </template>
      </div>
    </div>

    <!-- Profile Grid -->
    <div class="profile-grid">
      <!-- Left Column -->
      <div class="left-column">
        <!-- Profile Card -->
        <div class="profile-card card">
          <div class="profile-picture-section">
            <div class="picture-wrapper">
              <img
                v-if="profileData.profilePicture"
                :src="profileData.profilePicture"
                alt="Profile Picture"
                class="profile-image"
              />
              <div v-else class="profile-placeholder">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="64"
                  height="64"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                >
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
              </div>
            </div>
            <div v-if="isEditMode" class="picture-actions">
              <label class="btn-upload">
                <input
                  type="file"
                  accept="image/*"
                  style="display: none"
                  @change="handlePictureUpload"
                />
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
                Upload
              </label>
              <button
                v-if="profileData.profilePicture"
                class="btn-remove"
                @click="removeProfilePicture"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path
                    d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
                  ></path>
                </svg>
              </button>
            </div>

            <!-- Name Display/Edit -->
            <div class="profile-name-section">
              <template v-if="!isEditMode">
                <h2 class="display-name">{{ profileData.firstName }} {{ profileData.lastName }}</h2>
              </template>
              <template v-else>
                <div class="name-edit-grid">
                  <div class="form-group">
                    <label class="form-label">First Name</label>
                    <input
                      v-model="profileData.firstName"
                      type="text"
                      class="form-input"
                      placeholder="First Name"
                    />
                  </div>
                  <div class="form-group">
                    <label class="form-label">Last Name</label>
                    <input
                      v-model="profileData.lastName"
                      type="text"
                      class="form-input"
                      placeholder="Last Name"
                    />
                  </div>
                </div>
              </template>
            </div>
          </div>

          <div class="contact-info">
            <div class="form-group">
              <label class="form-label">Email</label>
              <input
                v-model="profileData.email"
                type="email"
                class="form-input"
                :disabled="!isEditMode"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Phone</label>
              <input
                v-model="profileData.phone"
                type="tel"
                class="form-input"
                :disabled="!isEditMode"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Location</label>
              <input
                v-model="profileData.location"
                type="text"
                class="form-input"
                :disabled="!isEditMode"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Bio</label>
              <textarea
                v-model="profileData.bio"
                class="form-textarea"
                :disabled="!isEditMode"
                rows="4"
                placeholder="Tell us about yourself..."
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Skills Card -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Skills</h2>
          </div>
          <div v-if="isEditMode" class="skill-input-group">
            <input
              v-model="newSkill"
              type="text"
              class="form-input"
              placeholder="Add a skill and press Enter"
              @keyup.enter="addSkill"
            />
          </div>
          <div v-if="profileData.skills.length > 0" class="skills-list">
            <div v-for="(skill, index) in profileData.skills" :key="index" class="skill-tag">
              <span>{{ skill }}</span>
              <button v-if="isEditMode" class="skill-remove" @click="removeSkill(index)">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>No skills added yet</p>
          </div>
        </div>

        <!-- Resumes Card -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Resumes</h2>
          </div>
          <div v-if="isEditMode" class="form-group">
            <input
              type="file"
              class="form-input"
              accept=".pdf,.doc,.docx"
              multiple
              @change="handleResumeUpload"
            />
            <p class="input-hint">You can upload multiple files (PDF, DOC, DOCX)</p>
          </div>
          <div v-if="profileData.resumes.length > 0" class="resume-list">
            <div v-for="(resume, index) in profileData.resumes" :key="index" class="resume-item">
              <div class="file-info">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <span>{{ resume }}</span>
              </div>
              <button v-if="isEditMode" class="btn-remove-file" @click="removeResume(index)">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>No resumes uploaded yet</p>
          </div>
        </div>
      </div>

      <!-- Right Column -->
      <div class="right-column">
        <!-- Experience Card -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Work Experience</h2>
            <button v-if="isEditMode" class="btn-add" @click="addExperience">+ Add</button>
          </div>
          <div v-if="profileData.experience.length > 0" class="experience-list">
            <div
              v-for="(exp, index) in profileData.experience"
              :key="index"
              class="experience-item"
            >
              <div class="form-group">
                <label class="form-label">Company</label>
                <input
                  v-model="exp.company"
                  type="text"
                  class="form-input"
                  :disabled="!isEditMode"
                />
              </div>
              <div class="form-group">
                <label class="form-label">Position</label>
                <input
                  v-model="exp.position"
                  type="text"
                  class="form-input"
                  :disabled="!isEditMode"
                />
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">Start Date</label>
                  <input
                    v-model="exp.startDate"
                    type="date"
                    class="form-input"
                    :disabled="!isEditMode"
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">End Date</label>
                  <input
                    v-model="exp.endDate"
                    type="date"
                    class="form-input"
                    :disabled="!isEditMode"
                  />
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Description</label>
                <textarea
                  v-model="exp.description"
                  class="form-textarea"
                  :disabled="!isEditMode"
                  rows="3"
                ></textarea>
              </div>
              <button v-if="isEditMode" class="btn-remove-item" @click="removeExperience(index)">
                Remove
              </button>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>No work experience added</p>
          </div>
        </div>

        <!-- Education Card -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Education</h2>
            <button v-if="isEditMode" class="btn-add" @click="addEducation">+ Add</button>
          </div>
          <div v-if="profileData.education.length > 0" class="education-list">
            <div v-for="(edu, index) in profileData.education" :key="index" class="education-item">
              <div class="form-group">
                <label class="form-label">School/University</label>
                <input
                  v-model="edu.school"
                  type="text"
                  class="form-input"
                  :disabled="!isEditMode"
                />
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">Degree</label>
                  <input
                    v-model="edu.degree"
                    type="text"
                    class="form-input"
                    :disabled="!isEditMode"
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">Field</label>
                  <input
                    v-model="edu.field"
                    type="text"
                    class="form-input"
                    :disabled="!isEditMode"
                  />
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">Grade/Score</label>
                  <input
                    v-model="edu.grade"
                    type="text"
                    class="form-input"
                    :disabled="!isEditMode"
                    placeholder="e.g., 8.5 or 85%"
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">Out of / Type</label>
                  <input
                    v-model="edu.gradeType"
                    type="text"
                    class="form-input"
                    :disabled="!isEditMode"
                    placeholder="e.g., 10 CGPA"
                  />
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">Start Date</label>
                  <input
                    v-model="edu.startDate"
                    type="date"
                    class="form-input"
                    :disabled="!isEditMode"
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">End Date</label>
                  <input
                    v-model="edu.endDate"
                    type="date"
                    class="form-input"
                    :disabled="!isEditMode"
                  />
                </div>
              </div>
              <button v-if="isEditMode" class="btn-remove-item" @click="removeEducation(index)">
                Remove
              </button>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>No education added</p>
          </div>
        </div>

        <!-- Certificates Card -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Certificates</h2>
            <button v-if="isEditMode" class="btn-add" @click="addCertificate">+ Add</button>
          </div>
          <div v-if="profileData.certificates.length > 0" class="certificate-list">
            <div
              v-for="(cert, index) in profileData.certificates"
              :key="index"
              class="certificate-item"
            >
              <div class="form-group">
                <label class="form-label">Certificate Name</label>
                <input v-model="cert.name" type="text" class="form-input" :disabled="!isEditMode" />
              </div>
              <div class="form-group">
                <label class="form-label">Issuing Organization</label>
                <input
                  v-model="cert.issuer"
                  type="text"
                  class="form-input"
                  :disabled="!isEditMode"
                />
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">Issue Date</label>
                  <input
                    v-model="cert.issueDate"
                    type="date"
                    class="form-input"
                    :disabled="!isEditMode"
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">Expiry Date</label>
                  <input
                    v-model="cert.expiryDate"
                    type="date"
                    class="form-input"
                    :disabled="!isEditMode"
                  />
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Credential ID (Optional)</label>
                <input
                  v-model="cert.credentialId"
                  type="text"
                  class="form-input"
                  :disabled="!isEditMode"
                />
              </div>
              <div class="form-group">
                <label class="form-label">Credential URL (Optional)</label>
                <input
                  v-model="cert.credentialUrl"
                  type="url"
                  class="form-input"
                  :disabled="!isEditMode"
                />
              </div>
              <button v-if="isEditMode" class="btn-remove-item" @click="removeCertificate(index)">
                Remove
              </button>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>No certificates added</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import api from '@/services/api'

const store = useStore()

const isEditMode = ref(false)
const newSkill = ref(null)

const profileData = ref({
  profilePicture: null,
  firstName: null,
  lastName: null,
  email: null,
  phone: null,
  location: null,
  bio: null,
  skills: [],
  experience: [],
  education: [],
  certificates: [],
  resumeFile: null,             // FILE
  coverLetterFile: null,        // FILE
  profilePictureFile: null,     // FILE for profile photo upload
  resumes: []
})

let originalProfileData = ref(null)

const transformBackendToUI = (data) => {
  const p = data.personal_info || {}
  
  // Split name properly, handling null/undefined
  let firstName = null
  let lastName = null
  if (p.name && p.name !== "null" && typeof p.name === "string") {
    const nameParts = p.name.trim().split(/\s+/)
    firstName = nameParts[0] || null
    lastName = nameParts.slice(1).join(' ') || null
  }

  return {
    profilePicture: null,
    firstName: firstName,
    lastName: lastName,
    email: p.email || null,
    phone: p.phone || null,
    location: p.location || null,
    bio: p.bio || null,

    skills: data.skills?.length ? data.skills : [],

    experience: data.work_experience?.length
      ? data.work_experience.map((e) => ({
          company: e.company || null,
          position: e.position || null,
          startDate: e.start_date || null,
          endDate: e.end_date || null,
          description: e.description || null
        }))
      : [],

    education: data.education?.length
      ? data.education.map((ed) => ({
          school: ed.university || null,
          degree: ed.degree || null,
          field: ed.field || null,
          grade: ed.grade || null,
          gradeType: ed.grade_out_of || null,
          startDate: ed.start_date || null,
          endDate: ed.end_date || null
        }))
      : [],

    certificates: data.certifications?.length
      ? data.certifications.map((c) => ({
          name: c.certificate_name || null,
          issuer: c.issuing_organization || null,
          issueDate: c.issue_date || null,
          expiryDate: c.expiry_date || null,
          credentialId: c.credential_id || null,
          credentialUrl: c.credential_url || null
        }))
      : [],

    resumes: data.resume?.filename ? [data.resume.filename] : [],
    resumeFile: null,
    coverLetterFile: null
  }
}

onMounted(async () => {
  await store.dispatch('applicant/fetchProfile')

  if (store.getters['applicant/profile']) {
    profileData.value = transformBackendToUI(store.getters['applicant/profile'])
  }
})

const enableEdit = () => {
  originalProfileData.value = JSON.parse(JSON.stringify(profileData.value))
  isEditMode.value = true
}

const cancelEdit = () => {
  profileData.value = JSON.parse(JSON.stringify(originalProfileData.value))
  isEditMode.value = false
}


const saveProfile = async () => {
  try {
    const formData = new FormData()

    const s = (v) => (v ? v : "")

    // Fix name construction to avoid "null" in name
    const firstName = (profileData.value.firstName && profileData.value.firstName !== "null") ? profileData.value.firstName : ""
    const lastName = (profileData.value.lastName && profileData.value.lastName !== "null") ? profileData.value.lastName : ""
    const fullName = `${firstName} ${lastName}`.trim() || firstName || lastName || ""
    formData.append("name", fullName)
    
    formData.append("address", s(profileData.value.location))
    formData.append("highest_qualification", s(profileData.value.education[0]?.degree))
    formData.append("institution_name", s(profileData.value.education[0]?.school))

    // graduation_year → only append if valid
    const gy = profileData.value.education[0]?.endDate
    if (gy) {
      const year = new Date(gy).getFullYear()
      if (!isNaN(year)) {
        formData.append("graduation_year", year)
      }
    }

    formData.append("skills", s(profileData.value.skills.join(",")))
    formData.append("preferred_location", s(profileData.value.location))

    // years_of_experience → only append if > 0
    const yoe = profileData.value.experience.length
    if (yoe > 0) {
      formData.append("years_of_experience", yoe)
    }

    formData.append("current_job_title", s(profileData.value.experience[0]?.position))
    formData.append("linkedin_url", s(profileData.value.linkedin))
    formData.append("github_url", s(profileData.value.github))
    formData.append("portfolio_url", s(profileData.value.portfolio))
    formData.append("phone", s(profileData.value.phone))
    formData.append("email", s(profileData.value.email))
    formData.append("bio", s(profileData.value.bio))

    if (profileData.value.resumeFile instanceof File) {
      formData.append("resume", profileData.value.resumeFile)
    }

    if (profileData.value.coverLetterFile instanceof File) {
      formData.append("cover_letter", profileData.value.coverLetterFile)
    }

    // Add profile photo if uploaded
    if (profileData.value.profilePictureFile instanceof File) {
      formData.append("profile_photo", profileData.value.profilePictureFile)
    }

    await store.dispatch("applicant/updateProfile", formData)

    // Save work experiences separately - delete existing first, then add new ones
    const user = store.getters['auth/currentUser']
    if (user && user.applicant_id && profileData.value.experience) {
      try {
        // Delete all existing experiences
        await api.delete(`/applicant/${user.applicant_id}/experiences`)
        
        // Add new experiences
        for (const exp of profileData.value.experience) {
          if (exp.company || exp.position) {
            try {
              await api.post(`/applicant/${user.applicant_id}/experiences`, {
                company: exp.company || "",
                position: exp.position || "",
                start_date: exp.startDate || null,
                end_date: exp.endDate || null,
                description: exp.description || ""
              })
            } catch (err) {
              console.warn("Failed to save experience:", err)
            }
          }
        }
      } catch (err) {
        console.warn("Failed to delete existing experiences:", err)
      }
    }

    // Save education separately - delete existing first, then add new ones
    if (user && user.applicant_id && profileData.value.education) {
      try {
        // Delete all existing education
        await api.delete(`/applicant/${user.applicant_id}/education`)
        
        // Add new education
        for (const edu of profileData.value.education) {
          if (edu.school || edu.degree) {
            try {
              await api.post(`/applicant/${user.applicant_id}/education`, {
                university: edu.school || "",
                degree: edu.degree || "",
                field: edu.field || "",
                grade: edu.grade || "",
                grade_out_of: edu.gradeType || "",
                start_date: edu.startDate || null,
                end_date: edu.endDate || null
              })
            } catch (err) {
              console.warn("Failed to save education:", err)
            }
          }
        }
      } catch (err) {
        console.warn("Failed to delete existing education:", err)
      }
    }

    // Save certifications separately - delete existing first, then add new ones
    if (user && user.applicant_id && profileData.value.certificates) {
      try {
        // Delete all existing certifications
        await api.delete(`/applicant/${user.applicant_id}/certifications`)
        
        // Add new certifications
        for (const cert of profileData.value.certificates) {
          if (cert.name || cert.issuer) {
            try {
              await api.post(`/applicant/${user.applicant_id}/certifications`, {
                certificate_name: cert.name || "",
                issuing_organization: cert.issuer || "",
                issue_date: cert.issueDate || null,
                expiry_date: cert.expiryDate || null,
                credential_id: cert.credentialId || "",
                credential_url: cert.credentialUrl || ""
              })
            } catch (err) {
              console.warn("Failed to save certification:", err)
            }
          }
        }
      } catch (err) {
        console.warn("Failed to delete existing certifications:", err)
      }
    }

    alert("Profile saved successfully!")
    isEditMode.value = false

    // Reload profile to get updated data
    await store.dispatch('applicant/fetchProfile')
    if (store.getters['applicant/profile']) {
      profileData.value = transformBackendToUI(store.getters['applicant/profile'])
    }

  } catch (error) {
    console.error("Save failed", error)
    alert("Failed to save profile")
  }
}





/* ============================
   FILE HANDLERS
   ============================ */

const handlePictureUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return

  // Validate file size (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    alert('File size must be less than 5MB')
    return
  }

  // Validate file type
  if (!file.type.startsWith('image/')) {
    alert('Please select an image file')
    return
  }

  // Store the file for upload
  profileData.value.profilePictureFile = file

  // Preview the image
  const reader = new FileReader()
  reader.onload = (e) => {
    profileData.value.profilePicture = e.target.result
  }
  reader.readAsDataURL(file)
}

const removeProfilePicture = () => {
  profileData.value.profilePicture = null
}

const handleResumeUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  profileData.value.resumeFile = file
  profileData.value.resumes = [file.name]
}

const handleCoverLetterUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  profileData.value.coverLetterFile = file
}

/* ======================================================
   SKILLS / EXPERIENCE / EDUCATION / CERTS (no change)
   ====================================================== */

const addSkill = () => {
  if (newSkill.value.trim() && !profileData.value.skills.includes(newSkill.value.trim())) {
    profileData.value.skills.push(newSkill.value.trim())
    newSkill.value = null
  }
}

const removeSkill = (index) => {
  profileData.value.skills.splice(index, 1)
}

const addExperience = () => {
  profileData.value.experience.push({
    company: null,
    position: null,
    startDate: null,
    endDate: null,
    description: null
  })
}

const removeExperience = (index) => {
  profileData.value.experience.splice(index, 1)
}

const addEducation = () => {
  profileData.value.education.push({
    school: null,
    degree: null,
    field: null,
    grade: null,
    gradeType: null,
    startDate: null,
    endDate: null
  })
}

const removeEducation = (index) => {
  profileData.value.education.splice(index, 1)
}

const addCertificate = () => {
  profileData.value.certificates.push({
    name: null,
    issuer: null,
    issueDate: null,
    expiryDate: null,
    credentialId: null,
    credentialUrl: null
  })
}

const removeCertificate = (index) => {
  profileData.value.certificates.splice(index, 1)
}
</script>


<style scoped>
/* Base Styles */
.applicant-profile {
  padding: 2rem;
  background: #f5f7fa;
  min-height: 100vh;
}

/* Header */
.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.btn-primary,
.btn-secondary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #6366f1;
  color: white;
}

.btn-primary:hover {
  background: #4f46e5;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-secondary {
  background: #e5e7eb;
  color: #1e3a5f;
}

.btn-secondary:hover {
  background: #d1d5db;
}

/* Grid Layout */
.profile-grid {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 2rem;
}

.left-column,
.right-column {
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
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0;
}

/* Profile Card */
.profile-card {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.profile-picture-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.picture-wrapper {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid #e5e7eb;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-placeholder {
  color: white;
}

.picture-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-upload,
.btn-remove {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-upload {
  background: #6366f1;
  color: white;
}

.btn-upload:hover {
  background: #4f46e5;
}

.btn-remove {
  background: #ef4444;
  color: white;
}

.btn-remove:hover {
  background: #dc2626;
}

/* Name Section - NEW IMPROVED STYLES */
.profile-name-section {
  width: 100%;
  text-align: center;
}

.display-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.name-edit-grid {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Forms */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #475569;
}

.form-input,
.form-textarea {
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.2s;
  background: white;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  border-color: #6366f1;
  outline: none;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-input:disabled,
.form-textarea:disabled {
  background: #f8f9fa;
  cursor: not-allowed;
}

.form-textarea {
  resize: vertical;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.input-hint {
  font-size: 0.8rem;
  color: #94a3b8;
  margin-top: 0.25rem;
  margin-bottom: 0;
}

/* Skills */
.skill-input-group {
  margin-bottom: 1.5rem;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.skill-tag {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #eff6ff;
  color: #1e40af;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
}

.skill-remove {
  background: none;
  border: none;
  color: #1e40af;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.skill-remove:hover {
  color: #1e3a8a;
}

/* Resume List */
.resume-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.resume-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #475569;
  min-width: 0;
  flex: 1;
}

.file-info span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-info svg {
  color: #6366f1;
  flex-shrink: 0;
}

.btn-remove-file {
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  border-radius: 4px;
  flex-shrink: 0;
}

.btn-remove-file:hover {
  background: #fee2e2;
}

/* Experience, Education, Certificates */
.experience-list,
.education-list,
.certificate-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.experience-item,
.education-item,
.certificate-item {
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn-add {
  padding: 0.5rem 1rem;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add:hover {
  background: #4f46e5;
}

.btn-remove-item {
  padding: 0.5rem 1rem;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  align-self: flex-start;
}

.btn-remove-item:hover {
  background: #dc2626;
}

/* Empty State */
.empty-state {
  padding: 2rem 1rem;
  text-align: center;
  color: #94a3b8;
  font-size: 0.9rem;
}

/* Responsive */
@media (max-width: 1200px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .applicant-profile {
    padding: 1rem;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .header-actions {
    width: 100%;
  }

  .btn-primary,
  .btn-secondary {
    flex: 1;
  }
}

@media (max-width: 480px) {
  .card {
    padding: 1rem;
  }

  .card-title {
    font-size: 1rem;
  }

  .experience-item,
  .education-item,
  .certificate-item {
    padding: 1rem;
  }

  .display-name {
    font-size: 1.25rem;
  }
}
</style>
