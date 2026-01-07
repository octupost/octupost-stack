import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

import {
  AgentDetails,
  SessionEntry,
  TeamDetails,
  type ChatMessage,
  type PausedRunState
} from './types/os'

// Maximum number of messages to keep in memory to prevent unbounded growth
const MAX_MESSAGES = 500
// Number of messages to keep when trimming
const TRIM_TO_MESSAGES = 400

interface Store {
  hydrated: boolean
  setHydrated: () => void
  streamingErrorMessage: string
  setStreamingErrorMessage: (streamingErrorMessage: string) => void
  endpoints: {
    endpoint: string
    id__endpoint: string
  }[]
  setEndpoints: (
    endpoints: {
      endpoint: string
      id__endpoint: string
    }[]
  ) => void
  isStreaming: boolean
  setIsStreaming: (isStreaming: boolean) => void
  isEndpointActive: boolean
  setIsEndpointActive: (isActive: boolean) => void
  isEndpointLoading: boolean
  setIsEndpointLoading: (isLoading: boolean) => void
  messages: ChatMessage[]
  setMessages: (
    messages: ChatMessage[] | ((prevMessages: ChatMessage[]) => ChatMessage[])
  ) => void
  chatInputRef: React.RefObject<HTMLTextAreaElement | null>
  selectedEndpoint: string
  setSelectedEndpoint: (selectedEndpoint: string) => void
  authToken: string
  setAuthToken: (authToken: string) => void
  agents: AgentDetails[]
  setAgents: (agents: AgentDetails[]) => void
  teams: TeamDetails[]
  setTeams: (teams: TeamDetails[]) => void
  selectedModel: string
  setSelectedModel: (model: string) => void
  mode: 'agent' | 'team'
  setMode: (mode: 'agent' | 'team') => void
  sessionsData: SessionEntry[] | null
  setSessionsData: (
    sessionsData:
      | SessionEntry[]
      | ((prevSessions: SessionEntry[] | null) => SessionEntry[] | null)
  ) => void
  isSessionsLoading: boolean
  setIsSessionsLoading: (isSessionsLoading: boolean) => void
  addSystemMessage: (content: string) => void
  // Persisted session/team state for page refresh restoration
  lastTeamId: string | null
  setLastTeamId: (id: string | null) => void
  lastDbId: string | null
  setLastDbId: (id: string | null) => void
  lastSessionId: string | null
  setLastSessionId: (id: string | null) => void
  lastTeamTier: string | null
  setLastTeamTier: (tier: string | null) => void
  // Active agent for thinking loader
  activeAgent: string | null
  setActiveAgent: (agent: string | null) => void
  // Abort controller for stopping streaming
  abortController: AbortController | null
  setAbortController: (controller: AbortController | null) => void
  // User ID for memory sharing across teams
  userId: string | null
  setUserId: (userId: string | null) => void
  // HITL paused run state
  pausedRun: PausedRunState | null
  setPausedRun: (pausedRun: PausedRunState | null) => void
  // Credit balance
  creditBalance: number | null
  setCreditBalance: (balance: number | null) => void
  // Message management
  clearMessages: () => void
  // Last message for retry capability
  lastUserMessage: string | null
  setLastUserMessage: (message: string | null) => void
}

export const useStore = create<Store>()(
  persist(
    (set) => ({
      hydrated: false,
      setHydrated: () => set({ hydrated: true }),
      streamingErrorMessage: '',
      setStreamingErrorMessage: (streamingErrorMessage) =>
        set(() => ({ streamingErrorMessage })),
      endpoints: [],
      setEndpoints: (endpoints) => set(() => ({ endpoints })),
      isStreaming: false,
      setIsStreaming: (isStreaming) => set(() => ({ isStreaming })),
      isEndpointActive: false,
      setIsEndpointActive: (isActive) =>
        set(() => ({ isEndpointActive: isActive })),
      isEndpointLoading: true,
      setIsEndpointLoading: (isLoading) =>
        set(() => ({ isEndpointLoading: isLoading })),
      messages: [],
      setMessages: (messages) =>
        set((state) => {
          const newMessages = typeof messages === 'function' ? messages(state.messages) : messages
          // Auto-trim if messages exceed max limit
          if (newMessages.length > MAX_MESSAGES) {
            // Keep the most recent messages
            return { messages: newMessages.slice(-TRIM_TO_MESSAGES) }
          }
          return { messages: newMessages }
        }),
      clearMessages: () => set({ messages: [] }),
      chatInputRef: { current: null },
      selectedEndpoint: 'http://localhost:7777',
      setSelectedEndpoint: (selectedEndpoint) =>
        set(() => ({ selectedEndpoint })),
      authToken: '',
      setAuthToken: (authToken) => set(() => ({ authToken })),
      agents: [],
      setAgents: (agents) => set({ agents }),
      teams: [],
      setTeams: (teams) => set({ teams }),
      selectedModel: '',
      setSelectedModel: (selectedModel) => set(() => ({ selectedModel })),
      mode: 'agent',
      setMode: (mode) => set(() => ({ mode })),
      sessionsData: null,
      setSessionsData: (sessionsData) =>
        set((state) => ({
          sessionsData:
            typeof sessionsData === 'function'
              ? sessionsData(state.sessionsData)
              : sessionsData
        })),
      isSessionsLoading: false,
      setIsSessionsLoading: (isSessionsLoading) =>
        set(() => ({ isSessionsLoading })),
      addSystemMessage: (content) =>
        set((state) => ({
          messages: [
            ...state.messages,
            {
              role: 'system' as const,
              content,
              created_at: Date.now()
            }
          ]
        })),
      // Persisted session/team state for page refresh restoration
      lastTeamId: null,
      setLastTeamId: (id) => set({ lastTeamId: id }),
      lastDbId: null,
      setLastDbId: (id) => set({ lastDbId: id }),
      lastSessionId: null,
      setLastSessionId: (id) => set({ lastSessionId: id }),
      lastTeamTier: null,
      setLastTeamTier: (tier) => set({ lastTeamTier: tier }),
      // Active agent for thinking loader
      activeAgent: null,
      setActiveAgent: (agent) => set({ activeAgent: agent }),
      // Abort controller for stopping streaming
      abortController: null,
      setAbortController: (controller) => set({ abortController: controller }),
      // User ID for memory sharing across teams
      userId: null,
      setUserId: (userId) => set({ userId }),
      // HITL paused run state
      pausedRun: null,
      setPausedRun: (pausedRun) => set({ pausedRun }),
      // Credit balance
      creditBalance: null,
      setCreditBalance: (creditBalance) => set({ creditBalance }),
      // Last message for retry capability
      lastUserMessage: null,
      setLastUserMessage: (lastUserMessage) => set({ lastUserMessage })
    }),
    {
      name: 'endpoint-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        selectedEndpoint: state.selectedEndpoint,
        selectedModel: state.selectedModel,  // Persist selected model like Cursor
        lastTeamId: state.lastTeamId,
        lastDbId: state.lastDbId,
        lastSessionId: state.lastSessionId,
        lastTeamTier: state.lastTeamTier
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHydrated?.()
      }
    }
  )
)
