import { Link } from 'react-router-dom'
import { Phone, MapPin, Clock, MessageCircle } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300 mt-16">
      <div className="max-w-7xl mx-auto px-4 py-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
        {/* Brand */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-black text-sm">D</span>
            </div>
            <div>
              <span className="text-white font-black text-lg leading-none">Drogarias</span>
              <span className="block text-primary-400 font-bold text-xs tracking-widest">MAX</span>
            </div>
          </div>
          <p className="text-sm text-gray-400">
            Sua saúde em boas mãos. Medicamentos, higiene e suplementos com atendimento personalizado.
          </p>
        </div>

        {/* Links */}
        <div>
          <h4 className="text-white font-semibold mb-4">Produtos</h4>
          <ul className="space-y-2 text-sm">
            <li><Link to="/catalogo?category=Analgesico" className="hover:text-primary-400 transition-colors">Analgésicos</Link></li>
            <li><Link to="/catalogo?category=Antibiotico" className="hover:text-primary-400 transition-colors">Antibióticos</Link></li>
            <li><Link to="/catalogo?category=Higiene" className="hover:text-primary-400 transition-colors">Higiene</Link></li>
            <li><Link to="/catalogo?category=Suplemento" className="hover:text-primary-400 transition-colors">Suplementos</Link></li>
          </ul>
        </div>

        {/* Atendimento */}
        <div>
          <h4 className="text-white font-semibold mb-4">Atendimento</h4>
          <ul className="space-y-3 text-sm">
            <li className="flex items-center gap-2">
              <Phone size={14} className="text-primary-400 shrink-0" />
              (21) 3000-0000
            </li>
            <li className="flex items-start gap-2">
              <MapPin size={14} className="text-primary-400 shrink-0 mt-0.5" />
              Av. das Américas, 12.700 – Barra Blue
            </li>
            <li className="flex items-center gap-2">
              <Clock size={14} className="text-primary-400 shrink-0" />
              24 horas, 7 dias por semana
            </li>
          </ul>
        </div>

        {/* Chat */}
        <div>
          <h4 className="text-white font-semibold mb-4">Atendimento Online</h4>
          <p className="text-sm text-gray-400 mb-4">
            Consulte disponibilidade, preços e faça seu pedido pelo nosso chat com IA.
          </p>
          <Link to="/chat" className="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-800 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors">
            <MessageCircle size={16} />
            Abrir Chat
          </Link>
        </div>
      </div>

      <div className="border-t border-gray-800 py-4">
        <p className="text-center text-xs text-gray-500">
          © {new Date().getFullYear()} Drogarias Max. Todos os direitos reservados. CNPJ: 00.000.000/0001-00
        </p>
      </div>
    </footer>
  )
}
