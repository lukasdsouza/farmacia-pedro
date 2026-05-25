import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { User, Mail, Phone, MapPin, Lock, Save, LogOut, Eye, EyeOff } from 'lucide-react'
import { updateMyProfile } from '../api/customers'
import { useCustomerAuth } from '../contexts/CustomerAuthContext'

export default function Profile() {
  const navigate = useNavigate()
  const { token, customer, updateCustomer, logout } = useCustomerAuth()
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    nome: customer?.nome || '',
    telefone: customer?.telefone || '',
    senha: '',
    endereco_rua: customer?.endereco_rua || '',
    endereco_numero: customer?.endereco_numero || '',
    endereco_complemento: customer?.endereco_complemento || '',
    endereco_bairro: customer?.endereco_bairro || '',
    endereco_cidade: customer?.endereco_cidade || 'Rio de Janeiro',
  })

  const set = (field) => (e) => setForm(f => ({ ...f, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess(false)
    const payload = { ...form }
    if (!payload.senha) delete payload.senha
    setLoading(true)
    try {
      const res = await updateMyProfile(token, payload)
      updateCustomer(res.data)
      setSuccess(true)
      setForm(f => ({ ...f, senha: '' }))
      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao salvar. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  if (!customer) {
    navigate('/entrar')
    return null
  }

  return (
    <main className="max-w-xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Meu perfil</h1>
          <p className="text-gray-500 text-sm">{customer.email}</p>
        </div>
        <button onClick={handleLogout}
          className="flex items-center gap-2 text-sm text-red-600 hover:text-red-800 border border-red-200 hover:border-red-400 px-3 py-2 rounded-lg transition-colors">
          <LogOut size={15} /> Sair
        </button>
      </div>

      {success && (
        <div className="mb-5 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
          ✅ Dados salvos com sucesso!
        </div>
      )}
      {error && (
        <div className="mb-5 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="card p-6 space-y-4">
          <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Dados pessoais</h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nome completo</label>
            <div className="relative">
              <User size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input required value={form.nome} onChange={set('nome')}
                className="w-full pl-9 pr-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:border-primary-500 text-sm" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">E-mail</label>
            <div className="relative">
              <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input disabled value={customer.email}
                className="w-full pl-9 pr-4 py-2.5 border border-gray-200 rounded-lg bg-gray-50 text-gray-500 text-sm cursor-not-allowed" />
            </div>
            <p className="text-xs text-gray-400 mt-1">O e-mail não pode ser alterado</p>
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
            <label className="block text-sm font-medium text-gray-700 mb-1">Nova senha</label>
            <div className="relative">
              <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input type={showPass ? 'text' : 'password'} value={form.senha} onChange={set('senha')}
                placeholder="Deixe em branco para manter a atual"
                className="w-full pl-9 pr-10 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:border-primary-500 text-sm" />
              <button type="button" onClick={() => setShowPass(v => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
        </div>

        <div className="card p-6 space-y-4">
          <div className="flex items-center gap-2">
            <MapPin size={16} className="text-primary-600" />
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Endereço de entrega</h2>
          </div>

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
            <input value={form.endereco_complemento} onChange={set('endereco_complemento')} placeholder="Apto 201, Casa..."
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

        <button type="submit" disabled={loading}
          className="w-full flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-800 disabled:bg-gray-300 text-white font-semibold py-3 rounded-lg transition-colors text-sm">
          <Save size={16} />
          {loading ? 'Salvando...' : 'Salvar alterações'}
        </button>
      </form>
    </main>
  )
}
