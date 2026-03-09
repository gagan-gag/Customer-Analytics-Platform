import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getRFMAnalysis, getRFMSegments, trainModels } from '../services/api'
import { RefreshCw, Target } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const SEGMENT_COLORS = {
  'Champions': '#10b981',
  'Loyal Customers': '#3b82f6',
  'Potential Loyalists': '#8b5cf6',
  'New Customers': '#06b6d4',
  'Promising': '#f59e0b',
  'Need Attention': '#f97316',
  'About to Sleep': '#ef4444',
  'At Risk': '#dc2626',
  'Cannot Lose Them': '#991b1b',
  'Hibernating': '#6b7280',
  'Lost': '#374151'
}

export default function SegmentationPage() {
  const queryClient = useQueryClient()

  const { data: segments, isLoading } = useQuery({
    queryKey: ['rfm-segments'],
    queryFn: () => getRFMSegments().then(res => res.data)
  })

  const trainMutation = useMutation({
    mutationFn: () => trainModels('rfm'),
    onSuccess: () => {
      queryClient.invalidateQueries(['rfm-segments'])
      alert('RFM model trained successfully!')
    }
  })

  const chartData = segments?.map(seg => ({
    segment: seg.segment,
    customers: seg.customer_count,
    value: seg.total_value,
    avgMonetary: seg.avg_monetary
  })) || []

  return (
    <div>
      <div className="page-header">
        <div className="flex-between">
          <div>
            <h1 className="page-title">RFM Segmentation</h1>
            <p className="page-description">
              Customer segmentation based on Recency, Frequency, and Monetary value
            </p>
          </div>
          <button 
            className="btn btn-primary"
            onClick={() => trainMutation.mutate()}
            disabled={trainMutation.isPending}
          >
            <RefreshCw size={16} className={trainMutation.isPending ? 'spinning' : ''} />
            {trainMutation.isPending ? 'Training...' : 'Recalculate'}
          </button>
        </div>
      </div>

      {/* Segment Cards */}
      <div className="grid grid-3 mb-xl">
        {segments?.slice(0, 6).map((seg, index) => (
          <div key={index} className="card" style={{ borderLeft: `4px solid ${SEGMENT_COLORS[seg.segment] || '#2563eb'}` }}>
            <div className="flex gap-md">
              <div style={{ flex: 1 }}>
                <h4 className="mb-sm">{seg.segment}</h4>
                <div className="text-sm text-secondary mb-sm">
                  {seg.customer_count} customers ({seg.percentage}%)
                </div>
                <div className="text-lg font-bold text-primary">
                  ₹{seg.total_value?.toLocaleString()}
                </div>
              </div>
              <Target size={32} style={{ color: SEGMENT_COLORS[seg.segment], opacity: 0.3 }} />
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-2 mb-lg">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Customer Distribution by Segment</h3>
          </div>
          <div className="card-body">
            {isLoading ? (
              <div className="loading"><div className="spinner"></div></div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="segment" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="customers" fill="#2563eb" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Average Monetary Value by Segment</h3>
          </div>
          <div className="card-body">
            {isLoading ? (
              <div className="loading"><div className="spinner"></div></div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="segment" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="avgMonetary" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* Detailed Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Segment Details</h3>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Segment</th>
                <th>Customers</th>
                <th>Percentage</th>
                <th>Avg Recency</th>
                <th>Avg Frequency</th>
                <th>Avg Monetary</th>
                <th>Total Value</th>
              </tr>
            </thead>
            <tbody>
              {segments?.map((seg, index) => (
                <tr key={index}>
                  <td>
                    <div className="flex gap-sm" style={{ alignItems: 'center' }}>
                      <div 
                        style={{ 
                          width: '12px', 
                          height: '12px', 
                          borderRadius: '50%', 
                          background: SEGMENT_COLORS[seg.segment] 
                        }}
                      />
                      <strong>{seg.segment}</strong>
                    </div>
                  </td>
                  <td>{seg.customer_count}</td>
                  <td>{seg.percentage}%</td>
                  <td>{seg.avg_recency?.toFixed(1)} days</td>
                  <td>{seg.avg_frequency?.toFixed(1)}</td>
                  <td>₹{seg.avg_monetary?.toFixed(2)}</td>
                  <td className="font-semibold">₹{seg.total_value?.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
