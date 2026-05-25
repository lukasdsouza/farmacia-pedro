import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Search, Filter, X } from 'lucide-react'
import ProductCard from '../components/ProductCard'
import { getProducts, getCategories } from '../api/products'

export default function Catalog() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState(searchParams.get('q') || '')

  const category = searchParams.get('category') || ''

  useEffect(() => {
    getCategories().then(r => setCategories(r.data)).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    const params = {}
    if (category) params.category = category
    if (search) params.q = search
    getProducts(params)
      .then(r => setProducts(r.data))
      .catch(() => setProducts([]))
      .finally(() => setLoading(false))
  }, [category, search])

  useEffect(() => {
    const q = searchParams.get('q')
    if (q !== null) setSearch(q)
  }, [searchParams])

  const handleSearch = (e) => {
    e.preventDefault()
    const params = {}
    if (search) params.q = search
    if (category) params.category = category
    setSearchParams(params)
  }

  const setCategory = (cat) => {
    const params = {}
    if (cat) params.category = cat
    if (search) params.q = search
    setSearchParams(params)
  }

  return (
    <main className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Todos os Produtos</h1>
        <p className="text-gray-500">
          {loading ? 'Carregando...' : `${products.length} produto(s) encontrado(s)`}
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar */}
        <aside className="lg:w-56 shrink-0">
          <div className="card p-4">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <Filter size={15} /> Filtrar por
            </h3>

            {/* Search */}
            <form onSubmit={handleSearch} className="mb-4">
              <div className="relative">
                <input
                  type="search"
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  placeholder="Buscar produto..."
                  className="w-full pl-3 pr-8 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-primary-500"
                />
                {search && (
                  <button type="button" onClick={() => { setSearch(''); setSearchParams(category ? { category } : {}); }} className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                    <X size={14} />
                  </button>
                )}
              </div>
            </form>

            {/* Categories */}
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Categorias</p>
              <ul className="space-y-1">
                <li>
                  <button
                    onClick={() => setCategory('')}
                    className={`w-full text-left px-3 py-1.5 rounded-lg text-sm transition-colors ${!category ? 'bg-primary-600 text-white font-semibold' : 'text-gray-700 hover:bg-primary-50'}`}
                  >
                    Todas
                  </button>
                </li>
                {categories.map(cat => (
                  <li key={cat}>
                    <button
                      onClick={() => setCategory(cat)}
                      className={`w-full text-left px-3 py-1.5 rounded-lg text-sm transition-colors ${category === cat ? 'bg-primary-600 text-white font-semibold' : 'text-gray-700 hover:bg-primary-50'}`}
                    >
                      {cat}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </aside>

        {/* Grid */}
        <div className="flex-1">
          {loading ? (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="card animate-pulse h-64">
                  <div className="h-40 bg-gray-200" />
                  <div className="p-4 space-y-2">
                    <div className="h-3 bg-gray-200 rounded w-1/3" />
                    <div className="h-4 bg-gray-200 rounded w-3/4" />
                  </div>
                </div>
              ))}
            </div>
          ) : products.length === 0 ? (
            <div className="text-center py-20">
              <Search size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500 text-lg font-medium">Nenhum produto encontrado</p>
              <p className="text-gray-400 text-sm mt-1">Tente outros termos ou <button onClick={() => { setSearch(''); setSearchParams({}); }} className="text-primary-600 hover:underline">limpar filtros</button></p>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {products.map(p => <ProductCard key={p.sku} product={p} />)}
            </div>
          )}
        </div>
      </div>
    </main>
  )
}
