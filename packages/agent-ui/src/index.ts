// Main exports for @octupost/agent-ui

// Video Editor Integration
export { VideoEditorChat } from './components/VideoEditorChat'
export { TeamTierSelector, type TeamTier } from './components/TeamTierSelector'

// Chat components
export { ChatArea } from './components/chat/ChatArea'
export { default as Sidebar } from './components/chat/Sidebar'
export { default as ChatInput } from './components/chat/ChatArea/ChatInput'
export { default as MessageArea } from './components/chat/ChatArea/MessageArea'
export { default as Messages } from './components/chat/ChatArea/Messages'
export { TaskProgress } from './components/chat/TaskProgress'
export { PlanPreview } from './components/chat/PlanPreview'

// Hooks
export { default as useAIChatStreamHandler } from './hooks/useAIStreamHandler'
export { default as useChatActions } from './hooks/useChatActions'
export { default as useSessionLoader } from './hooks/useSessionLoader'
export { default as useAIResponseStream } from './hooks/useAIResponseStream'

// Store
export { useStore } from './store'

// Types
export * from './types/os'

// API
export * from './api/os'
export { APIRoutes } from './api/routes'
