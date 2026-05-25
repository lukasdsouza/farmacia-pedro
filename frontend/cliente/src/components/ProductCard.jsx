import { ShoppingBag, Package } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const CATEGORY_COLORS = {
  Analgesico: 'bg-blue-100 text-blue-700',
  Antibiotico: 'bg-purple-100 text-purple-700',
  Higiene: 'bg-cyan-100 text-cyan-700',
  Suplemento: 'bg-orange-100 text-orange-700',
}

export default function ProductCard({ product }) {
  const navigate = useNavigate()
  const inStock = product.stock > 0
  const badgeClass = CATEGORY_COLORS[product.category] || 'bg-gray-100 text-gray-600'

  return (
    <div className="card hover:shadow-md transition-shadow group">
      {/* Image placeholder */}
      <div className="h-40 bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center relative overflow-hidden">
        <Package size={48} className="text-primary-300" />
        {!inStock && (
          <div className="absolute inset-0 bg-gray-900/40 flex items-center justify-center">
            <span className="text-white font-semibold text-sm bg-gray-800 px-3 py-1 rounded-full">Indisponível</span>
          </div>
        )}
        <span className={`absolute top-2 left-2 text-xs font-medium px-2 py-0.5 rounded-full ${badgeClass}`}>
          {product.category}
        </span>
      </div>

      <div className="p-4">
        <p className="text-xs text-gray-400 font-mono mb-1">{product.sku}</p>
        <h3 className="font-semibold text-gray-800 text-sm mb-2 line-clamp-2">{product.name}</h3>

        <div className="flex items-center justify-between mt-3">
          <div>
            <span className="text-primary-600 font-bold text-lg">
              R$ {product.price.toFixed(2).replace('.', ',')}
            </span>
          </div>
          <span className={`text-xs font-medium ${inStock ? 'text-green-600' : 'text-red-500'}`}>
            {inStock ? `${product.stock} em estoque` : 'Sem estoque'}
          </span>
        </div>

        <button
          onClick={() => navigate('/chat')}
          disabled={!inStock}
          className="mt-3 w-full flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-800 disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed text-white font-semibold py-2 rounded-lg text-sm transition-colors"
        >
          <ShoppingBag size={15} />
          {inStock ? 'Pedir pelo Chat' : 'Indisponível'}
        </button>
      </div>
    </div>
  )
}
