import { useState, useEffect } from 'react'
import api from '../api/client'
import { MessageSquare, ChevronRight, RefreshCw, Bot, User } from 'lucide-react'

export default function ChatSessions() {
  const [sessions, setSessions] = useState([])
  const [selected, setSelected] = useState(null)
  const [sessionData, setSessionData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadingSession, setLoadingSession] = useState(false)

  const loadSessions = async () => {
    setLoading(true)
    try {
      const res = await api.get('/chat/sessions')
      setSessions(res.data.sessions || [])
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  const loadSession = async (id) => {
    setSelected(id)
    setLoadingSession(true)
    try {
      const res = await api.get(`/chat/sessions/${id}`)
      setSessionData(res.data)
    } catch (e) { console.error(e) }
    finally { setLoadingSession(false) }
  }

  useEffect(() => { loadSessions() }, [])

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Atendimentos</h1>
          <p className="text-sm text-gray-500 mt-0.5">{sessions.length} sessão(ões) de chat</p>
        </div>
        <button onClick={loadSessions} disabled={loading} className="btn-secondary flex items-center gap-2">
          <RefreshCw size={15} className={loading ? 'animate-spin' : ''} /> Atualizar
        </button>
      </div>

      <div className="flex gap-4 h-[calc(100vh-220px)] min-h-[400px]">
        {/* Sessions list */}
        <div className="w-72 shrink-0 card overflow-y-auto">
          {loading ? (
            <div className="p-4 space-y-2">
              {[...Array(5)].map((_, i) => <div key={i} className="h-12 bg-gray-100 rounded-lg animate-pulse" />)}
            </div>
          ) : sessions.length === 0 ? (
            <div className="p-8 text-center">
              <MessageSquare size={32} className="mx-auto text-gray-300 mb-2" />
              <p className="text-gray-400 text-sm">Nenhuma sessão ainda</p>
            </div>
          ) : (
            <ul className="py-2">
              {sessions.map(s => (
                <li key={s}>
                  <button
                    onClick={() => loadSession(s)}
                    className={`w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-gray-50 transition-colors ${selected === s ? 'bg-primary-50 border-r-2 border-primary-600' : ''}`}
                  >
                    <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center shrink-0">
                      <MessageSquare size={14} className="text-primary-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-medium truncate ${selected === s ? 'text-primary-700' : 'text-gray-700'}`}>
                        {s}
                      </p>
                    </div>
                    <ChevronRight size={14} className="text-gray-300 shrink-0" />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Session detail */}
        <div className="flex-1 card overflow-hidden flex flex-col">
          {!selected ? (
            <div className="flex-1 flex items-center justify-center text-center">
              <div>
                <MessageSquare size={48} className="mx-auto text-gray-200 mb-3" />
                <p className="text-gray-400">Selecione uma sessão para visualizar</p>
              </div>
            </div>
          ) : loadingSession ? (
            <div className="flex-1 flex items-center justify-center">
              <RefreshCw size={24} className="text-gray-300 animate-spin" />
            </div>
          ) : sessionData ? (
            <>
              <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-3">
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                  <MessageSquare size={14} className="text-primary-600" />
                </div>
                <div>
                  <p className="font-semibold text-gray-800 text-sm">{selected}</p>
                  <p className="text-xs text-gray-400">
                    Estado: <span className="font-medium text-primary-600">{sessionData.flow_state}</span>
                    · {sessionData.messages.length} mensagem(s)
                  </p>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
                {sessionData.messages.length === 0 ? (
                  <p className="text-gray-400 text-sm text-center py-8">Nenhuma mensagem nesta sessão</p>
                ) : sessionData.messages.map((m, i) => (
                  <div key={i} className={`flex items-end gap-2 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
                    <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 ${m.role === 'user' ? 'bg-gray-600' : 'bg-primary-600'}`}>
                      {m.role === 'user' ? <User size={13} className="text-white" /> : <Bot size={13} className="text-white" />}
                    </div>
                    <div className={`max-w-sm px-4 py-2 rounded-2xl text-sm whitespace-pre-line ${
                      m.role === 'user'
                        ? 'bg-gray-700 text-white rounded-br-sm'
                        : 'bg-white border border-gray-100 text-gray-800 rounded-bl-sm shadow-sm'
                    }`}>
                      {m.content}
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : null}
        </div>
      </div>
    </div>
  )
}
