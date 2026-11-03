import { useMemo, useState } from 'react'
import {
  LayoutDashboard, Activity, SlidersHorizontal,
  GitCompareArrows, BrainCircuit, Zap, Building2,
  Target, TrendingDown, Clock3, Leaf, Menu, X,
  Info, AlertCircle, CheckCircle2, BarChart3,
  Lightbulb, Layers, Box
} from 'lucide-react'

import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, BarChart, Bar,
  ReferenceLine
} from 'recharts'

import { useNexusData } from './useNexusData'
import './App.css'

import RotatableBuildingDigitalTwin from './BuildingDigitalTwin'
const navigation = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'analytics', label: 'Energy Analytics', icon: Activity },
  { id: 'simulator', label: 'Scenario Simulator', icon: SlidersHorizontal },
  { id: 'comparison', label: 'Scenario Comparison', icon: GitCompareArrows },
  { id: 'insights', label: 'AI Insights', icon: BrainCircuit },
  { id: 'digital-twin', label: 'Building Digital Twin', icon: Building2 },
]

const formatNumber = (value, digits = 2) =>
  Number(value || 0).toFixed(digits)

const formatPercent = (value) =>
  `${Number(value || 0).toFixed(2)}%`

function MetricCard({ icon: Icon, caption, label, value, note, color }) {
  return (
    <article className="metric-card">
      <div className="metric-top">
        <span className={`metric-icon ${color}`}>
          <Icon size={20} />
        </span>
        <span className="metric-caption">{caption}</span>
      </div>
      <p className="metric-label">{label}</p>
      <h2>{value}</h2>
      <p className="metric-footnote">{note}</p>
    </article>
  )
}

function Panel({ title, subtitle, children, className = '' }) {
  return (
    <section className={`panel ${className}`}>
      <div className="panel-heading">
        <div>
          <h3>{title}</h3>
          <p>{subtitle}</p>
        </div>
      </div>
      {children}
    </section>
  )
}

function LoadingState() {
  return (
    <div className="panel coming-soon">
      <div className="placeholder-icon">
        <Activity size={28} />
      </div>
      <h2>Loading NEXUS data</h2>
      <p>Connecting to the NEXUS backend...</p>
    </div>
  )
}

function ErrorState({ error }) {
  return (
    <div className="panel coming-soon">
      <AlertCircle size={34} color="#d05c5c" />
      <h2>Unable to load project data</h2>
      <p>{error}</p>
      <p>Check that the FastAPI backend is running on port 8000.</p>
    </div>
  )
}

/* ---------------- DASHBOARD ---------------- */

function DashboardHome({ data }) {
  const baseline = data.scenarios.find(
    (s) => s.Scenario === 'Baseline'
  )

  const best = data.impacts
    .filter((s) => s.Scenario_Status === 'Assumption-Based Simulation')
    .filter((s) => Number.isFinite(Number(s.Rank)))
    .sort((a, b) => Number(a.Rank) - Number(b.Rank))[0]

  const chartData = data.predictions
    .filter((_, index) => index % 24 === 0)
    .map((row) => ({
      time: String(row.timestamp).slice(5, 16),
      actual: Number(row.Actual),
      predicted: Number(row.Predicted),
    }))

  return (
    <>
      <div className="welcome-section">
        <div>
          <p className="eyebrow">BUILDING ENERGY MANAGEMENT</p>
          <h1>Building Overview</h1>
          <p className="welcome-description">
            Monitor electricity demand and explore energy-efficiency scenarios.
          </p>
        </div>
        <div className="date-chip">
          <Clock3 size={16} />
          Historical dataset · 2016–2017
        </div>
      </div>

      <section className="building-banner">
        <div className="building-banner-content">
          <div className="building-icon">
            <Building2 size={25} />
          </div>
          <div>
            <p className="banner-label">SELECTED BUILDING</p>
            <h2>Panther Education – Vincent</h2>
            <p className="banner-subtitle">
              Education building · Panther site
            </p>
          </div>
        </div>
        <div className="building-area">
          <span>Building area</span>
          <strong>11,248.1 m²</strong>
        </div>
      </section>

      <section className="metrics-grid">
        <MetricCard
          icon={Zap}
          caption="BASELINE"
          label="Average predicted demand"
          value={formatNumber(baseline?.Average_Demand)}
          note="Dataset measurement units"
          color="blue"
        />
        <MetricCard
          icon={Target}
          caption="MODEL PERFORMANCE"
          label="Evaluation R²"
          value="0.9483"
          note="Random Forest model"
          color="purple"
        />
        <MetricCard
          icon={TrendingDown}
          caption="ERROR METRIC"
          label="Evaluation MAE"
          value="7.8908"
          note="Chronological evaluation period"
          color="green"
        />
        <MetricCard
          icon={SlidersHorizontal}
          caption="SIMULATION"
          label="Scenarios generated"
          value={String(data.scenarios.length)}
          note="Precomputed scenarios"
          color="orange"
        />
      </section>

      <section className="dashboard-grid">
        <Panel
          title="Actual vs Predicted Demand"
          subtitle="Evaluation period · sampled hourly observations"
        >
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" tick={{ fontSize: 9 }} minTickGap={35} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="actual"
                  name="Actual"
                  stroke="#347fca"
                  dot={false}
                  strokeWidth={2}
                />
                <Line
                  type="monotone"
                  dataKey="predicted"
                  name="Predicted"
                  stroke="#18a58b"
                  dot={false}
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="panel-note">
            <Info size={15} />
            Displayed points are sampled from the actual evaluation CSV.
          </div>
        </Panel>

        <Panel title="Model Information" subtitle="Final trained prediction model">
          <div className="model-name">
            <div className="model-symbol">
              <BrainCircuit size={24} />
            </div>
            <div>
              <strong>Random Forest</strong>
              <span>Regression model</span>
            </div>
          </div>

          {[
            ['Evaluation MAE', '7.8908'],
            ['Evaluation RMSE', '11.4067'],
            ['Evaluation R²', '0.9483'],
            ['Evaluation samples', data.predictions.length.toLocaleString('en-IN')],
          ].map(([label, value]) => (
            <div className="model-detail" key={label}>
              <span>{label}</span>
              <strong>{value}</strong>
            </div>
          ))}
        </Panel>
      </section>

      <Panel
        title="Best Ranked Intervention"
        subtitle="Based on the impact analysis ranking"
        className="scenario-panel"
      >
        {best ? (
          <div className="best-scenario">
            <div>
              <span className="banner-label">TOP RANKED SIMULATION</span>
              <h2>{best.Scenario}</h2>
              <p>
                Average simulated demand: {formatNumber(best.Average_Demand)}
              </p>
            </div>
            <div className="best-scenario-value">
              <strong>{formatPercent(best.Demand_Savings_Percent)}</strong>
              <span>Assumed demand reduction</span>
            </div>
          </div>
        ) : (
          <p>No ranked intervention is available.</p>
        )}

        <p className="table-disclaimer">
          These are assumption-based simulations, not verified real-world savings.
        </p>
      </Panel>
    </>
  )
}

/* ---------------- ENERGY ANALYTICS ---------------- */

function EnergyAnalytics({ data }) {
  const [range, setRange] = useState('all')

  const predictions = useMemo(() => {
    if (range === 'all') return data.predictions
    return data.predictions.slice(0, Number(range))
  }, [data.predictions, range])

  const chartData = predictions.map((row) => ({
    time: String(row.timestamp).slice(5, 16),
    actual: Number(row.Actual),
    predicted: Number(row.Predicted),
    error: Number(row.Prediction_Error),
  }))

  const features = [...data.features]
    .sort((a, b) => Number(b.Importance) - Number(a.Importance))
    .slice(0, 10)
    .map((row) => ({
      feature: row.Feature,
      importance: Number(row.Importance) * 100,
    }))

  const mae = data.predictions.reduce(
    (sum, row) => sum + Number(row.Absolute_Error), 0
  ) / (data.predictions.length || 1)

  const mse = data.predictions.reduce(
    (sum, row) => sum + Number(row.Prediction_Error) ** 2, 0
  ) / (data.predictions.length || 1)

  return (
    <>
      <div className="welcome-section">
        <div>
          <p className="eyebrow">MODEL PERFORMANCE</p>
          <h1>Energy Analytics</h1>
          <p className="welcome-description">
            Explore evaluation predictions, errors and model feature importance.
          </p>
        </div>

        <select
          className="data-select"
          value={range}
          onChange={(e) => setRange(e.target.value)}
        >
          <option value="all">All evaluation records</option>
          <option value="500">First 500 records</option>
          <option value="200">First 200 records</option>
        </select>
      </div>

      <section className="metrics-grid">
        <MetricCard icon={Target} caption="MODEL" label="R² score"
          value="0.9483" note="Random Forest" color="purple" />
        <MetricCard icon={Activity} caption="ERROR" label="Calculated MAE"
          value={formatNumber(mae, 4)} note="Evaluation CSV" color="blue" />
        <MetricCard icon={BarChart3} caption="ERROR" label="Calculated RMSE"
          value={formatNumber(Math.sqrt(mse), 4)} note="Evaluation CSV" color="orange" />
        <MetricCard icon={CheckCircle2} caption="DATA" label="Evaluation records"
          value={data.predictions.length.toLocaleString('en-IN')}
          note="Test prediction rows" color="green" />
      </section>

      <Panel
        title="Actual vs Predicted Electricity Demand"
        subtitle="Chronological model evaluation"
      >
        <div className="chart-container large">
          <ResponsiveContainer width="100%" height={330}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" tick={{ fontSize: 9 }} minTickGap={35} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Legend />
              <Line dataKey="actual" name="Actual" stroke="#347fca"
                dot={false} strokeWidth={2} />
              <Line dataKey="predicted" name="Predicted" stroke="#18a58b"
                dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Panel>

      <section className="dashboard-grid analytics-grid">
        <Panel
          title="Feature Importance"
          subtitle="Top 10 features from the trained Random Forest"
        >
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={340}>
              <BarChart data={features} layout="vertical"
                margin={{ left: 22, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 9 }} unit="%" />
                <YAxis type="category" dataKey="feature"
                  width={90} tick={{ fontSize: 9 }} />
                <Tooltip formatter={(value) =>
                  `${Number(value).toFixed(3)}%`
                } />
                <Bar dataKey="importance" name="Importance"
                  fill="#477fbd" radius={[0, 5, 5, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="table-disclaimer">
            Feature importance indicates predictive contribution, not causation.
          </p>
        </Panel>

        <Panel
          title="Prediction Error"
          subtitle="Signed prediction error over selected records"
        >
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={340}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" tick={{ fontSize: 9 }} minTickGap={30} />
                <YAxis tick={{ fontSize: 9 }} />
                <Tooltip />
                <ReferenceLine y={0} stroke="#8e98a7" />
                <Line dataKey="error" name="Prediction error"
                  stroke="#d58a43" dot={false} strokeWidth={1.5} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </section>
    </>
  )
}

/* ---------------- SCENARIO SIMULATOR ---------------- */

function ScenarioSimulator({ data }) {
  const [selected, setSelected] = useState('Efficiency +15%')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const impact = data.impacts.find((item) => item.Scenario === selected)
  const displayedScenario = result?.result || data.scenarios.find(
    (item) => item.Scenario === selected
  )

  async function handleScenarioChange(value) {
    setSelected(value)
    setError('')
    setLoading(true)
    setResult(null)

    try {
      const response = await fetch('http://127.0.0.1:8000/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario_name: value }),
      })

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message || 'Unable to retrieve scenario result.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="welcome-section">
        <div>
          <p className="eyebrow">BUILDING DIGITAL TWIN</p>
          <h1>Scenario Simulator</h1>
          <p className="welcome-description">
            Explore precomputed electricity demand intervention scenarios.
          </p>
        </div>
      </div>

      <Panel
        title="Select a Scenario"
        subtitle="Choose from the scenarios generated by the backend"
      >
        <div className="simulator-controls">
          <label htmlFor="scenario-select">Available scenario</label>
          <select
            id="scenario-select"
            className="data-select"
            value={selected}
            onChange={(e) => handleScenarioChange(e.target.value)}
          >
            {data.scenarios.map((item) => (
              <option key={item.Scenario} value={item.Scenario}>
                {item.Scenario}
              </option>
            ))}
          </select>
        </div>

        {loading && <p className="simulator-message">Loading scenario result...</p>}
        {error && <p className="simulator-error">{error}</p>}

        {displayedScenario && !loading && (
          <div className="simulation-result">
            <div className="result-item">
              <span>Average simulated demand</span>
              <strong>{formatNumber(displayedScenario.Average_Demand)}</strong>
            </div>
            <div className="result-item">
              <span>Change from baseline</span>
              <strong>{formatPercent(displayedScenario.Change_From_Baseline_Percent)}</strong>
            </div>
            <div className="result-item">
              <span>Scenario category</span>
              <strong>{displayedScenario.Scenario_Type}</strong>
            </div>
            <div className="result-item">
              <span>Heuristic sustainability score</span>
              <strong>
                {formatNumber(impact?.Sustainability_Score, 1)} / 100
              </strong>
            </div>
          </div>
        )}

        {displayedScenario && !loading && (
          <div className="assumption-box">
            <Info size={18} />
            <div>
              <strong>Scenario assumption</strong>
              <p>{displayedScenario.Assumption}</p>
            </div>
          </div>
        )}

        <p className="table-disclaimer">
          Results are retrieved from the backend's precomputed scenario outputs.
          They do not retrain or dynamically modify the model.
        </p>
      </Panel>
    </>
  )
}

/* ---------------- SCENARIO COMPARISON ---------------- */

function ScenarioComparison({ data }) {
  const sorted = [...data.impacts].sort((a, b) => {
    const rankA = Number(a.Rank)
    const rankB = Number(b.Rank)
    if (!Number.isFinite(rankA)) return 1
    if (!Number.isFinite(rankB)) return -1
    return rankA - rankB
  })

  const chartData = sorted.map((row) => ({
    name: row.Scenario,
    demand: Number(row.Average_Demand),
  }))

  return (
    <>
      <div className="welcome-section">
        <div>
          <p className="eyebrow">INTERVENTION ANALYSIS</p>
          <h1>Scenario Comparison</h1>
          <p className="welcome-description">
            Compare simulated demand and heuristic impact scores across scenarios.
          </p>
        </div>
      </div>

      <Panel
        title="Average Demand by Scenario"
        subtitle="Values retrieved from scenario_results.csv"
      >
        <div className="chart-container large">
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={chartData}
              margin={{ bottom: 60, left: 8, right: 15 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" angle={-35} textAnchor="end"
                interval={0} height={85} tick={{ fontSize: 9 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Bar dataKey="demand" name="Average demand"
                fill="#477fbd" radius={[5, 5, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Panel>

      <Panel
        title="Impact Analysis"
        subtitle="Savings, impact category, heuristic score and ranking"
        className="scenario-panel"
      >
        <div className="scenario-table-wrap">
          <table className="scenario-table">
            <thead>
              <tr>
                <th>Scenario</th>
                <th>Average demand</th>
                <th>Savings</th>
                <th>Impact category</th>
                <th>Score</th>
                <th>Rank</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((row) => (
                <tr key={row.Scenario}>
                  <td>{row.Scenario}</td>
                  <td>{formatNumber(row.Average_Demand)}</td>
                  <td>{formatPercent(row.Demand_Savings_Percent)}</td>
                  <td>{row.Impact_Category}</td>
                  <td>{formatNumber(row.Sustainability_Score, 1)}</td>
                  <td>{row.Rank === '' || row.Rank == null ? '—' : row.Rank}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="table-disclaimer">
          Sustainability scores are heuristic values, not independently measured
          sustainability indicators.
        </p>
      </Panel>
    </>
  )
}

/* ---------------- AI INSIGHTS ---------------- */

function AIInsights({ data }) {
  const best = data.impacts
    .filter((row) => row.Scenario_Status === 'Assumption-Based Simulation')
    .filter((row) => Number.isFinite(Number(row.Rank)))
    .sort((a, b) => Number(a.Rank) - Number(b.Rank))[0]

  const baseline = data.scenarios.find(
    (row) => row.Scenario === 'Baseline'
  )

  return (
    <>
      <div className="welcome-section">
        <div>
          <p className="eyebrow">EXPLANATION & RECOMMENDATIONS</p>
          <h1>AI Insights</h1>
          <p className="welcome-description">
            Scenario-based recommendations from the project's controlled analysis layer.
          </p>
        </div>
      </div>

      <Panel
        title="Top Ranked Intervention"
        subtitle="Selected using the impact analysis ranking"
      >
        {best ? (
          <>
            <div className="insight-highlight">
              <div className="insight-icon">
                <Lightbulb size={27} />
              </div>
              <div>
                <span className="banner-label">TOP RANKED SIMULATION</span>
                <h2>{best.Scenario}</h2>
                <p>{best.Impact_Category}</p>
              </div>
            </div>

            <div className="simulation-result">
              <div className="result-item">
                <span>Baseline average demand</span>
                <strong>{formatNumber(baseline?.Average_Demand)}</strong>
              </div>
              <div className="result-item">
                <span>Scenario average demand</span>
                <strong>{formatNumber(best.Average_Demand)}</strong>
              </div>
              <div className="result-item">
                <span>Assumed demand reduction</span>
                <strong>{formatPercent(best.Demand_Savings_Percent)}</strong>
              </div>
              <div className="result-item">
                <span>Heuristic sustainability score</span>
                <strong>{formatNumber(best.Sustainability_Score, 1)} / 100</strong>
              </div>
            </div>
          </>
        ) : (
          <p>No ranked intervention is available.</p>
        )}
      </Panel>

      <Panel
        title="Interpretation and Limitations"
        subtitle="How to understand these results"
      >
        <div className="insight-list">
          <div className="insight-row">
            <CheckCircle2 size={19} />
            <div>
              <strong>Model-based demand prediction</strong>
              <p>
                The Random Forest model estimates electricity demand using
                historical demand, weather and time-based features.
              </p>
            </div>
          </div>

          <div className="insight-row">
            <Info size={19} />
            <div>
              <strong>Assumption-based interventions</strong>
              <p>
                Efficiency and operational reductions are simulated assumptions.
                They are not measured real-world savings.
              </p>
            </div>
          </div>

          <div className="insight-row">
            <Info size={19} />
            <div>
              <strong>Heuristic sustainability score</strong>
              <p>
                The score is calculated from demand savings percentage using
                the project's scoring formula.
              </p>
            </div>
          </div>

          <div className="insight-row">
            <Info size={19} />
            <div>
              <strong>Controlled explanation layer</strong>
              <p>
                This frontend displays results derived from the project's
                analysis. It does not claim to connect to a live external
                language model.
              </p>
            </div>
          </div>
        </div>
      </Panel>
    </>
  )
}

/* ---------------- BUILDING DIGITAL TWIN ---------------- */

function BuildingDigitalTwin({ data }) {
  const [view, setView] = useState('twin')
  const [selectedFloor, setSelectedFloor] = useState(6)

  const baseline = data.scenarios.find(
    (item) => item.Scenario === 'Baseline'
  )

  const demand = Number(baseline?.Average_Demand || 0)
  const floors = [1, 2, 3, 4, 5, 6]

  return (
    <>
      <div className="welcome-section">
        <div>
          <p className="eyebrow">BUILDING VISUALIZATION</p>
          <h1>Building Digital Twin</h1>
          <p className="welcome-description">
            Interactive illustrative model of Panther Education – Vincent.
          </p>
        </div>
      </div>

      <section className="twin-header">
        <div>
          <h2>Panther Education Building</h2>
          <p>Panther Site · Vincent · Building-level electricity data</p>
        </div>

        <div className="twin-tabs">
          <button
            className={view === 'twin' ? 'selected' : ''}
            onClick={() => setView('twin')}
          >
            <Box size={15} /> 3D Twin
          </button>
          <button
            className={view === 'energy' ? 'selected' : ''}
            onClick={() => setView('energy')}
          >
            <Zap size={15} /> Energy Map
          </button>
          <button
            className={view === 'zones' ? 'selected' : ''}
            onClick={() => setView('zones')}
          >
            <Layers size={15} /> Zones
          </button>
        </div>
      </section>

      <section className="twin-stage">
        {view === 'twin' && (
          <>
            <div className="twin-status">
              <span className="online-dot" />
              BUILDING MODEL
              <small>Interactive · Illustrative</small>
            </div>

            <div className="twin-floor-info">
              <strong>Floor {selectedFloor}</strong>
              <p>
                {selectedFloor === 6
                  ? 'Roof and upper building zone'
                  : `Illustrative building floor ${selectedFloor}`}
              </p>
              <small>Floor-level readings are not available.</small>
            </div>

            <svg
              className="building-svg"
              viewBox="0 0 850 530"
              role="img"
              aria-label="Illustrative six-floor building model"
            >
              <polygon
                points="100,420 440,275 790,390 450,520"
                fill="#d1d6dc"
              />

              <polygon
                points="570,125 710,165 710,390 570,350"
                fill="#91b5c2"
              />

              <polygon
                points="280,165 570,125 570,350 280,405"
                fill="#b6c9d2"
              />

              {floors.map((floor, index) => {
                const y = 165 + index * 38
                const nextY = y + 38
                const active = selectedFloor === floor

                return (
                  <g
                    key={floor}
                    onClick={() => setSelectedFloor(floor)}
                    className="floor-select"
                  >
                    <polygon
                      points={`280,${y} 570,${y - 40} 570,${nextY - 40} 280,${nextY}`}
                      fill={active ? '#56c8c1' : index % 2 === 0 ? '#b8cbd3' : '#a7bec9'}
                      stroke="#edf4f7"
                      strokeWidth="2"
                    />
                    <text
                      x="420"
                      y={y - 10}
                      textAnchor="middle"
                      fill="#344d60"
                      fontSize="12"
                      fontWeight="600"
                    >
                      Floor {floor}
                    </text>
                  </g>
                )
              })}

              <polygon
                points="280,165 420,85 710,125 570,205"
                fill="#34465f"
              />
              <polygon
                points="570,205 710,165 710,180 570,220"
                fill="#29394f"
              />

              {[390, 455, 520, 585].map((x) => (
                <g key={x}>
                  <polygon
                    points={`${x},105 ${x + 35},95 ${x + 55},101 ${x + 20},112`}
                    fill="#9aabba"
                  />
                  <polygon
                    points={`${x},105 ${x + 20},112 ${x + 20},135 ${x},128`}
                    fill="#52667b"
                  />
                </g>
              ))}

              {[
                [330, 205], [430, 190], [520, 175],
                [350, 285], [465, 270], [540, 250],
                [390, 355], [500, 335],
              ].map(([x, y], index) => (
                <circle
                  key={index}
                  cx={x}
                  cy={y}
                  r="5"
                  fill="#35b9e8"
                  stroke="white"
                  strokeWidth="2"
                />
              ))}
            </svg>

            <div className="twin-legend">
              <span><i className="sensor-dot" /> Illustrative marker</span>
              <span><i className="active-dot" /> Selected floor</span>
            </div>
          </>
        )}

        {view === 'energy' && (
          <div className="energy-map-content">
            <h2>Building Energy Map</h2>
            <p>
              Building-wide electricity demand from the historical dataset.
            </p>

            <div className="energy-total">
              <span>Average baseline predicted demand</span>
              <strong>{demand.toFixed(2)}</strong>
              <small>Dataset measurement units</small>
            </div>

            <div className="energy-zones">
              {floors.map((floor) => (
                <button
                  key={floor}
                  className={
                    selectedFloor === floor
                      ? 'energy-zone active'
                      : 'energy-zone'
                  }
                  onClick={() => {
                    setSelectedFloor(floor)
                    setView('zones')
                  }}
                >
                  <span>Floor {floor}</span>
                  <span>Illustrative zone</span>
                </button>
              ))}
            </div>

            <p className="twin-disclaimer">
              Floor-level energy distribution is illustrative. The dataset
              provides building-level measurements only.
            </p>
          </div>
        )}

        {view === 'zones' && (
          <div className="energy-map-content">
            <h2>Building Zones</h2>
            <p>Select a floor to explore its illustrative zone information.</p>

            <div className="zone-selector">
              {floors.map((floor) => (
                <button
                  key={floor}
                  className={
                    selectedFloor === floor
                      ? 'zone-button active'
                      : 'zone-button'
                  }
                  onClick={() => setSelectedFloor(floor)}
                >
                  Floor {floor}
                </button>
              ))}
            </div>

            <div className="selected-zone">
              <Building2 size={35} />
              <div>
                <span>SELECTED ZONE</span>
                <h3>Floor {selectedFloor}</h3>
                <p>
                  Illustrative floor representation of Panther Education Building.
                </p>
              </div>
            </div>

            <div className="zone-data-note">
              <Info size={18} />
              <p>
                Actual floor-wise electricity consumption, occupancy and sensor
                readings are not included in the available dataset. Only
                overall building demand is currently available.
              </p>
            </div>
          </div>
        )}
      </section>

      <section className="twin-energy-footer">
        <div>
          <span>BUILDING ENERGY BASELINE</span>
          <strong>{demand.toFixed(2)}</strong>
          <small>Dataset measurement units</small>
        </div>

        <div>
          <span>BUILDING AREA</span>
          <strong>11,248.1 m²</strong>
          <small>Panther Education – Vincent</small>
        </div>

        <div>
          <span>MODEL STATUS</span>
          <strong>Connected</strong>
          <small>Historical data via NEXUS API</small>
        </div>
      </section>
    </>
  )
}

/* ---------------- MAIN APP ---------------- */

function App() {
  const [activePage, setActivePage] = useState('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const { data, loading, error } = useNexusData()

  const activeItem = navigation.find(
    (item) => item.id === activePage
  )

  const pageContent = () => {
    if (loading) return <LoadingState />
    if (error) return <ErrorState error={error} />

    switch (activePage) {
      case 'analytics':
        return <EnergyAnalytics data={data} />
      case 'simulator':
        return <ScenarioSimulator data={data} />
      case 'comparison':
        return <ScenarioComparison data={data} />
      case 'insights':
        return <AIInsights data={data} />
      case 'digital-twin':
        return <RotatableBuildingDigitalTwin data={data} />
      default:
        return <DashboardHome data={data} />
    }
  }

  return (
    <div className="app-shell">
      {sidebarOpen && (
        <button
          className="sidebar-overlay"
          aria-label="Close navigation"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="brand">
          <div className="brand-logo">
            <Zap size={23} />
          </div>
          <div>
            <h2>NEXUS</h2>
            <span>DIGITAL TWIN</span>
          </div>
          <button
            className="mobile-close"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close menu"
          >
            <X size={20} />
          </button>
        </div>

        <div className="sidebar-section-label">WORKSPACE</div>

        <nav className="sidebar-nav">
          {navigation.map((item) => {
            const Icon = item.icon

            return (
              <button
                key={item.id}
                className={`nav-item ${activePage === item.id ? 'active' : ''}`}
                onClick={() => {
                  setActivePage(item.id)
                  setSidebarOpen(false)
                }}
              >
                <Icon size={19} />
                <span>{item.label}</span>
                {activePage === item.id && (
                  <span className="active-indicator" />
                )}
              </button>
            )
          })}
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-info-icon">
            <Leaf size={20} />
          </div>
          <div>
            <strong>Building Sustainability</strong>
            <p>Data-driven scenario analysis</p>
          </div>
        </div>

        <div className="sidebar-version">
          NEXUS · PROJECT DASHBOARD
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="menu-button"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open navigation"
            >
              <Menu size={21} />
            </button>

            <div className="breadcrumb">
              <span>NEXUS</span>
              <span className="breadcrumb-separator">/</span>
              <strong>{activeItem?.label || 'Dashboard'}</strong>
            </div>
          </div>

          <div className="topbar-actions">
            <div className="project-status">
              <span className="online-dot" />
              Project workspace
            </div>
            <div className="profile">
              <div className="profile-avatar">N</div>
            </div>
          </div>
        </header>

        <div className="page-content">
          {pageContent()}
        </div>

        <footer className="app-footer">
          <span>NEXUS Digital Twin Framework</span>
          <span>Building-level electricity scenario simulation</span>
        </footer>
      </main>
    </div>
  )
}

export default App