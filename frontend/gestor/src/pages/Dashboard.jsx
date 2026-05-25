import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../api/client'
import { Package, ShoppingBag, AlertTriangle, TrendingUp, DollarSign, Users, RefreshCw } from 'lucide-react'

function StatCard({ icon: Icon, label, value, sub, color }) {
  return (
    <div className="card p-5 flex items-start gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
        <Icon size={22} className="text-white" />
      </div>
      <div>
        <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">{label}</p>
        <p className="text-2xl font-bold text-gray-900 mt-0.5">{value}</p>
        {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { isGestor } = useAuth()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const load = async (withRefresh = false) => {
    if (withRefresh) setRefreshing(true)
    try {
      const res = await api.get('/dashboard')
      setStats(res.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => { load() }, [])

  if (loading) return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 animate-pulse">
      {[...Array(6)].map((_, i) => <div key={i} className="card h-24 bg-gray-100" />)}
    </div>
  )

  if (!stats) return <p className="text-gray-500">Erro ao carregar dashboard.</p>

  const statCards = [
    { icon: Package, label: 'Total de Produtos', value: stats.total_products, sub: 'no catálogo', color: 'bg-blue-500' },
    { icon: AlertTriangle, label: 'Estoque Baixo', value: stats.low_stock_count, sub: 'produtos com alerta', color: stats.low_stock_count > 0 ? 'bg-orange-500' : 'bg-gray-400' },
    { icon: ShoppingBag, label: 'Pedidos Pendentes', value: stats.pending_customer_orders, sub: 'via chat', color: stats.pending_customer_orders > 0 ? 'bg-yellow-500' : 'bg-gray-400' },
    { icon: TrendingUp, label: 'Pedidos Hoje', value: stats.todays_orders, sub: 'no ERP', color: 'bg-purple-500' },
    ...(isGestor ? [
      { icon: DollarSign, label: 'Receita Hoje', value: `R$ ${stats.revenue_today.toFixed(2).replace('.', ',')}`, sub: 'pedidos do ERP', color: 'bg-primary-600' },
    ] : []),
    { icon: ShoppingBag, label: 'Total Pedidos Chat', value: stats.total_customer_orders, sub: 'pedidos via IA', color: 'bg-teal-500' },
  ]

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500 mt-0.5">Visão geral do sistema</p>
        </div>
        <button onClick={() => load(true)} disabled={refreshing} className="btn-secondary flex items-center gap-2">
          <RefreshCw size={15} className={refreshing ? 'animate-spin' : ''} />
          Atualizar
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {statCards.map(s => <StatCard key={s.label} {...s} />)}
      </div>

      {/* Top Products */}
      <div className="card p-6">
        <h2 className="font-semibold text-gray-800 mb-4">Produtos Mais Vendidos</h2>
        <div className="space-y-3">
          {stats.top_products.length === 0 ? (
            <p className="text-gray-400 text-sm">Nenhuma venda registrada.</p>
          ) : stats.top_products.map((p, i) => (
            <div key={p.sku} className="flex items-center gap-3">
              <span className="w-6 h-6 bg-primary-100 text-primary-700 rounded-full text-xs font-bold flex items-center justify-center">{i + 1}</span>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-800">{p.name}</p>
                <p className="text-xs text-gray-400">{p.sku}</p>
              </div>
              <span className="text-sm font-semibold text-primary-600">{p.total_sold} un.</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
