import { useEffect, useCallback, useState } from 'react'
import { useStore } from '../store'

interface UseCreditBalanceOptions {
  /** Refresh interval in ms (default: 30000 = 30s) */
  refreshInterval?: number
  /** Whether to auto-refresh (default: true) */
  autoRefresh?: boolean
  /** Pause polling when tab is not visible (default: true) */
  pauseOnHidden?: boolean
}

/**
 * Hook to fetch and manage the user's credit balance.
 * Fetches from /api/billing/balance endpoint.
 * - Pauses polling when tab is hidden to save resources
 * - Immediately refetches when tab becomes visible again
 */
export function useCreditBalance(options: UseCreditBalanceOptions = {}) {
  const { refreshInterval = 30000, autoRefresh = true, pauseOnHidden = true } = options

  const selectedEndpoint = useStore((s) => s.selectedEndpoint)
  const authToken = useStore((s) => s.authToken)
  const creditBalance = useStore((s) => s.creditBalance)
  const setCreditBalance = useStore((s) => s.setCreditBalance)
  const [isVisible, setIsVisible] = useState(true)
  const [isLoading, setIsLoading] = useState(false)

  // Track tab visibility
  useEffect(() => {
    if (!pauseOnHidden) return

    const handleVisibilityChange = () => {
      const visible = document.visibilityState === 'visible'
      setIsVisible(visible)
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange)
  }, [pauseOnHidden])

  const fetchBalance = useCallback(async () => {
    if (!selectedEndpoint || !authToken) {
      return
    }

    setIsLoading(true)
    try {
      // Build the billing API URL from the agent endpoint
      // Agent endpoint: http://localhost:7777 -> Billing: http://localhost:7777/api/billing/balance
      const baseUrl = selectedEndpoint.replace(/\/+$/, '')
      const response = await fetch(`${baseUrl}/api/billing/balance`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        setCreditBalance(data.balance ?? null)
      }
    } catch (error) {
      console.error('Failed to fetch credit balance:', error)
    } finally {
      setIsLoading(false)
    }
  }, [selectedEndpoint, authToken, setCreditBalance])

  // Initial fetch
  useEffect(() => {
    fetchBalance()
  }, [fetchBalance])

  // Refetch when tab becomes visible again
  useEffect(() => {
    if (isVisible && pauseOnHidden) {
      fetchBalance()
    }
  }, [isVisible, pauseOnHidden, fetchBalance])

  // Auto-refresh (pauses when tab is hidden)
  useEffect(() => {
    if (!autoRefresh || refreshInterval <= 0) {
      return
    }

    // Don't poll when tab is hidden
    if (pauseOnHidden && !isVisible) {
      return
    }

    const interval = setInterval(fetchBalance, refreshInterval)
    return () => clearInterval(interval)
  }, [autoRefresh, refreshInterval, fetchBalance, pauseOnHidden, isVisible])

  return {
    balance: creditBalance,
    refetch: fetchBalance,
    isLoading,
  }
}

export default useCreditBalance
