import { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getCustomers, uploadCustomerData, resetAllData } from '../services/api'
import { Upload, Download, Search, Trash2 } from 'lucide-react'

export default function CustomersPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [showConfirm, setShowConfirm] = useState(false)
  const fileInputRef = useRef(null)
  const queryClient = useQueryClient()

  const { data: customers, isLoading } = useQuery({
    queryKey: ['customers'],
    queryFn: () => getCustomers(0, 500).then(res => res.data)
  })

  const uploadMutation = useMutation({
    mutationFn: uploadCustomerData,
    onSuccess: (response) => {
      // Invalidate ALL related queries so every page refreshes with new data
      queryClient.invalidateQueries({ queryKey: ['customers'] })
      queryClient.invalidateQueries({ queryKey: ['stats'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['rfm-segments'] })
      queryClient.invalidateQueries({ queryKey: ['rfm-analysis'] })
      queryClient.invalidateQueries({ queryKey: ['churn-summary'] })
      queryClient.invalidateQueries({ queryKey: ['churn-analysis'] })
      queryClient.invalidateQueries({ queryKey: ['clv-summary'] })
      queryClient.invalidateQueries({ queryKey: ['clv-analysis'] })
      queryClient.invalidateQueries({ queryKey: ['retention-strategies'] })
      queryClient.invalidateQueries({ queryKey: ['recommendations'] })
      const msg = response?.data?.message || 'Data uploaded successfully!'
      alert(msg)
    },
    onError: (error) => {
      alert(`Upload failed: ${error.response?.data?.detail || error.message}`)
    }
  })

  const clearMutation = useMutation({
    mutationFn: resetAllData,
    onSuccess: (response) => {
      const d = response?.data?.deleted || {}
      queryClient.invalidateQueries()
      setShowConfirm(false)
      alert(
        `All data cleared!\n` +
        `\u2022 Customers: ${d.customers ?? 0}\n` +
        `\u2022 Transactions: ${d.transactions ?? 0}\n` +
        `\u2022 RFM Scores: ${d.rfm_scores ?? 0}\n` +
        `\u2022 Churn Predictions: ${d.churn_predictions ?? 0}\n` +
        `\u2022 CLV Predictions: ${d.clv_predictions ?? 0}\n` +
        `\nYou can now upload a fresh dataset.`
      )
    },
    onError: (error) => {
      setShowConfirm(false)
      alert(`Clear failed: ${error.response?.data?.detail || error.message}`)
    }
  })

  const handleFileUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      uploadMutation.mutate(file)
    }
  }

  const filteredCustomers = customers?.filter(customer =>
    customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.customer_id.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  return (
    <div>
      <div className="page-header">
        <div className="flex-between">
          <div>
            <h1 className="page-title">Customers</h1>
            <p className="page-description">
              Manage and view customer information
            </p>
          </div>
          <div className="flex gap-md">
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploadMutation.isPending}
            >
              <Upload size={16} />
              {uploadMutation.isPending ? 'Uploading...' : 'Upload Data'}
            </button>
            <button
              className="btn btn-sm"
              style={{ background: '#ef4444', color: '#ffffffff', border: 'none' }}
              onClick={() => setShowConfirm(true)}
              disabled={clearMutation.isPending}
            >
              <Trash2 size={16} />
              {clearMutation.isPending ? 'Clearing...' : 'Clear All Data'}
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.xlsx,.xls"
              style={{ display: 'none' }}
              onChange={handleFileUpload}
            />
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="card mb-lg">
        <div className="flex gap-md">
          <div style={{ position: 'relative', flex: 1 }}>
            <Search 
              size={20} 
              style={{ 
                position: 'absolute', 
                left: '12px', 
                top: '50%', 
                transform: 'translateY(-50%)',
                color: 'var(--text-tertiary)'
              }} 
            />
            <input
              type="text"
              placeholder="Search customers by name, email, or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 10px 10px 40px',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.875rem',
                fontFamily: 'var(--font-sans)'
              }}
            />
          </div>
        </div>
      </div>

      {/* Customers Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">
            All Customers ({filteredCustomers.length})
          </h3>
        </div>
        
        {isLoading ? (
          <div className="loading"><div className="spinner"></div></div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Customer ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Country</th>
                  <th>City</th>
                  <th>Registration Date</th>
                </tr>
              </thead>
              <tbody>
                {filteredCustomers.map((customer) => (
                  <tr key={customer.id}>
                    <td><strong>{customer.customer_id}</strong></td>
                    <td>{customer.name}</td>
                    <td>{customer.email || 'N/A'}</td>
                    <td>{customer.country || 'N/A'}</td>
                    <td>{customer.city || 'N/A'}</td>
                    <td>{new Date(customer.registration_date).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      {/* Confirmation Modal */}
      {showConfirm && (
        <div style={{
          position: 'fixed', inset: 0,
          background: 'rgba(0,0,0,0.6)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: '#ffffff',
            border: '1px solid #d1d5db',
            borderRadius: 'var(--radius-lg)',
            padding: '2rem',
            maxWidth: '420px',
            width: '90%',
            boxShadow: '0 20px 60px rgba(0,0,0,0.4)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
              <Trash2 size={24} color="#ef4444" />
              <h3 style={{ margin: 0, color: '#111111' }}>Clear All Data?</h3>
            </div>
            <p style={{ color: '#333333', marginBottom: '0.5rem' }}>
              This will <strong style={{ color: '#ef4444' }}>permanently delete</strong> all:
            </p>
            <ul style={{ color: '#333333', marginBottom: '1.5rem', paddingLeft: '1.25rem' }}>
              <li>Customers &amp; transactions</li>
              <li>RFM scores &amp; segments</li>
              <li>Churn predictions</li>
              <li>CLV predictions</li>
              <li>Trained model metadata</li>
            </ul>
            <p style={{ color: '#555555', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
              This action <strong style={{ color: '#111111' }}>cannot be undone</strong>. You will need to upload a new dataset and retrain models.
            </p>
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => setShowConfirm(false)}
                disabled={clearMutation.isPending}
              >
                Cancel
              </button>
              <button
                className="btn btn-sm"
                style={{ background: '#ef4444', color: '#ffffff', border: 'none' }}
                onClick={() => clearMutation.mutate()}
                disabled={clearMutation.isPending}
              >
                <Trash2 size={14} />
                {clearMutation.isPending ? 'Clearing...' : 'Yes, Clear Everything'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
