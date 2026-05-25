import { useState, useEffect } from 'react'
import api from '../api/client'
import { RefreshCw, Play, AlertTriangle, TrendingDown, Package, BarChart2 } from 'lucide-react'

function Section({ title, icon: Icon, color, children }) {
  const [open, setOpen] = useState(true)
  return (
    <div className="card mb-4 overflow-hidden">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center gap-3 px-5 py-4 hover:bg-gray-50 transition-colors">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${color}`}>
          <Icon size={16} className="text-white" />
        </div>
        <span className="font-semibold text-gray-800 flex-1 text-left">{title}</span>
        <span className="text-gray-400 text-sm">{open ? '▲' : '▼'}</span>
      </button>
      {open && <div className="px-5 pb-5 pt-2 border-t border-gray-50">{children}</div>}
    </div>
  )
}

function Table({ rows, columns }) {
  if (!rows || rows.length === 0)
    return <p className="text-sm text-gray-400 py-2">Nenhum dado disponível.</p>
  return (
    <div className="overflow-x-auto rounded-lg border border-gray-100">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-gray-50 border-b border-gray-100">
            {columns.map(c => (
              <th key={c.key} className="px-3 py-2 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">{c.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-b border-gray-50 hover:bg-gray-50/50">
              {columns.map(c => (
                <td key={c.key} className={`px-3 py-2 text-gray-700 ${c.className || ''}`}>
                  {c.render ? c.render(row[c.key], row) : String(row[c.key] ?? '—')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function Reports() {
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')

  const loadReport = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.get('/reports/latest')
      setReport(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Erro ao carregar relatório')
    } finally {
      setLoading(false)
    }
  }

  const generateReport = async () => {
    setGenerating(true)
    try {
      await api.post('/reports/generate')
      await loadReport()
    } catch (e) {
      alert('Erro: ' + (e.response?.data?.detail || e.message))
    } finally {
      setGenerating(false)
    }
  }

  useEffect(() => { loadReport() }, [])

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Relatórios</h1>
          {report && <p className="text-sm text-gray-500 mt-0.5">Gerado em: {new Date(report.gerado_em).toLocaleString('pt-BR')}</p>}
        </div>
        <div className="flex gap-2">
          <button onClick={loadReport} disabled={loading} className="btn-secondary flex items-center gap-2">
            <RefreshCw size={15} className={loading ? 'animate-spin' : ''} /> Recarregar
          </button>
          <button onClick={generateReport} disabled={generating} className="btn-primary flex items-center gap-2">
            <Play size={15} /> {generating ? 'Gerando...' : 'Gerar Novo'}
          </button>
        </div>
      </div>

      {loading && (
        <div className="space-y-4">
          {[...Array(4)].map((_, i) => <div key={i} className="card h-24 animate-pulse bg-gray-100" />)}
        </div>
      )}

      {error && (
        <div className="card p-8 text-center">
          <AlertTriangle size={40} className="mx-auto text-orange-400 mb-3" />
          <p className="text-gray-600 font-medium">{error}</p>
          <button onClick={generateReport} disabled={generating} className="btn-primary mt-4 flex items-center gap-2 mx-auto">
            <Play size={15} /> Gerar Primeiro Relatório
          </button>
        </div>
      )}

      {report && (
        <>
          <Section title="Operacional — Estoque e Pedidos" icon={Package} color="bg-blue-500">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Estoque Baixo</p>
                <Table
                  rows={report.operacional?.estoque_baixo || []}
                  columns={[
                    { key: 'sku', label: 'SKU', className: 'font-mono text-xs' },
                    { key: 'name', label: 'Nome' },
                    { key: 'stock', label: 'Estoque', render: v => <span className="font-bold text-orange-600">{v}</span> },
                  ]}
                />
              </div>
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Pedidos Recentes</p>
                <Table
                  rows={report.operacional?.pedidos_recentes || []}
                  columns={[
                    { key: 'order_id', label: 'ID' },
                    { key: 'status', label: 'Status' },
                    { key: 'customer', label: 'Cliente' },
                  ]}
                />
              </div>
            </div>
          </Section>

          {report.auditoria_entrada && (
            <Section title="Auditoria de Entrada — Margens" icon={AlertTriangle} color="bg-orange-500">
              <Table
                rows={report.auditoria_entrada?.margem_baixa || []}
                columns={[
                  { key: 'sku', label: 'SKU', className: 'font-mono text-xs' },
                  { key: 'name', label: 'Nome' },
                  { key: 'margin_pct', label: 'Margem', render: v => <span className={`font-bold ${v < 0 ? 'text-red-600' : 'text-orange-600'}`}>{v?.toFixed(1)}%</span> },
                  { key: 'price', label: 'Preço', render: v => `R$ ${Number(v).toFixed(2).replace('.', ',')}` },
                  { key: 'unit_cost', label: 'Custo', render: v => `R$ ${Number(v).toFixed(2).replace('.', ',')}` },
                ]}
              />
            </Section>
          )}

          <Section title="Estratégico — Concorrência e Giro" icon={TrendingDown} color="bg-purple-500">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Quedas de Giro</p>
                <Table
                  rows={report.estrategista?.quedas_giro || []}
                  columns={[
                    { key: 'region', label: 'Região' },
                    { key: 'current_qty', label: 'Atual' },
                    { key: 'prev_qty', label: 'Anterior' },
                    { key: 'drop_pct', label: 'Queda', render: v => <span className="text-red-600 font-bold">{v?.toFixed(1)}%</span> },
                  ]}
                />
              </div>
              {report.estrategista?.alertas_concorrencia && (
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Alertas Concorrência</p>
                  <Table
                    rows={report.estrategista?.alertas_concorrencia || []}
                    columns={[
                      { key: 'sku', label: 'SKU', className: 'font-mono text-xs' },
                      { key: 'our_price', label: 'Nosso', render: v => `R$ ${Number(v).toFixed(2).replace('.', ',')}` },
                      { key: 'comp_price', label: 'Concorrente', render: v => <span className="text-red-600">R$ {Number(v).toFixed(2).replace('.', ',')}</span> },
                    ]}
                  />
                </div>
              )}
            </div>
          </Section>

          <Section title="Estoque — Parado e Recompras" icon={BarChart2} color="bg-teal-500">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Estoque Parado</p>
                <Table
                  rows={report.estoque?.estoque_parado || []}
                  columns={[
                    { key: 'sku', label: 'SKU', className: 'font-mono text-xs' },
                    { key: 'nome', label: 'Nome' },
                    { key: 'dias_sem_venda', label: 'Dias s/ venda', render: v => <span className="font-bold text-orange-600">{v}</span> },
                  ]}
                />
              </div>
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Sugestões de Recompra</p>
                <Table
                  rows={report.estoque?.recompras || []}
                  columns={[
                    { key: 'sku', label: 'SKU', className: 'font-mono text-xs' },
                    { key: 'nome', label: 'Nome' },
                    { key: 'quantidade_recompra', label: 'Qtd. Sugerida', render: v => <span className="font-bold text-primary-600">{v}</span> },
                  ]}
                />
              </div>
            </div>
          </Section>

          {report.regras?.alertas_bonus && report.regras.alertas_bonus.length > 0 && (
            <Section title="Alertas de Markup Elevado" icon={AlertTriangle} color="bg-red-500">
              <Table
                rows={report.regras.alertas_bonus}
                columns={[
                  { key: 'sku', label: 'SKU', className: 'font-mono text-xs' },
                  { key: 'nome', label: 'Nome' },
                  { key: 'markup_pct', label: 'Markup', render: v => <span className="font-bold text-red-600">{v?.toFixed(1)}%</span> },
                ]}
              />
            </Section>
          )}
        </>
      )}
    </div>
  )
}
