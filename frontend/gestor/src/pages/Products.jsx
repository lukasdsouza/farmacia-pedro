import { useState, useEffect } from 'react'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'
import { Search, AlertTriangle, RefreshCw, Edit2, Check, X } from 'lucide-react'

export default function Products() {
  const { isGestor } = useAuth()
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [editingStock, setEditingStock] = useState(null)
  const [stockValue, setStockValue] = useState('')
  const [savingStock, setSavingStock] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const params = search ? { q: search } : {}
      const res = await api.get('/products', { params })
      setProducts(res.data)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const handleSearch = (e) => {
    e.preventDefault()
    load()
  }

  const startEditStock = (sku, current) => {
    setEditingStock(sku)
    setStockValue(String(current))
  }

  const saveStock = async (sku) => {
    const val = parseInt(stockValue, 10)
    if (isNaN(val) || val < 0) return
    setSavingStock(true)
    try {
      await api.patch(`/products/${sku}/stock`, { stock: val })
      setProducts(prev => prev.map(p => p.sku === sku ? { ...p, stock: val } : p))
      setEditingStock(null)
    } catch (e) {
      alert('Erro ao atualizar estoque: ' + (e.response?.data?.detail || e.message))
    } finally {
      setSavingStock(false)
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Produtos</h1>
          <p className="text-sm text-gray-500 mt-0.5">{products.length} produto(s)</p>
        </div>
        <button onClick={load} disabled={loading} className="btn-secondary flex items-center gap-2">
          <RefreshCw size={15} className={loading ? 'animate-spin' : ''} /> Atualizar
        </button>
      </div>

      <div className="card p-4 mb-4">
        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="relative flex-1 max-w-sm">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="search"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Buscar por nome..."
              className="input pl-9"
            />
          </div>
          <button type="submit" className="btn-primary">Buscar</button>
          {search && <button type="button" onClick={() => { setSearch(''); load() }} className="btn-secondary">Limpar</button>}
        </form>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100">
              {['SKU', 'Nome', 'Categoria', 'Preço', 'Custo', 'Estoque', ...(isGestor ? ['Margem'] : []), 'Ação'].map(h => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              [...Array(6)].map((_, i) => (
                <tr key={i} className="border-b border-gray-50">
                  {[...Array(isGestor ? 8 : 7)].map((__, j) => (
                    <td key={j} className="px-4 py-3"><div className="h-4 bg-gray-100 rounded animate-pulse" /></td>
                  ))}
                </tr>
              ))
            ) : products.map(p => {
              const lowStock = p.stock < 10
              const margin = p.avg_cost > 0 ? ((p.price - p.avg_cost) / p.price * 100) : 0

              return (
                <tr key={p.sku} className={`table-row ${lowStock ? 'bg-orange-50/50' : ''}`}>
                  <td className="px-4 py-3 font-mono text-xs text-gray-500">{p.sku}</td>
                  <td className="px-4 py-3 font-medium text-gray-800">
                    {p.name}
                    {lowStock && <span className="ml-2 inline-flex items-center gap-1 text-xs text-orange-600"><AlertTriangle size={11} />Baixo</span>}
                  </td>
                  <td className="px-4 py-3 text-gray-500">{p.category}</td>
                  <td className="px-4 py-3 font-semibold text-primary-600">R$ {p.price.toFixed(2).replace('.', ',')}</td>
                  {isGestor && <td className="px-4 py-3 text-gray-500">R$ {p.avg_cost.toFixed(2).replace('.', ',')}</td>}
                  <td className="px-4 py-3">
                    <span className={`font-semibold ${lowStock ? 'text-orange-600' : 'text-gray-800'}`}>{p.stock}</span>
                  </td>
                  {isGestor && (
                    <td className="px-4 py-3">
                      <span className={`text-xs font-semibold ${margin < 15 ? 'text-red-600' : 'text-green-600'}`}>
                        {margin.toFixed(1)}%
                      </span>
                    </td>
                  )}
                  <td className="px-4 py-3">
                    {editingStock === p.sku ? (
                      <div className="flex items-center gap-1">
                        <input
                          type="number"
                          value={stockValue}
                          onChange={e => setStockValue(e.target.value)}
                          className="w-16 border border-primary-300 rounded px-2 py-1 text-xs focus:outline-none focus:border-primary-500"
                          min={0}
                          autoFocus
                          onKeyDown={e => { if (e.key === 'Enter') saveStock(p.sku); if (e.key === 'Escape') setEditingStock(null) }}
                        />
                        <button onClick={() => saveStock(p.sku)} disabled={savingStock} className="text-green-600 hover:text-green-800 p-1">
                          <Check size={14} />
                        </button>
                        <button onClick={() => setEditingStock(null)} className="text-gray-400 hover:text-gray-600 p-1">
                          <X size={14} />
                        </button>
                      </div>
                    ) : (
                      <button onClick={() => startEditStock(p.sku, p.stock)} className="text-xs text-primary-600 hover:text-primary-800 flex items-center gap-1 font-medium">
                        <Edit2 size={12} /> Estoque
                      </button>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
