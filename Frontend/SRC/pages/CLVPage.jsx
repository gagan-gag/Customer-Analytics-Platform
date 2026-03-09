import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getCLVAnalysis, getCLVSummary, trainModels } from '../services/api'
import { DollarSign, RefreshCw, TrendingUp } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function CLVPage() {
  const queryClient = useQueryClient()

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['clv-summary'],
    queryFn: () => getCLVSummary().then(res => res.data)
  })

  const { data: analysis, isLoading: analysisLoading } = useQuery({
    queryKey: ['clv-analysis'],
    queryFn: () => getCLVAnalysis().then(res => res.data)
  })

  const trainMutation = useMutation({
    mutationFn: () => trainModels('clv'),
    onSuccess: () => {
      queryClient.invalidateQueries(['clv-summary'])
      queryClient.invalidateQueries(['clv-analysis'])
      alert('CLV model trained successfully!')
    }
  })

  const topCustomers = analysis?.predictions
    ?.sort((a, b) => b.predicted_clv - a.predicted_clv)
    ?.slice(0, 10) || []

  const segmentData = [
    { segment: 'High Value', count: summary?.high_value_count || 0 },
    { segment: 'Medium Value', count: summary?.medium_value_count || 0 },
    { segment: 'Low Value', count: summary?.low_value_count || 0 }
  ]

  return (
    <div>
      <div className="page-header">
        <div className="flex-between">
          <div>
            <h1 className="page-title">Customer Lifetime Value</h1>
            <p className="page-description">
              Predict future customer value and identify high-value segments
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
          <div className="stat-label">Total Predicted CLV</div>
          <div className="stat-value">₹{summary?.total_predicted_clv?.toLocaleString() || '0'}</div>
        </div>
        <div className="stat-card secondary">
          <div className="stat-label">Average CLV</div>
          <div className="stat-value">₹{summary?.avg_clv?.toFixed(2) || '0'}</div>
        </div>
        <div className="stat-card accent">
          <div className="stat-label">High Value Customers</div>
          <div className="stat-value">{summary?.high_value_count?.toLocaleString() || '0'}</div>
        </div>
        <div className="stat-card warning">
          <div className="stat-label">Total Customers</div>
          <div className="stat-value">{summary?.total_customers?.toLocaleString() || '0'}</div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-2 mb-lg">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">CLV Segment Distribution</h3>
          </div>
          <div className="card-body">
            {summaryLoading ? (
              <div className="loading"><div className="spinner"></div></div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={segmentData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="segment" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8b5cf6" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Top 10 Customers by CLV</h3>
          </div>
          <div className="card-body" style={{ maxHeight: '300px', overflowY: 'auto' }}>
            {analysisLoading ? (
              <div className="loading"><div className="spinner"></div></div>
            ) : (
              <div>
                {topCustomers.map((customer, index) => (
                  <div 
                    key={index} 
                    className="flex-between mb-sm" 
                    style={{ 
                      padding: 'var(--spacing-sm)', 
                      background: 'var(--bg-secondary)', 
                      borderRadius: 'var(--radius-sm)',
                      borderLeft: '3px solid var(--accent)'
                    }}
                  >
                    <div>
                      <div className="font-semibold">Customer #{customer.customer_id}</div>
                      <div className="text-sm text-secondary">
                        Historical: ₹{customer.historical_value?.toFixed(2)}
                      </div>
                    </div>
                    <div className="text-lg font-bold text-accent">
                      ₹{customer.predicted_clv?.toFixed(2)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Detailed Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">CLV Predictions</h3>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Customer ID</th>
                <th>Predicted CLV</th>
                <th>Segment</th>
                <th>Historical Value</th>
                <th>Avg Order Value</th>
                <th>Purchase Frequency</th>
                <th>Predicted At</th>
              </tr>
            </thead>
            <tbody>
              {analysis?.predictions?.slice(0, 50).map((pred, index) => (
                <tr key={index}>
                  <td><strong>#{pred.customer_id}</strong></td>
                  <td className="font-bold text-primary">₹{pred.predicted_clv?.toFixed(2)}</td>
                  <td>
                    <span className={`badge badge-${
                      pred.clv_segment === 'High Value' ? 'success' : 
                      pred.clv_segment === 'Medium Value' ? 'info' : 'warning'
                    }`}>
                      {pred.clv_segment}
                    </span>
                  </td>
                  <td>₹{pred.historical_value?.toFixed(2)}</td>
                  <td>₹{pred.avg_order_value?.toFixed(2)}</td>
                  <td>{pred.purchase_frequency?.toFixed(3)}</td>
                  <td>{new Date(pred.predicted_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
