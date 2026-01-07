'use client'

import { useState, useEffect, useRef, useMemo } from 'react'
import { createClient, SupabaseClient, RealtimeChannel } from '@supabase/supabase-js'

export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'

export interface Job {
  id: string
  owner_id: string
  type: string
  status: JobStatus
  progress: number
  model: string
  params: Record<string, unknown> | null
  asset_id: string | null
  result: Record<string, unknown> | null
  error: string | null
  created_at: string
  updated_at: string
}

export interface ActiveGeneration {
  id: string
  type: string
  status: 'queued' | 'processing'
  progress: number
  title: string
  startedAt: number
}

// Map job types to human-readable labels
const JOB_TYPE_LABELS: Record<string, string> = {
  'text-to-video': 'Video',
  'image-to-video': 'Video',
  'text-to-image': 'Image',
  'avatar': 'Avatar',
  'text-to-speech': 'Speech',
  'text-to-audio': 'Audio',
  'text-to-music': 'Music',
  'video-to-audio': 'V2A',
}

function getJobTitle(job: Job): string {
  const typeLabel = JOB_TYPE_LABELS[job.type] || 'Generation'

  // Try to get a meaningful name from params
  if (job.params) {
    const prompt = job.params.prompt as string | undefined
    if (prompt && prompt.length > 0) {
      const truncated = prompt.length > 30 ? prompt.slice(0, 30) + '...' : prompt
      return `${typeLabel}: ${truncated}`
    }
  }

  return `${typeLabel} ${job.id.slice(0, 8)}`
}

interface UseActiveGenerationsProps {
  projectId: string
  supabaseUrl?: string
  supabaseAnonKey?: string
  userId?: string
}

export function useActiveGenerations({
  projectId,
  supabaseUrl,
  supabaseAnonKey,
  userId,
}: UseActiveGenerationsProps) {
  const [jobs, setJobs] = useState<Job[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const channelRef = useRef<RealtimeChannel | null>(null)
  const supabaseRef = useRef<SupabaseClient | null>(null)

  // Initialize Supabase client
  useEffect(() => {
    if (supabaseUrl && supabaseAnonKey) {
      supabaseRef.current = createClient(supabaseUrl, supabaseAnonKey)
    }
    return () => {
      supabaseRef.current = null
    }
  }, [supabaseUrl, supabaseAnonKey])

  // Fetch and subscribe to jobs
  useEffect(() => {
    const supabase = supabaseRef.current
    if (!supabase || !projectId) {
      setJobs([])
      setIsLoading(false)
      return
    }

    // Fetch initial jobs
    const fetchJobs = async () => {
      try {
        let query = supabase
          .schema('octupost')
          .from('jobs')
          .select('*')
          .or(`params->>project_id.eq.${projectId}`)
          .in('status', ['pending', 'processing'])
          .order('created_at', { ascending: false })
          .limit(10)

        if (userId) {
          query = query.eq('owner_id', userId)
        }

        const { data, error } = await query

        if (error) {
          console.error('[useActiveGenerations] Failed to fetch jobs:', error)
          setJobs([])
        } else {
          setJobs(data || [])
        }
      } catch (err) {
        console.error('[useActiveGenerations] Error:', err)
        setJobs([])
      } finally {
        setIsLoading(false)
      }
    }

    fetchJobs()

    // Subscribe to realtime updates
    const channelName = `active-generations-${projectId}`
    const channel = supabase
      .channel(channelName)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'octupost',
          table: 'jobs',
        },
        (payload) => {
          const newJob = payload.new as Job
          const oldJob = payload.old as Job | undefined

          // Check if job is for this project
          const isRelevant =
            newJob?.params &&
            (newJob.params as Record<string, unknown>).project_id === projectId

          if (!isRelevant && payload.eventType !== 'DELETE') {
            return
          }

          if (payload.eventType === 'INSERT') {
            if (newJob.status === 'pending' || newJob.status === 'processing') {
              setJobs((prev) => [newJob, ...prev].slice(0, 10))
            }
          } else if (payload.eventType === 'UPDATE') {
            if (newJob.status === 'completed' || newJob.status === 'failed' || newJob.status === 'cancelled') {
              // Remove completed/failed jobs from active list
              setJobs((prev) => prev.filter((j) => j.id !== newJob.id))
            } else {
              // Update job in list
              setJobs((prev) =>
                prev.map((j) => (j.id === newJob.id ? newJob : j))
              )
            }
          } else if (payload.eventType === 'DELETE' && oldJob) {
            setJobs((prev) => prev.filter((j) => j.id !== oldJob.id))
          }
        }
      )
      .subscribe()

    channelRef.current = channel

    return () => {
      channel.unsubscribe()
      channelRef.current = null
    }
  }, [projectId, userId])

  // Transform jobs to ActiveGeneration format
  const activeGenerations = useMemo<ActiveGeneration[]>(() => {
    return jobs.map((job) => ({
      id: job.id,
      type: job.type,
      status: job.status === 'pending' ? 'queued' : 'processing',
      progress: job.progress,
      title: getJobTitle(job),
      startedAt: new Date(job.created_at).getTime(),
    }))
  }, [jobs])

  return {
    activeGenerations,
    isLoading,
    count: activeGenerations.length,
    hasActive: activeGenerations.length > 0,
  }
}

export default useActiveGenerations
