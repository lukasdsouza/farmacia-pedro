import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { MessageCircle, Truck, Clock, Shield, ChevronRight, Pill } from 'lucide-react'
import ProductCard from '../components/ProductCard'
import { getProducts } from '../api/products'

const FEATURES = [
  { icon: Truck, title: 'Entrega Rápida', desc: 'Barra e Recreio em até 60min' },
  { icon: Clock, title: 'Plantão 24h', desc: 'Sempre disponível para você' },
  { icon: Shield, title: 'Produtos Originais', desc: '100% autorizados pela ANVISA' },
  { icon: MessageCircle, title: 'Atendimento por IA', desc: 'Chat inteligente 24/7' },
]

export default function Home() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    getProducts()
      .then(r => setProducts(r.data.slice(0, 6)))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <main>
      {/* Hero */}
      <section className="bg-gradient-to-br from-primary-600 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 py-16 flex flex-col lg:flex-row items-center gap-10">
          <div className="flex-1 text-center lg:text-left">
            <div className="inline-flex items-center gap-2 bg-white/20 rounded-full px-4 py-1.5 text-sm font-medium mb-6">
              <Pill size={14} /> Plantão 24 horas
            </div>
            <h1 className="text-4xl lg:text-5xl font-black leading-tight mb-4">
              Sua saúde<br />
              <span className="text-yellow-300">em boas mãos</span>
            </h1>
            <p className="text-primary-100 text-lg mb-8 max-w-md mx-auto lg:mx-0">
              Remédios, higiene e suplementos. Peça pelo chat com nossa IA ou retire na loja.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center lg:justify-start">
              <Link to="/chat" className="inline-flex items-center justify-center gap-2 bg-white text-primary-700 hover:bg-gray-50 font-bold px-6 py-3 rounded-xl transition-colors text-lg shadow-lg">
                <MessageCircle size={20} /> Falar com IA
              </Link>
              <Link to="/catalogo" className="inline-flex items-center justify-center gap-2 border-2 border-white/70 text-white hover:bg-white/10 font-semibold px-6 py-3 rounded-xl transition-colors">
                Ver Produtos <ChevronRight size={18} />
              </Link>
            </div>
          </div>

          <div className="hidden lg:flex flex-wrap gap-4 w-80">
            {FEATURES.map((f) => (
              <div key={f.title} className="bg-white/10 backdrop-blur rounded-xl p-4 w-36">
                <f.icon size={24} className="text-yellow-300 mb-2" />
                <p className="font-semibold text-sm">{f.title}</p>
                <p className="text-xs text-primary-200">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features mobile */}
      <section className="lg:hidden bg-primary-50 py-8">
        <div className="max-w-7xl mx-auto px-4 grid grid-cols-2 gap-3">
          {FEATURES.map((f) => (
            <div key={f.title} className="bg-white rounded-xl p-4 shadow-sm flex items-start gap-3">
              <div className="w-9 h-9 bg-primary-100 rounded-lg flex items-center justify-center shrink-0">
                <f.icon size={18} className="text-primary-600" />
              </div>
              <div>
                <p className="font-semibold text-sm text-gray-800">{f.title}</p>
                <p className="text-xs text-gray-500">{f.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Products */}
      <section className="max-w-7xl mx-auto px-4 py-12">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Produtos em Destaque</h2>
            <p className="text-gray-500 text-sm mt-1">Disponibilidade atualizada em tempo real</p>
          </div>
          <Link to="/catalogo" className="text-primary-600 hover:text-primary-800 font-semibold text-sm flex items-center gap-1">
            Ver todos <ChevronRight size={16} />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="card animate-pulse h-64">
                <div className="h-40 bg-gray-200" />
                <div className="p-4 space-y-2">
                  <div className="h-3 bg-gray-200 rounded w-1/3" />
                  <div className="h-4 bg-gray-200 rounded w-3/4" />
                  <div className="h-4 bg-gray-200 rounded w-1/2" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
            {products.map(p => <ProductCard key={p.sku} product={p} />)}
          </div>
        )}
      </section>

      {/* CTA Chat */}
      <section className="bg-primary-600 text-white py-14">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <MessageCircle size={48} className="mx-auto mb-4 text-yellow-300" />
          <h2 className="text-3xl font-black mb-3">Atendimento por IA 24/7</h2>
          <p className="text-primary-100 text-lg mb-8">
            Nossa IA conhece todo o estoque. Pergunte sobre disponibilidade, preços, e faça seu pedido diretamente pelo chat.
          </p>
          <Link to="/chat" className="inline-flex items-center gap-3 bg-white text-primary-700 hover:bg-gray-50 font-bold px-8 py-4 rounded-xl text-lg transition-colors shadow-xl">
            <MessageCircle size={22} /> Começar atendimento
          </Link>
        </div>
      </section>
    </main>
  )
}
