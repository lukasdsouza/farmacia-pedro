import { useState, useEffect } from 'react'
import api from '../api/client'
import { RefreshCw, Search, ChevronDown } from 'lucide-react'

const STATUS_COLORS = {
  pendente:    'bg-yellow-100 text-yellow-800',
  confirmado:  'bg-blue-100 text-blue-700',
  em_preparo:  'bg-purple-100 text-purple-700',
  pronto:      'bg-teal-100 text-teal-700',
  entregue:    'bg-green-100 text-green-800',
  cancelado:   'bg-red-100 text-red-700',
  processando: 'bg-blue-100 text-blue-700',
  enviado:     'bg-teal-100 text-teal-700',
}

const CUSTOMER_STATUSES = ['pendente', 'confirmado', 'em_preparo', 'pronto', 'entregue', 'cancelado']

function StatusBadge({ status }) {
  return (
    <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${STATUS_COLORS[status] || 'bg-gray-100 text-gray-600'}`}>
      {status}
    </span>
  )
}

export default function Orders() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')
  const [updating, setUpdating] = useState(null)
  const [tab, setTab] = useState('chat')

  const load = async () => {
    setLoading(true)
    try {
      const url = tab === 'chat' ? '/orders' : '/orders/erp'
      const params = filter ? { status: filter } : {}
      const res = await api.get(url, { params })
      setOrders(res.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [tab, filter])

  const updateStatus = async (id, status) => {
    setUpdating(id)
    try {
      const url = tab === 'chat' ? `/orders/${id}/status` : `/orders/erp/${id}/status`
      await api.patch(url, { status })
      setOrders(prev => prev.map(o => o.id === id ? { ...o, status } : o))
    } catch (e) {
      alert('Erro ao atualizar status: ' + (e.response?.data?.detail || e.message))
    } finally {
      setUpdating(null)
    }
  }

  const statuses = tab === 'chat' ? CUSTOMER_STATUSES : ['pendente', 'processando', 'enviado', 'entregue', 'cancelado']

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Pedidos</h1>
          <p className="text-sm text-gray-500 mt-0.5">{orders.length} pedido(s) encontrado(s)</p>
        </div>
        <button onClick={load} disabled={loading} className="btn-secondary flex items-center gap-2">
          <RefreshCw size={15} className={loading ? 'animate-spin' : ''} /> Atualizar
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        {[['chat', 'Pedidos via Chat'], ['erp', 'Pedidos ERP']].map(([key, label]) => (
          <button
            key={key}
            onClick={() => { setTab(key); setFilter('') }}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${tab === key ? 'bg-primary-600 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'}`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Filter */}
      <div className="card p-4 mb-4 flex flex-wrap gap-2">
        <button onClick={() => setFilter('')} className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${!filter ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
          Todos
        </button>
        {statuses.map(s => (
          <button key={s} onClick={() => setFilter(s)} className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${filter === s ? 'bg-primary-600 text-white' : `${STATUS_COLORS[s]} hover:opacity-80`}`}>
            {s}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100 text-left">
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">ID</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Cliente</th>
              {tab === 'chat' && <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Entrega</th>}
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Total</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Data</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Status</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Ação</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              [...Array(5)].map((_, i) => (
                <tr key={i} className="border-b border-gray-50">
                  {[...Array(tab === 'chat' ? 7 : 6)].map((__, j) => (
                    <td key={j} className="px-4 py-3"><div className="h-4 bg-gray-100 rounded animate-pulse" /></td>
                  ))}
                </tr>
              ))
            ) : orders.length === 0 ? (
              <tr><td colSpan={tab === 'chat' ? 7 : 6} className="px-4 py-12 text-center text-gray-400">Nenhum pedido encontrado</td></tr>
            ) : orders.map(order => (
              <tr key={order.id} className="table-row">
                <td className="px-4 py-3 font-mono text-gray-500">#{order.id}</td>
                <td className="px-4 py-3 font-medium text-gray-800">
                  {tab === 'chat' ? (order.customer_name || '—') : order.customer}
                  {tab === 'chat' && order.customer_phone && (
                    <p className="text-xs text-gray-400">{order.customer_phone}</p>
                  )}
                </td>
                {tab === 'chat' && (
                  <td className="px-4 py-3 text-gray-600">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${order.delivery_type === 'entrega' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'}`}>
                      {order.delivery_type}
                    </span>
                    {order.delivery_address && <p className="text-xs text-gray-400 mt-0.5 max-w-32 truncate">{order.delivery_address}</p>}
                  </td>
                )}
                <td className="px-4 py-3 font-semibold text-gray-800">
                  R$ {Number(order.total).toFixed(2).replace('.', ',')}
                </td>
                <td className="px-4 py-3 text-gray-500 text-xs">
                  {new Date(order.created_at).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })}
                </td>
                <td className="px-4 py-3"><StatusBadge status={order.status} /></td>
                <td className="px-4 py-3">
                  <div className="relative">
                    <select
                      value={order.status}
                      disabled={updating === order.id}
                      onChange={e => updateStatus(order.id, e.target.value)}
                      className="text-xs border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:border-primary-500 cursor-pointer bg-white disabled:opacity-50 pr-6 appearance-none"
                    >
                      {statuses.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                    <ChevronDown size={12} className="absolute right-1.5 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400" />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
