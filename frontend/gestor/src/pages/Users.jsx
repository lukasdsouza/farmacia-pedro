import { useState, useEffect } from 'react'
import api from '../api/client'
import { UserPlus, Edit2, Trash2, RefreshCw, X, Check } from 'lucide-react'

const ROLE_COLORS = {
  gestor: 'bg-purple-100 text-purple-700',
  funcionario: 'bg-blue-100 text-blue-700',
}

function Modal({ title, onClose, children }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-gray-900/50" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-2xl w-full max-w-md mx-4">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h3 className="font-semibold text-gray-800">{title}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><X size={18} /></button>
        </div>
        <div className="px-6 py-5">{children}</div>
      </div>
    </div>
  )
}

export default function Users() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [editUser, setEditUser] = useState(null)
  const [form, setForm] = useState({ username: '', email: '', password: '', role: 'funcionario', nome_completo: '' })
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState('')

  const load = async () => {
    setLoading(true)
    try {
      const res = await api.get('/users')
      setUsers(res.data)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const openCreate = () => {
    setForm({ username: '', email: '', password: '', role: 'funcionario', nome_completo: '' })
    setFormError('')
    setShowCreate(true)
  }

  const openEdit = (u) => {
    setForm({ username: u.username, email: u.email, password: '', role: u.role, nome_completo: u.nome_completo })
    setFormError('')
    setEditUser(u)
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    setSaving(true)
    setFormError('')
    try {
      await api.post('/users', form)
      setShowCreate(false)
      load()
    } catch (e) {
      setFormError(e.response?.data?.detail || 'Erro ao criar usuário')
    } finally {
      setSaving(false)
    }
  }

  const handleEdit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setFormError('')
    const payload = { email: form.email, role: form.role, nome_completo: form.nome_completo }
    if (form.password) payload.password = form.password
    try {
      await api.patch(`/users/${editUser.id}`, payload)
      setEditUser(null)
      load()
    } catch (e) {
      setFormError(e.response?.data?.detail || 'Erro ao atualizar usuário')
    } finally {
      setSaving(false)
    }
  }

  const toggleActive = async (u) => {
    try {
      await api.patch(`/users/${u.id}`, { is_active: !u.is_active })
      load()
    } catch (e) { alert('Erro: ' + (e.response?.data?.detail || e.message)) }
  }

  const deleteUser = async (u) => {
    if (!confirm(`Deletar usuário "${u.username}"? Esta ação não pode ser desfeita.`)) return
    try {
      await api.delete(`/users/${u.id}`)
      load()
    } catch (e) { alert('Erro: ' + (e.response?.data?.detail || e.message)) }
  }

  const UserForm = ({ onSubmit, isEdit }) => (
    <form onSubmit={onSubmit} className="space-y-4">
      {formError && <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2 rounded-lg">{formError}</div>}
      {!isEdit && (
        <div>
          <label className="label">Usuário</label>
          <input className="input" value={form.username} onChange={e => setForm(f => ({ ...f, username: e.target.value }))} required minLength={3} />
        </div>
      )}
      <div>
        <label className="label">Nome completo</label>
        <input className="input" value={form.nome_completo} onChange={e => setForm(f => ({ ...f, nome_completo: e.target.value }))} />
      </div>
      <div>
        <label className="label">Email</label>
        <input type="email" className="input" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} required />
      </div>
      <div>
        <label className="label">{isEdit ? 'Nova senha (deixe em branco para manter)' : 'Senha'}</label>
        <input type="password" className="input" value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} {...(!isEdit && { required: true, minLength: 6 })} />
      </div>
      <div>
        <label className="label">Perfil</label>
        <select className="input" value={form.role} onChange={e => setForm(f => ({ ...f, role: e.target.value }))}>
          <option value="funcionario">Funcionário</option>
          <option value="gestor">Gestor</option>
        </select>
      </div>
      <div className="flex justify-end gap-2 pt-2">
        <button type="button" onClick={() => isEdit ? setEditUser(null) : setShowCreate(false)} className="btn-secondary">Cancelar</button>
        <button type="submit" disabled={saving} className="btn-primary">{saving ? 'Salvando...' : isEdit ? 'Salvar' : 'Criar Usuário'}</button>
      </div>
    </form>
  )

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Usuários</h1>
          <p className="text-sm text-gray-500 mt-0.5">{users.length} usuário(s)</p>
        </div>
        <div className="flex gap-2">
          <button onClick={load} disabled={loading} className="btn-secondary flex items-center gap-2">
            <RefreshCw size={15} className={loading ? 'animate-spin' : ''} />
          </button>
          <button onClick={openCreate} className="btn-primary flex items-center gap-2">
            <UserPlus size={15} /> Novo Usuário
          </button>
        </div>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100">
              {['Usuário', 'Nome', 'Email', 'Perfil', 'Status', 'Criado em', 'Ações'].map(h => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              [...Array(3)].map((_, i) => (
                <tr key={i} className="border-b border-gray-50">
                  {[...Array(7)].map((__, j) => (
                    <td key={j} className="px-4 py-3"><div className="h-4 bg-gray-100 rounded animate-pulse" /></td>
                  ))}
                </tr>
              ))
            ) : users.map(u => (
              <tr key={u.id} className="table-row">
                <td className="px-4 py-3 font-mono text-sm font-semibold text-gray-800">{u.username}</td>
                <td className="px-4 py-3 text-gray-700">{u.nome_completo || '—'}</td>
                <td className="px-4 py-3 text-gray-500">{u.email}</td>
                <td className="px-4 py-3">
                  <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${ROLE_COLORS[u.role] || 'bg-gray-100 text-gray-600'}`}>
                    {u.role}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <button onClick={() => toggleActive(u)} className={`text-xs font-semibold px-2.5 py-1 rounded-full transition-colors ${u.is_active ? 'bg-green-100 text-green-700 hover:bg-green-200' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'}`}>
                    {u.is_active ? 'Ativo' : 'Inativo'}
                  </button>
                </td>
                <td className="px-4 py-3 text-gray-400 text-xs">
                  {new Date(u.created_at).toLocaleDateString('pt-BR')}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1">
                    <button onClick={() => openEdit(u)} className="p-1.5 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors">
                      <Edit2 size={14} />
                    </button>
                    <button onClick={() => deleteUser(u)} className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                      <Trash2 size={14} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showCreate && (
        <Modal title="Novo Usuário" onClose={() => setShowCreate(false)}>
          <UserForm onSubmit={handleCreate} isEdit={false} />
        </Modal>
      )}
      {editUser && (
        <Modal title={`Editar: ${editUser.username}`} onClose={() => setEditUser(null)}>
          <UserForm onSubmit={handleEdit} isEdit />
        </Modal>
      )}
    </div>
  )
}
