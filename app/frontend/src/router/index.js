import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

// Import components
import DashboardLayout from '../components/DashboardLayout.vue'

// Public pages
import HomePage from '../views/HomePage.vue'
import LoginPage from '../views/LoginPage.vue'
import SignUp from '../views/SignUp.vue'
import ForgotPassword from '../views/ForgotPassword.vue'
import PasswordReset from '../views/PasswordReset.vue'
import RoleSelection from '../views/RoleSelection.vue'

// Applicant views
import ApplicantDashboard from '../views/applicant/ApplicantDashboard.vue'
import ApplicantProfile from '../views/applicant/ApplicantProfile.vue'
import ApplicantRegistration from '../views/applicant/ApplicantRegistration.vue'
import ApplicationsReview from '../views/applicant/ApplicationsReview.vue'
import InterviewSlotBooking from '../views/applicant/InterviewSlotBooking.vue'
import JobPostings from '../views/applicant/JobPostings.vue'
import InterviewSummary from '../views/applicant/InterviewSummary.vue'

// HR views
import CandidatesReview from '../views/hr/CandidatesReview.vue'
import CreateJob from '../views/hr/CreateJob.vue'
import HRAnalytics from '../views/hr/HRAnalytics.vue'
import HRDashboard from '../views/hr/HRDashboard.vue'
import HRProfile from '../views/hr/HRProfile.vue'
import InterviewSlots from '../views/hr/InterviewSlots.vue'
import OfferLetterEditor from '../views/hr/OfferLetterEditor.vue'
import OnboardingTracker from '../views/hr/OnboardingTracker.vue'
import ResumeReview from '../views/hr/ResumeReview.vue'
import ShortlistedCandidates from '../views/hr/ShortlistedCandidates.vue'
import InterviewDetails from '../views/hr/InterviewDetails.vue'
import EligibleCandidates from '../views/hr/EligibleCandidates.vue'

// Organization views
import OrganizationDashboard from '../views/organization/OrganizationDashboard.vue'
import OrganizationRegistration from '../views/organization/OrganizationRegistration.vue'
import Staff from '../views/organization/Staff.vue'

const routes = [
  // Public Routes
  {
    path: '/',
    name: 'home',
    component: HomePage,
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: ForgotPassword,
  },
  {
    path: '/password-reset',
    name: 'password-reset',
    component: PasswordReset,
  },
  {
    path: '/signup',
    name: 'signup',
    component: SignUp,
  },
  {
    path: '/register/role-selection',
    name: 'role-selection',
    component: RoleSelection,
  },
  {
    path: '/applicant-registration',
    component: ApplicantRegistration,
  },
  {
    path: '/organisation-registration',
    component: OrganizationRegistration,
  },

  // Applicant Routes (Protected)
  {
    path: '/applicant',
    component: DashboardLayout,
    meta: { requiresAuth: true, role: 'applicant' },
    children: [
      {
        path: 'dashboard',
        component: ApplicantDashboard,
      },
      {
        path: 'profile',
        component: ApplicantProfile,
      },
      {
        path: 'review-applications',
        component: ApplicationsReview,
      },
      {
        path: 'interview-slots',
        component: InterviewSlotBooking,
      },
      {
        path: 'jobs',
        component: JobPostings,
      },
      {
        path: 'job-details/:id',
        name: 'job-details',
        component: () => import('../views/applicant/JobDetails.vue'),
      },
      {
        path: 'interview-thank-you',
        name: 'InterviewSummary',
        component: InterviewSummary, // or () => import('../views/applicant/InterviewSummary.vue')
      },
    ],
  },

  // Video Interview Route (Without Sidebar)
  {
    path: '/applicant/video-interview/:id',
    name: 'video-interview',
    component: () => import('../views/applicant/VideoInterview.vue'),
    meta: { requiresAuth: true, role: 'applicant' },
  },

  // HR Routes (Protected)
  {
    path: '/hr',
    component: DashboardLayout,
    meta: { requiresAuth: true, role: 'hr' },
    children: [
      {
        path: 'review-candidates',
        component: CandidatesReview,
      },
      {
        path: 'create-job',
        component: CreateJob,
      },
      {
        path: 'analytics',
        component: HRAnalytics,
      },
      {
        path: 'dashboard',
        component: HRDashboard,
      },
      {
        path: 'candidates/:id',
        component: () => import('../views/hr/CandidateProfile.vue'),
      },
      {
        path: 'profile',
        component: HRProfile,
      },
      {
        path: 'interview-slots',
        component: InterviewSlots,
      },
      {
        path: 'interview-details/:interviewId',
        name: 'interview-details',
        component: () => import('@/views/hr/InterviewDetails.vue'),
        props: true,
      },
      {
        path: 'offer-letters',
        component: OfferLetterEditor,
      },
      {
        path: 'eligible-candidates',
        component: EligibleCandidates,
      },
      {
        path: 'onboarding-tracker',
        component: OnboardingTracker,
      },
      {
        path: 'review-resume',
        component: ResumeReview,
      },
      {
        path: 'shortlisted-candidates',
        component: ShortlistedCandidates,
      },
      {
        path: 'offer-letters/create/:candidateId',
        name: 'create-offer-letter',
        component: OfferLetterEditor,
        props: true,
      },
    ],
  },

  // Organization Routes (Protected)
  {
    path: '/organisation',
    component: DashboardLayout,
    meta: { requiresAuth: true, role: ['company', 'admin'] },
    children: [
      {
        path: '/organization/profile',
        name: 'OrganizationProfile',
        component: () => import('@/views/organization/OrganizationProfile.vue'),
      },

      {
        path: 'dashboard',
        component: OrganizationDashboard,
      },
      {
        path: 'staff',
        component: Staff,
      },
      {
        path: 'staff/add',
        component: () => import('../views/organization/AddStaff.vue'),
      },
      {
        path: 'staff/edit/:staffId',
        component: () => import('../views/organization/EditStaff.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Route guard for authentication and authorization
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated']
  const userRole = store.getters['auth/userRole']
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
  const requiredRole = to.matched.find((record) => record.meta.role)?.meta.role

  if (requiresAuth) {
    if (!isAuthenticated) {
      // Not logged in, redirect to login
      next({ name: 'login', query: { redirect: to.fullPath } })
    } else if (requiredRole) {
      // Handle array of roles or single role
      const allowedRoles = Array.isArray(requiredRole) ? requiredRole : [requiredRole]
      if (!allowedRoles.includes(userRole)) {
        // Wrong role, redirect to home
        next({ name: 'home' })
      } else {
        // All checks passed
        next()
      }
    } else {
      // All checks passed
      next()
    }
  } else {
    next()
  }
})

export default router
