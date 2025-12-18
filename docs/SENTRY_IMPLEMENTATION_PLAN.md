# Sentry Logging Implementation Plan

This document outlines all locations in the `octupost` codebase where Sentry logging should be added for better error tracking, performance monitoring, and debugging visibility.

---

## Current State

Sentry is configured with basic automatic error capturing:
- `sentry.client.config.ts` - Client-side with Replay integration
- `sentry.server.config.ts` - Server-side basic config
- `instrumentation.ts` - Request error capturing via `Sentry.captureRequestError`

**Missing:** No manual `Sentry.captureException`, `Sentry.captureMessage`, `Sentry.addBreadcrumb`, or `Sentry.startSpan` calls exist. All error logging uses `console.error`.

---

## Priority Levels

| Priority | Description | Impact |
|----------|-------------|--------|
| **CRITICAL** | Authentication failures, data mutations, onboarding | User cannot access app or loses data |
| **HIGH** | API failures, database errors, generation failures | Core features broken |
| **MEDIUM** | Data fetching errors, context failures | Degraded experience |
| **LOW** | UI component errors, non-critical features | Minor inconvenience |

---

## CRITICAL Priority

### 1. Authentication Flow (`app/auth/`)

| File | Line | Current | Recommended |
|------|------|---------|-------------|
| `callback/route.ts` | 17-19 | `console.error("Auth callback error:", error.message)` | `Sentry.captureException(error, { tags: { flow: 'oauth' } })` |
| `callback/route.ts` | 47-49 | `console.error("OTP verification error:", error.message)` | `Sentry.captureException(error, { tags: { flow: 'otp', type } })` |
| `sign-in/page.tsx` | 59-62 | Catch block with no logging | `Sentry.captureException(err, { tags: { action: 'sign-in' } })` |
| `sign-up/page.tsx` | 48 | Catch block with no logging | `Sentry.captureException(err, { tags: { action: 'sign-up' } })` |
| `forgot-password/page.tsx` | 37 | Catch block with no logging | `Sentry.captureException(err, { tags: { action: 'forgot-password' } })` |
| `reset-password/page.tsx` | 64 | Catch block with no logging | `Sentry.captureException(err, { tags: { action: 'reset-password' } })` |
| `signout/route.ts` | - | No error handling for `signOut()` | Add try/catch with `Sentry.captureException` |

### 2. Onboarding Flow (`app/onboarding/actions.ts`)

| Line | Current | Recommended |
|------|---------|-------------|
| 22 | `return { error: "Not authenticated" }` | `Sentry.captureMessage("Onboarding: unauthenticated user", { level: 'warning' })` |
| 35-37 | `console.error("Profile update error:", profileError)` | `Sentry.captureException(profileError, { tags: { step: 'profile-update' } })` |
| 53-55 | `console.error("Workspace creation error:", workspaceError)` | `Sentry.captureException(workspaceError, { tags: { step: 'workspace-create' } })` |
| 68-70 | `console.error("Member creation error:", memberError)` | `Sentry.captureException(memberError, { tags: { step: 'member-add' } })` |
| 83-85 | `console.error("Onboarding completion error:", completeError)` | `Sentry.captureException(completeError, { tags: { step: 'complete' } })` |

### 3. Workspace Mutations (`lib/actions/workspace-settings-actions.ts`)

| Line | Current | Recommended |
|------|---------|-------------|
| 72-73 | `console.error("[updateWorkspaceAction] Error:", updateError)` | `Sentry.captureException(updateError, { extra: { workspaceId } })` |
| 127-128 | `console.error("[deleteWorkspaceAction] Error deleting members:", membersError)` | `Sentry.captureException(membersError, { extra: { workspaceId } })` |
| 139-140 | `console.error("[deleteWorkspaceAction] Error deleting projects:", projectsError)` | `Sentry.captureException(projectsError, { extra: { workspaceId } })` |
| 151-152 | `console.error("[deleteWorkspaceAction] Error:", deleteError)` | `Sentry.captureException(deleteError, { extra: { workspaceId } })` |

### 4. Workspace Creation (`lib/actions/workspace-actions.ts`)

| Line | Current | Recommended |
|------|---------|-------------|
| 51-52 | `console.error("[createWorkspaceAction] Error creating workspace:", workspaceError)` | `Sentry.captureException(workspaceError, { extra: { name } })` |
| 66-67 | `console.error("[createWorkspaceAction] Error adding owner member:", memberError)` | `Sentry.captureException(memberError, { extra: { workspaceId: workspace.id } })` |

---

## HIGH Priority

### 5. API Client (`lib/api/client.ts`)

| Line | Current | Recommended |
|------|---------|-------------|
| 115 | `throw new Error("API base URL is not configured...")` | Add breadcrumb before throw: `Sentry.addBreadcrumb({ category: 'api', message: 'Missing API config' })` |
| 129-131 | Catch block throws network error | `Sentry.captureException(err, { tags: { type: 'network' }, extra: { url } })` |
| 136 | `throw new Error(error.message \|\| HTTP ${response.status})` | `Sentry.captureException(new Error(...), { extra: { status: response.status, url } })` |
| 237 | `throw new Error("Job polling timeout exceeded")` | `Sentry.captureMessage("Job polling timeout", { level: 'error', extra: { jobId, timeout } })` |

### 6. Generation Hooks (`lib/api/hooks.ts`)

| Line | Current | Recommended |
|------|---------|-------------|
| 119-128 | Catch block calls `options.onError` | Add `Sentry.captureException(err, { tags: { type: 'generation' } })` |
| 155-158 | `console.error("Failed to cancel job:", err)` | `Sentry.captureException(err, { extra: { jobId: state.jobId } })` |
| 259-260 | Catch block sets error state | `Sentry.captureException(err, { tags: { hook: 'useJobStatus' } })` |

### 7. Asset Mutations (`lib/data/assets.ts`)

| Line | Current | Recommended |
|------|---------|-------------|
| 187-188 | `console.error("[assignAssetToProject] Error assigning asset:", error)` | `Sentry.captureException(error, { extra: { assetId, projectId } })` |
| 221-222 | `console.error("[removeAssetFromProject] Error removing asset:", error)` | `Sentry.captureException(error, { extra: { assetId, projectId } })` |
| 389-390 | `console.error("[deleteAsset] Error soft-deleting asset:", assetError)` | `Sentry.captureException(assetError, { extra: { assetId } })` |
| 402-403 | `console.error("[deleteAsset] Error deleting project_assets:", projectAssetsError)` | `Sentry.captureException(projectAssetsError, { extra: { assetId } })` |
| 415-416 | `console.error("[deleteAsset] Error deleting workplace_assets:", workplaceAssetsError)` | `Sentry.captureException(workplaceAssetsError, { extra: { assetId } })` |

### 8. Project Mutations (`lib/actions/project-actions.ts`)

| Line | Current | Recommended |
|------|---------|-------------|
| 164-165 | `console.error("[deleteProjectAction] Error:", deleteError)` | `Sentry.captureException(deleteError, { extra: { projectId } })` |
| 204-205 | `console.error("[assignProjectToWorkspace] Error:", error)` | `Sentry.captureException(error, { extra: { projectId, workplaceId } })` |
| 239-240 | `console.error("[removeProjectFromWorkspace] Error:", error)` | `Sentry.captureException(error, { extra: { projectId, workplaceId } })` |

### 9. User Profile Updates (`lib/actions/user-actions.ts`)

| Line | Current | Recommended |
|------|---------|-------------|
| 84-85 | `console.error("[updateUserProfileAction] Error updating profile:", updateError)` | `Sentry.captureException(updateError)` |

### 10. Playground Generators (`components/playground/`)

| File | Line | Current | Recommended |
|------|------|---------|-------------|
| `image-generator.tsx` | 58-59 | `console.error("Image generation failed:", err)` | `Sentry.captureException(err, { tags: { generator: 'image' } })` |
| `video-generator.tsx` | 162-163 | `console.error("Video generation failed:", err)` | `Sentry.captureException(err, { tags: { generator: 'video' } })` |
| `video-generator.tsx` | 201-202 | `console.error("Image-to-video generation failed:", err)` | `Sentry.captureException(err, { tags: { generator: 'image-to-video' } })` |
| `speech-generator.tsx` | 56-57 | `console.error("Speech generation failed:", err)` | `Sentry.captureException(err, { tags: { generator: 'speech' } })` |

---

## MEDIUM Priority

### 11. Data Fetching - Assets (`lib/data/assets.ts`)

| Line | Current | Recommended |
|------|---------|-------------|
| 64 | `console.error("[getAssets] User not authenticated:", userError)` | `Sentry.addBreadcrumb({ category: 'auth', message: 'Unauthenticated getAssets' })` |
| 87 | `console.error("[getAssets] Error fetching assets:", error)` | `Sentry.captureException(error, { tags: { query: 'getAssets' } })` |
| 118 | `console.error("[getAssetsByProject] User not authenticated:", userError)` | Breadcrumb |
| 133 | `console.error("[getAssetsByProject] Error fetching project assets:", error)` | `Sentry.captureException(error, { extra: { projectId } })` |
| 241 | `console.error("[getAssetProjects] User not authenticated:", userError)` | Breadcrumb |
| 257 | `console.error("[getAssetProjects] Error fetching asset projects:", error)` | `Sentry.captureException(error, { extra: { assetId } })` |
| 284 | `console.error("[getAssetsByWorkspace] User not authenticated:", userError)` | Breadcrumb |
| 303 | `console.error("[getAssetsByWorkspace] Error fetching workplace assets:", error)` | `Sentry.captureException(error, { extra: { workspaceId } })` |
| 334 | `console.error("[getAsset] User not authenticated:", userError)` | Breadcrumb |
| 350 | `console.error("[getAsset] Error fetching asset:", error)` | `Sentry.captureException(error, { extra: { assetId: id } })` |

### 12. Data Fetching - Projects (`lib/data/projects.ts`)

| Line | Current | Recommended |
|------|---------|-------------|
| 58 | `console.error("[getProjects] User not authenticated:", userError)` | Breadcrumb |
| 71 | `console.error("[getProjects] Error fetching projects:", error)` | `Sentry.captureException(error)` |
| 91 | `console.error("[getProject] User not authenticated:", userError)` | Breadcrumb |
| 108 | `console.error("[getProject] Error fetching project:", error)` | `Sentry.captureException(error, { extra: { projectId: id } })` |
| 128 | `console.error("[deleteProject] Error deleting project:", error)` | `Sentry.captureException(error, { extra: { projectId: id } })` |

### 13. Data Fetching - Workspaces (`lib/data/workspaces.ts`)

| Line | Current | Recommended |
|------|---------|-------------|
| 62 | `console.error("[getWorkspaces] User not authenticated:", userError)` | Breadcrumb |
| 74 | `console.error("[getWorkspaces] Error fetching memberships:", memberError)` | `Sentry.captureException(memberError)` |
| 93 | `console.error("[getWorkspaces] Error fetching workspaces:", workspaceError)` | `Sentry.captureException(workspaceError)` |
| 105 | `console.error("[getWorkspaces] Error fetching member counts:", countError)` | `Sentry.captureException(countError)` |
| 132 | `console.error("[createWorkspace] User not authenticated:", userError)` | Breadcrumb |
| 148 | `console.error("[createWorkspace] Error creating workspace:", workspaceError)` | `Sentry.captureException(workspaceError)` |
| 163 | `console.error("[createWorkspace] Error adding owner member:", memberError)` | `Sentry.captureException(memberError)` |
| 184 | `console.error("[getWorkspace] Error fetching workspace:", error)` | `Sentry.captureException(error, { extra: { workspaceId: id } })` |

### 14. Server Actions - Projects (`lib/actions/project-actions.ts`)

| Line | Current | Recommended |
|------|---------|-------------|
| 58 | `console.error("[getProjectsByWorkspace] User not authenticated:", userError)` | Breadcrumb |
| 74 | `console.error("[getProjectsByWorkspace] Error fetching workplace projects:", error)` | `Sentry.captureException(error, { extra: { workplaceId } })` |
| 99 | `console.error("[getProject] User not authenticated:", userError)` | Breadcrumb |
| 115 | `console.error("[getProject] Error fetching project:", error)` | `Sentry.captureException(error, { extra: { projectId: id } })` |
| 261 | `console.error("[getWorkspacesByProject] User not authenticated:", userError)` | Breadcrumb |
| 273 | `console.error("[getWorkspacesByProject] Error:", error)` | `Sentry.captureException(error, { extra: { projectId } })` |

### 15. Context Providers (`lib/contexts/`)

| File | Line | Current | Recommended |
|------|------|---------|-------------|
| `user-context.tsx` | 39-40 | `console.error("[UserContext] Failed to fetch user:", error)` | `Sentry.captureException(error, { tags: { context: 'user' } })` |
| `workspace-context.tsx` | 135-136 | `console.error("[WorkspaceContext] Failed to fetch workspaces:", error)` | `Sentry.captureException(error, { tags: { context: 'workspace' } })` |

---

## LOW Priority

### 16. UI Components

| File | Line | Current | Recommended |
|------|------|---------|-------------|
| `asset-picker-modal.tsx` | 76-77 | `console.error("[AssetPickerModal] Failed to fetch assets:", error)` | `Sentry.captureException(error, { tags: { component: 'asset-picker' } })` |
| `add-to-project-dropdown.tsx` | 75-76 | `console.error("Failed to fetch projects:", err)` | `Sentry.captureException(err, { tags: { component: 'add-to-project' } })` |
| `assign-project-modal.tsx` | 87-88 | Catch block sets error state | Optional: Add breadcrumb |
| `assign-project-modal.tsx` | 123-124 | Catch block sets error state | Optional: Add breadcrumb |
| `settings/profile-tab.tsx` | 25, 27-28 | `console.error("Failed to save profile:", ...)` | `Sentry.captureException(error)` |
| `new-project-modal.tsx` | 95 | Catch block with no logging | Optional: Add breadcrumb |

### 17. Page Components (`app/(app)/`)

| File | Line | Current | Recommended |
|------|------|---------|-------------|
| `dashboard/page.tsx` | 37-38 | `console.error("Failed to fetch projects:", error)` | `Sentry.captureException(error, { tags: { page: 'dashboard' } })` |
| `projects/page.tsx` | 30-31 | `console.error("Failed to fetch projects:", error)` | `Sentry.captureException(error, { tags: { page: 'projects' } })` |
| `projects/[id]/project-assets-client.tsx` | 92, 94-95 | `console.error(...)` | `Sentry.captureException(error)` |
| `assets/assets-page-client.tsx` | 116, 118-119 | `console.error("Error deleting asset:", error)` | `Sentry.captureException(error)` |

---

## Missing Error Boundaries

**No React Error Boundaries exist in the codebase.** Consider adding:

1. **Root Error Boundary** in `app/layout.tsx` to catch rendering errors
2. **Feature Error Boundaries** around:
   - Playground generators
   - Dashboard widgets
   - Project detail views

---

## Additional Recommendations

### 1. User Context
Add user context to Sentry when user authenticates:

```typescript
// In auth callback or context provider
Sentry.setUser({
  id: user.id,
  email: user.email,
})
```

### 2. Performance Monitoring
Add transaction spans for critical operations:

```typescript
// Example for generation
const transaction = Sentry.startSpan({ name: "generate-image" })
// ... generation code
transaction.end()
```

### 3. Breadcrumbs for User Actions
Add breadcrumbs for important user actions:

```typescript
Sentry.addBreadcrumb({
  category: "user-action",
  message: "User started image generation",
  data: { model, prompt_length: prompt.length },
})
```

---

## Summary Statistics

| Category | Count |
|----------|-------|
| CRITICAL locations | 17 |
| HIGH locations | 21 |
| MEDIUM locations | 23 |
| LOW locations | 12 |
| **Total locations** | **73** |

| File Type | Count |
|-----------|-------|
| Server Actions | 6 files |
| Data Layer | 3 files |
| API Client | 2 files |
| Auth Routes | 5 files |
| Contexts | 2 files |
| Components | 10+ files |

---

## Implementation Order

1. **Week 1**: CRITICAL - Auth flows, onboarding, workspace mutations
2. **Week 2**: HIGH - API client, generation hooks, asset/project mutations
3. **Week 3**: MEDIUM - Data fetching layer, context providers
4. **Week 4**: LOW - UI components, error boundaries


