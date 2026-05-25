import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Mail, Lock, Eye, EyeOff } from 'lucide-react'
import { loginCustomer } from '../api/customers'
import { useCustomerAuth } from '../contexts/CustomerAuthContext'

export default function Login() {
  const navigate = useNavigate()
  const { login } = useCustomerAuth()
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await loginCustomer(email, senha)
      login(res.data.access_token, res.data.customer)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Email ou senha incorretos.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="max-w-md mx-auto px-4 py-16">
      <div className="card p-8">
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-3">
            <Lock size={24} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Entrar</h1>
          <p className="text-gray-500 text-sm mt-1">Acesse sua conta Drogarias Max</p>
        </div>

        {error && (
          <div className="mb-5 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">E-mail</label>
            <div className="relative">
              <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input required type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="seu@email.com"
                className="w-full pl-9 pr-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:border-primary-500 text-sm" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Senha</label>
            <div className="relative">
              <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input required type={showPass ? 'text' : 'password'} value={senha} onChange={e => setSenha(e.target.value)} placeholder="Sua senha"
                className="w-full pl-9 pr-10 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:border-primary-500 text-sm" />
              <button type="button" onClick={() => setShowPass(v => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <button type="submit" disabled={loading}
            className="w-full bg-primary-600 hover:bg-primary-800 disabled:bg-gray-300 text-white font-semibold py-3 rounded-lg transition-colors text-sm">
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>

        <div className="mt-5 space-y-2 text-center text-sm text-gray-500">
          <p>
            Não tem conta?{' '}
            <Link to="/cadastro" className="text-primary-600 hover:underline font-medium">Criar conta grátis</Link>
          </p>
          <p className="text-xs text-gray-400">
            Demo: maria@email.com / senha123
          </p>
        </div>
      </div>
    </main>
  )
}
