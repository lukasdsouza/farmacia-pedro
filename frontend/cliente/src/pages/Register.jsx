import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { User, Mail, Lock, Phone, MapPin, Eye, EyeOff } from 'lucide-react'
import { registerCustomer } from '../api/customers'
import { useCustomerAuth } from '../contexts/CustomerAuthContext'

export default function Register() {
  const navigate = useNavigate()
  const { login } = useCustomerAuth()
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    nome: '', email: '', telefone: '', senha: '',
    endereco_rua: '', endereco_numero: '', endereco_complemento: '',
    endereco_bairro: '', endereco_cidade: 'Rio de Janeiro',
  })

  const set = (field) => (e) => setForm(f => ({ ...f, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (form.senha.length < 6) { setError('Senha deve ter pelo menos 6 caracteres'); return }
    setLoading(true)
    try {
      const res = await registerCustomer(form)
      login(res.data.access_token, res.data.customer)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao criar conta. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="max-w-xl mx-auto px-4 py-10">
      <div className="card p-8">
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-3">
            <User size={28} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Criar conta</h1>
          <p className="text-gray-500 text-sm mt-1">Seus dados ficam salvos pra facilitar seus pedidos</p>
        </div>

        {error && (
          <div className="mb-5 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <section>
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">Dados pessoais</h2>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nome completo *</label>
                <div className="relative">
                  <User size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input required value={form.nome} onChange={set('nome')} placeholder="Seu nome completo"
                    className="w-full pl-9 pr-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:border-primary-500 text-sm" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">E-mail *</label>
                <div className="relative">
                  <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input required type="email" value={form.email} onChange={set('email')} placeholder="seu@email.com"
                    className="w-full pl-9 pr-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:border-primary-500 text-sm" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Telefone / WhatsApp</label>
                <div className="relative">
                  <Phone size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input value={form.telefone} onChange={set('telefone')} placeholder="(21) 99999-0000"
                    className="w-full pl-9 pr-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:border-primary-500 text-sm" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Senha *</label>
                <div className="relative">
                  <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input required type={showPass ? 'text' : 'password'} value={form.senha} onChange={set('senha')} placeholder="Mínimo 6 caracteres"
                    className="w-full pl-9 pr-10 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:border-primary-500 text-sm" />
                  <button type="button" onClick={() => setShowPass(v => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                    {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-1">Endereço de entrega</h2>
            <p className="text-xs text-gray-400 mb-3">Opcional — facilita futuros pedidos</p>
            <div className="space-y-3">
              <div className="flex gap-3">
                <div className="flex-1">
                  <label className="block text-xs font-medium text-gray-600 mb-1">Rua / Avenida</label>
                  <input value={form.endereco_rua} onChange={set('endereco_rua')} placeholder="Rua das Flores"
                    className="w-full px-3 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:border-primary-500 text-sm" />
                </div>
                <div className="w-24">
                  <label className="block text-xs font-medium text-gray-600 mb-1">Número</label>
                  <input value={form.endereco_numero} onChange={set('endereco_numero')} placeholder="100"
                    className="w-full px-3 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:border-primary-500 text-sm" />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Complemento</label>
                <input value={form.endereco_complemento} onChange={set('endereco_complemento')} placeholder="Apto 201, Bloco B..."
                  className="w-full px-3 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:border-primary-500 text-sm" />
              </div>
              <div className="flex gap-3">
                <div className="flex-1">
                  <label className="block text-xs font-medium text-gray-600 mb-1">Bairro</label>
                  <input value={form.endereco_bairro} onChange={set('endereco_bairro')} placeholder="Barra da Tijuca"
                    className="w-full px-3 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:border-primary-500 text-sm" />
                </div>
                <div className="flex-1">
                  <label className="block text-xs font-medium text-gray-600 mb-1">Cidade</label>
                  <input value={form.endereco_cidade} onChange={set('endereco_cidade')}
                    className="w-full px-3 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:border-primary-500 text-sm" />
                </div>
              </div>
            </div>
          </section>

          <button type="submit" disabled={loading}
            className="w-full bg-primary-600 hover:bg-primary-800 disabled:bg-gray-300 text-white font-semibold py-3 rounded-lg transition-colors text-sm">
            {loading ? 'Criando conta...' : 'Criar minha conta'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-5">
          Já tem conta?{' '}
          <Link to="/entrar" className="text-primary-600 hover:underline font-medium">Entrar</Link>
        </p>
      </div>
    </main>
  )
}
