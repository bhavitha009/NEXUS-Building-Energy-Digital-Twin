
import { useEffect, useState } from 'react'

const API_BASE = 'http://127.0.0.1:8000'

export function useNexusData() {
  const [data, setData] = useState({
    building: null,
    baseline: null,
    predictions: [],
    features: [],
    scenarios: [],
    impacts: [],
    insights: null,
    bestScenario: null,
  })

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function fetchJSON(endpoint) {
      const response = await fetch(`${API_BASE}${endpoint}`)

      if (!response.ok) {
        throw new Error(
          `API request failed (${response.status}): ${endpoint}`
        )
      }

      return response.json()
    }

    async function loadData() {
      try {
        const [
          building,
          baseline,
          predictionResponse,
          featureResponse,
          scenarioResponse,
          impactResponse,
          insights,
          bestScenario,
        ] = await Promise.all([
          fetchJSON('/api/building'),
          fetchJSON('/api/baseline'),
          fetchJSON('/api/predictions?limit=2583'),
          fetchJSON('/api/features'),
          fetchJSON('/api/scenarios'),
          fetchJSON('/api/impact-analysis'),
          fetchJSON('/api/insights'),
          fetchJSON('/api/best-scenario'),
        ])

        if (cancelled) return

        setData({
          building,
          baseline,
          predictions: predictionResponse.predictions || [],
          features: featureResponse.features || [],
          scenarios: scenarioResponse.scenarios || [],
          impacts: impactResponse.results || [],
          insights,
          bestScenario,
        })

        setError('')
      } catch (err) {
        if (!cancelled) {
          setError(
            `${err.message}. Check that the FastAPI backend is running on port 8000.`
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadData()

    return () => {
      cancelled = true
    }
  }, [])

  return { data, loading, error }
}
