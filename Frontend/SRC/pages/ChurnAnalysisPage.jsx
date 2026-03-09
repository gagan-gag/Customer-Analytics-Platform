import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getChurnAnalysis, getChurnSummary, trainModels } from '../services/api'
import { AlertTriangle, RefreshCw, Users, TrendingDown, ShieldAlert, ShieldCheck } from 'lucide-react'
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts'

const RISK_COLORS = {
  'High': '#ef4444',
  'Medium': '#f59e0b',
  'Low': '#10b981'
}

export default function ChurnAnalysisPage() {
  const queryClient = useQueryClient()

  const {
    data: summary,
    isLoading: summaryLoading,
    isError: summaryError
  } = useQuery({
    queryKey: ['churn-summary'],
    queryFn: () => getChurnSummary().then(res => res.data),
    retry: 1
  })

  const {
    data: analysis,
    isLoading: analysisLoading,
    isError: analysisError
  } = useQuery({
    queryKey: ['churn-analysis'],
    queryFn: () => getChurnAnalysis().then(res => res.data),
    retry: 1
  })

  const trainMutation = useMutation({
    mutationFn: () => trainModels('churn'),
    onSuccess: () => {
      queryClient.invalidateQueries(['churn-summary'])
      queryClient.invalidateQueries(['churn-analysis'])
      alert('Churn model trained successfully!')
    },
    onError: (err) => {
      alert('Training failed: ' + (err?.response?.data?.detail || err.message))
    }
  })

  const predictions = analysis?.predictions || []

  const riskDistribution = [
    { name: 'High Risk', value: summary?.high_risk_count || 0, color: RISK_COLORS.High },
    { name: 'Medium Risk', value: summary?.medium_risk_count || 0, color: RISK_COLORS.Medium },
    { name: 'Low Risk', value: summary?.low_risk_count || 0, color: RISK_COLORS.Low }
  ]

  const hasRiskData = riskDistribution.some(r => r.value > 0)

  const highRiskCustomers = predictions
    .filter(p => p.churn_risk === 'High')
    .slice(0, 20)

  // Bar chart data for high risk: churn probability per customer
  const highRiskBarData = highRiskCustomers.map(c => ({
    name: c.customer_str_id || `#${c.customer_id}`,
    probability: parseFloat((c.churn_probability * 100).toFixed(1))
  }))

  const EmptyState = ({ message }) => (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem',
      color: 'var(--text-secondary)',
      gap: '0.5rem'
    }}>
      <ShieldCheck size={32} opacity={0.4} />
      <p style={{ margin: 0, fontSize: '0.9rem' }}>{message}</p>
    </div>
  )

  const ErrorState = ({ message }) => (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem',
      color: 'var(--danger)',
      gap: '0.5rem'
    }}>
      <AlertTriangle size={32} opacity={0.6} />
      <p style={{ margin: 0, fontSize: '0.9rem' }}>{message}</p>
    </div>
  )

  return (
    <div>
      <div className="page-header">
        <div className="flex-between">
          <div>
            <h1 className="page-title">Churn Analysis</h1>
            <p className="page-description">
              Predict and prevent customer churn with ML-powered insights
            </p>
          </div>
          <button
            className="btn btn-primary"
            onClick={() => trainMutation.mutate()}
            disabled={trainMutation.isPending}
          >
            <RefreshCw size={16} />
            {trainMutation.isPending ? 'Training...' : 'Retrain Model'}
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-4 mb-xl">
        <div className="stat-card primary">
          <div className="stat-label">Total Customers</div>
          <div className="stat-value">{summary?.total_customers?.toLocaleString() || '0'}</div>
        </div>
        <div className="stat-card" style={{ background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)' }}>
          <div className="stat-label">High Risk</div>
          <div className="stat-value">{summary?.high_risk_count?.toLocaleString() || '0'}</div>
        </div>
        <div className="stat-card warning">
          <div className="stat-label">Medium Risk</div>
          <div className="stat-value">{summary?.medium_risk_count?.toLocaleString() || '0'}</div>
        </div>
        <div className="stat-card secondary">
          <div className="stat-label">Low Risk</div>
          <div className="stat-value">{summary?.low_risk_count?.toLocaleString() || '0'}</div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-2 mb-lg">

        {/* Pie Chart - Risk Distribution */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Churn Risk Distribution</h3>
          </div>
          <div className="card-body">
            {summaryLoading ? (
              <div className="loading"><div className="spinner"></div></div>
            ) : summaryError ? (
              <ErrorState message="Failed to load risk distribution." />
            ) : !hasRiskData ? (
              <EmptyState message="No churn predictions available. Train the model to see data." />
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={riskDistribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={90}
                    dataKey="value"
                  >
                    {riskDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [value, 'Customers']} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Bar Chart - High Risk Customers */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">High Risk Customers — Churn Probability</h3>
          </div>
          <div className="card-body">
            {analysisLoading ? (
              <div className="loading"><div className="spinner"></div></div>
            ) : analysisError ? (
              <ErrorState message="Failed to load high risk customers." />
            ) : highRiskBarData.length === 0 ? (
              <EmptyState message="No high-risk customers found. Train the churn model first." />
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={highRiskBarData}
                  margin={{ top: 10, right: 20, left: 0, bottom: 60 }}
                >
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis
                    dataKey="name"
                    tick={{ fontSize: 10 }}
                    angle={-45}
                    textAnchor="end"
                    interval={0}
                  />
                  <YAxis
                    domain={[0, 100]}
                    tickFormatter={(v) => `${v}%`}
                    tick={{ fontSize: 11 }}
                  />
                  <Tooltip
                    formatter={(value) => [`${value}%`, 'Churn Probability']}
                  />
                  <Bar dataKey="probability" fill="#ef4444" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* High Risk Customer List */}
      <div className="card mb-lg">
        <div className="card-header">
          <h3 className="card-title">
            <ShieldAlert size={18} style={{ display: 'inline', marginRight: '0.5rem', color: '#ef4444' }} />
            High Risk Customer Details
          </h3>
        </div>
        <div className="card-body" style={{ maxHeight: '320px', overflowY: 'auto' }}>
          {analysisLoading ? (
            <div className="loading"><div className="spinner"></div></div>
          ) : analysisError ? (
            <ErrorState message="Failed to load customer data." />
          ) : highRiskCustomers.length === 0 ? (
            <EmptyState message="No high-risk customers found. Train the churn model first." />
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '0.75rem' }}>
              {highRiskCustomers.map((customer, index) => (
                <div
                  key={index}
                  className="flex-between"
                  style={{
                    padding: 'var(--spacing-sm)',
                    background: 'var(--bg-secondary)',
                    borderRadius: 'var(--radius-sm)',
                    borderLeft: '3px solid var(--danger)'
                  }}
                >
                  <div>
                    <div className="font-semibold">
                      {customer.customer_name || `Customer #${customer.customer_str_id || customer.customer_id}`}
                    </div>
                    <div className="text-sm text-secondary">
                      ID: {customer.customer_str_id || customer.customer_id}
                    </div>
                    <div className="text-sm" style={{ color: '#ef4444', fontWeight: 600 }}>
                      Churn Probability: {(customer.churn_probability * 100).toFixed(1)}%
                    </div>
                  </div>
                  <AlertTriangle size={20} color="#ef4444" />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Detailed Table - All Churn Predictions */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">All Churn Predictions</h3>
          {predictions.length > 0 && (
            <span className="text-sm text-secondary">
              Showing {Math.min(predictions.length, 50)} of {predictions.length} records
            </span>
          )}
        </div>
        <div className="table-container">
          {analysisLoading ? (
            <div className="loading" style={{ padding: '3rem' }}><div className="spinner"></div></div>
          ) : analysisError ? (
            <ErrorState message="Failed to load predictions. Make sure the backend is running." />
          ) : predictions.length === 0 ? (
            <EmptyState message="No predictions available. Click 'Retrain Model' to generate churn predictions." />
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Customer ID</th>
                  <th>Name</th>
                  <th>Churn Probability</th>
                  <th>Risk Level</th>
                  <th>Status</th>
                  <th>Risk Factors</th>
                  <th>Predicted At</th>
                </tr>
              </thead>
              <tbody>
                {predictions.slice(0, 50).map((pred, index) => (
                  <tr key={index}>
                    <td><strong>{pred.customer_str_id || `#${pred.customer_id}`}</strong></td>
                    <td>{pred.customer_name || '—'}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{
                          width: `${(pred.churn_probability * 100).toFixed(0)}px`,
                          maxWidth: '80px',
                          height: '6px',
                          background: pred.churn_risk === 'High' ? '#ef4444' : pred.churn_risk === 'Medium' ? '#f59e0b' : '#10b981',
                          borderRadius: '3px'
                        }} />
                        {(pred.churn_probability * 100).toFixed(1)}%
                      </div>
                    </td>
                    <td>
                      <span className={`badge badge-${
                        pred.churn_risk === 'High' ? 'danger' :
                        pred.churn_risk === 'Medium' ? 'warning' : 'success'
                      }`}>
                        {pred.churn_risk}
                      </span>
                    </td>
                    <td>
                      {pred.is_churned ?
                        <span className="badge badge-danger">Churned</span> :
                        <span className="badge badge-success">Active</span>
                      }
                    </td>
                    <td className="text-sm">{pred.risk_factors || '—'}</td>
                    <td>{pred.predicted_at ? new Date(pred.predicted_at).toLocaleDateString() : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}
