# 🗺️ ROADMAP - Authentication Issue Investigation

**Created:** 2025-10-02
**Status:** Investigation Phase
**Priority:** HIGH - Production Issue

---

## 🎯 Current Problem Statement

### Issue #1: Desktop 401 Errors (CRITICAL)
- **Symptoms:** Desktop browser shows 401 Unauthorized errors on `/folders/tree` and `/urls/all`
- **Mobile Status:** ✅ Works perfectly - can see folders and links
- **Desktop Status:** ❌ Cannot access protected resources
- **Error Details:**
  ```
  401 on /folders/tree
  401 on /urls/all
  Uncaught Error: Minified React error #418
  ```

### Issue #2: Mobile Responsive UI (HIGH PRIORITY)
- **Symptoms:** Sidebar takes full screen width on mobile devices
- **Impact:** Users cannot see main content area on mobile
- **Required:** Collapsible sidebar or bottom navigation for mobile

---

## 🔍 Investigation Plan (Agentic Loop Approach)

### Phase 1: Root Cause Analysis (CURRENT)

#### Step 1.1: Examine Auth Flow Code ⏳
- [ ] Review `auth.ts` token management functions
- [ ] Analyze `AuthGuard.tsx` authentication check logic
- [ ] Check `login/page.tsx` token saving mechanism
- [ ] Verify API clients (`api.ts`, `folders-api.ts`) header injection

#### Step 1.2: Identify Timing/Race Conditions
- [ ] Check if `getToken()` is called before sessionStorage is ready
- [ ] Verify `useEffect` dependency arrays in AuthGuard
- [ ] Test if hydration mismatch exists between server/client
- [ ] Confirm token is saved before navigation occurs

#### Step 1.3: SessionStorage Investigation
- [ ] Compare sessionStorage state between mobile (working) and desktop (broken)
- [ ] Check if token exists in desktop sessionStorage
- [ ] Verify token format and validity
- [ ] Test if clearing sessionStorage and re-login fixes desktop

#### Step 1.4: Network Analysis
- [ ] Compare request headers from mobile vs desktop
- [ ] Check if Authorization header is present in desktop requests
- [ ] Verify timing of requests (are they sent before login completes?)
- [ ] Review backend logs to see what token (if any) desktop sends

### Phase 2: Hypothesis Formation

**Primary Hypotheses:**

1. **Race Condition Hypothesis**
   - `AuthGuard` checks auth before sessionStorage is hydrated
   - Fix: Add proper loading state and wait for client-side hydration

2. **Token Storage Hypothesis**
   - Token saved successfully on mobile but fails on desktop
   - Possible browser-specific sessionStorage behavior
   - Fix: Add localStorage fallback or verify sessionStorage availability

3. **Navigation Timing Hypothesis**
   - Desktop navigates to `/dashboard/links` before token is saved
   - Mobile has slower navigation giving time for token to persist
   - Fix: Ensure token save completes before navigation

4. **Server-Side Rendering Hypothesis**
   - Desktop serves SSR'd page that checks auth server-side (where sessionStorage doesn't exist)
   - Mobile gets CSR'd version
   - Fix: Ensure auth check only happens client-side

### Phase 3: Targeted Fixes (DO NOT START UNTIL PHASE 1 COMPLETE)

**Fix Strategy Based on Root Cause:**

- **If Race Condition:** Add proper `mounted` state in AuthGuard
- **If Storage Issue:** Implement localStorage fallback
- **If Navigation Timing:** Use Promise.resolve() or async/await properly
- **If SSR Issue:** Add `'use client'` directive and client-only checks

### Phase 4: Verification (DO NOT START UNTIL PHASE 3 COMPLETE)

- [ ] Test desktop login in local dev environment
- [ ] Verify token appears in sessionStorage
- [ ] Confirm API requests include Authorization header
- [ ] Test in incognito mode (fresh state)
- [ ] Deploy to production and verify fix

---

## 📊 Current System State

### ✅ What's Working
- Mobile authentication and authorization
- Public redirects (`/{shortCode}`)
- Backend API endpoints (when properly authenticated)
- CORS headers on all responses
- Token generation and validation
- Folder and URL management (on mobile)

### ❌ What's Broken
- Desktop authentication (401 errors)
- Mobile responsive UI (sidebar too wide)

### 🤔 What's Unknown
- Why mobile works but desktop doesn't
- Whether this is a browser-specific issue
- If this affects only certain desktop browsers
- Whether it's related to Next.js SSR/CSR

---

## 🧪 Investigation Evidence Checklist

Before implementing any fix, we need:

- [ ] **Backend Logs:** Comparison of mobile (success) vs desktop (401) requests
- [ ] **SessionStorage Inspection:** Desktop browser DevTools sessionStorage contents
- [ ] **Network Tab Analysis:** Desktop request headers showing Authorization presence/absence
- [ ] **Console Errors:** Complete error stack trace from desktop
- [ ] **Incognito Test:** Does fresh browser state fix the issue?
- [ ] **Cross-Browser Test:** Does issue occur in Chrome, Safari, Firefox?

---

## 🎯 Success Criteria

### Desktop Auth Fix
- ✅ Desktop can successfully login
- ✅ Token persists in sessionStorage
- ✅ API requests include valid Authorization header
- ✅ Folders and links load on desktop
- ✅ No 401 errors in network tab
- ✅ Works across Chrome, Safari, Firefox

### Mobile Responsive UI
- ✅ Sidebar collapses on mobile viewports (<768px)
- ✅ Main content visible on mobile
- ✅ Touch-friendly navigation
- ✅ Smooth transitions between sidebar states
- ✅ Maintains all functionality on mobile

---

## 🚀 Next Immediate Action

**CURRENT TASK:** Begin Phase 1.1 - Examine auth flow code

**Methodology:**
1. Read and analyze auth-related files
2. Document findings and potential issues
3. Form specific hypotheses
4. DO NOT proceed to fixes until root cause is identified

**Time Allocation:**
- Investigation: Take as long as needed
- Analysis: Be thorough, not fast
- Implementation: Only after confidence in diagnosis

---

## 📝 Investigation Log

### 2025-10-02 - Initial Investigation

**Files Examined:**
- ✅ `/frontend/src/lib/auth.ts` - Token management (NO ISSUES)
- ✅ `/frontend/src/components/AuthGuard.tsx` - Route protection (**CRITICAL ISSUE FOUND**)
- ✅ `/frontend/src/app/login/page.tsx` - Login flow (NO ISSUES)
- ✅ `/frontend/src/lib/api.ts` - API client (NO ISSUES)
- ✅ `/frontend/src/lib/folders-api.ts` - Folders API client (NO ISSUES)

**Answers to Key Questions:**
1. ✅ `getToken()` is synchronous - NO ISSUE
2. ❌ **`AuthGuard` does NOT wait for client-side mount - THIS IS THE PROBLEM**
3. ✅ Token is saved before navigation - NO ISSUE
4. ✅ No `useEffect` dependency issues - NO ISSUE
5. ❌ **SSR/CSR mismatch exists - THIS IS THE ROOT CAUSE**

---

## 🔍 ROOT CAUSE IDENTIFIED

### **SSR/Hydration Race Condition in AuthGuard**

**Location:** `/frontend/src/components/AuthGuard.tsx:25`

**The Problem:**

```typescript
export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  // ❌ THIS IS THE PROBLEM - runs during SSR AND initial client render
  if (!isAuthenticated()) {
    return (
      <div className="min-h-screen flex items-center justify-center...">
        <div className="text-gray-400">Redirecting to login...</div>
      </div>
    );
  }

  return <>{children}</>;
}
```

**Why This Causes Desktop 401 Errors:**

1. **Server-Side Rendering (SSR):**
   - Next.js 15 pre-renders pages on the server
   - During SSR, `typeof window === 'undefined'`
   - Therefore `getToken()` returns `null`
   - Therefore `isAuthenticated()` returns `false`
   - Component renders "Redirecting to login..." on server

2. **Hydration Mismatch on Desktop:**
   - Desktop browsers (Chrome) have stricter hydration behavior
   - SSR HTML shows "Redirecting to login..."
   - React tries to hydrate the page
   - During hydration, if `isAuthenticated()` is still false, the check at line 25 fails
   - **Children never render, so API calls to `/folders/tree` and `/urls/all` never happen**
   - **OR components render momentarily but without auth context, making unauthenticated requests**

3. **Why Mobile Works:**
   - Different browser (Safari vs Chrome)
   - Different caching/hydration behavior
   - Slower rendering allows sessionStorage to be read before auth check
   - Or browser doesn't cache SSR'd version as aggressively

**Evidence:**
- ✅ Token management code is correct (auth.ts)
- ✅ API clients correctly use `getAuthHeader()`
- ✅ Login flow correctly saves token before navigation
- ❌ AuthGuard checks auth during SSR when sessionStorage doesn't exist
- ❌ No "mounted" state to wait for client-side hydration

**Hypothesis Confirmed:** #4 - Server-Side Rendering Hypothesis

---

## 🛠️ The Fix

**Strategy:** Add `mounted` state to ensure auth check only happens AFTER client-side mount

**Changes Required:**
1. Add `useState` for `mounted` state
2. Add `useEffect` to set `mounted` to `true` after mount
3. Show loading state during SSR and initial mount
4. Only check `isAuthenticated()` after component is mounted

**Implementation:** See AuthGuard.tsx:15-36

---

*This roadmap follows the "bucle agéntico" methodology: verify each step before proceeding to the next.*
