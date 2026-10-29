import { useEffect, useState, useMemo } from 'react'
import { api } from '../services/api'
import { parseDateUTC } from '../utils/date'
import { ChefHat, CheckCircle2, Clock, Loader2, RefreshCw } from 'lucide-react'

const INTERVALO_ATUALIZACAO = 10000 // 10 segundos

export function CozinhaPage() {
  const [pedidosPendentes, setPedidosPendentes] = useState([])
  const [produtos, setProdutos] = useState([])
  const [loading, setLoading] = useState(true)
  const [updatingId, setUpdatingId] = useState(null)
  const [error, setError] = useState('')

  const produtosMap = useMemo(() => {
    const map = new Map()
    produtos.forEach((p) => map.set(p.id_produto, p))
    return map
  }, [produtos])

  async function loadData() {
    try {
      setError('')
      const [pedidosRes, produtosRes] = await Promise.all([
        api.get('/pedidos/'),
        api.get('/produtos/')
      ])

      setProdutos(produtosRes.data)
      const pendentes = pedidosRes.data.filter((p) => p.status === 'pendente')
      setPedidosPendentes(pendentes)
    } catch {
      setError('Erro ao carregar os dados da cozinha. Verifique a conexão com a API.')
    } finally {
      setLoading(false)
    }
  }

  // Auto-refresh logic
  useEffect(() => {
    const timerInit = setTimeout(() => {
      loadData()
    }, 0)

    const timer = setInterval(() => {
      loadData()
    }, INTERVALO_ATUALIZACAO)

    return () => {
      clearTimeout(timerInit)
      clearInterval(timer)
    }
  }, [])

  async function marcarComoPronto(idNotaFiscal) {
    setUpdatingId(idNotaFiscal)
    try {
      await api.patch(`/pedidos/${idNotaFiscal}/status`, { status: 'pronto' })
      setPedidosPendentes((prev) => prev.filter((p) => p.id_nota_fiscal !== idNotaFiscal))
    } catch {
      alert('Erro ao atualizar o status do pedido.')
    } finally {
      setUpdatingId(null)
    }
  }

  // Filtrar apenas pedidos que tem itens que exigem preparo
  const pedidosComPreparo = pedidosPendentes.map((pedido) => {
    const itens = pedido.itens || []
    const itensParaPreparo = itens.filter((item) => {
      const produto = produtosMap.get(item.id_produto)
      return produto?.exige_preparo === true
    })

    return {
      ...pedido,
      itensParaPreparo
    }
  }).filter((pedido) => pedido.itensParaPreparo.length > 0)

  if (loading && pedidosPendentes.length === 0) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-brand-500" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-3">
            <ChefHat className="h-8 w-8 text-orange-500" />
            Monitor de Preparo (Cozinha)
          </h1>
          <p className="mt-1 text-slate-500">
            Acompanhe em tempo real os pedidos que exigem preparo (chapa, cozinha, etc).
          </p>
        </div>
        <button
          onClick={loadData}
          className="flex items-center gap-2 rounded-lg bg-white border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          Atualizar Agora
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {pedidosComPreparo.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white py-24 text-center shadow-sm">
          <div className="flex h-20 w-20 items-center justify-center rounded-full bg-slate-50 mb-4">
            <CheckCircle2 className="h-10 w-10 text-emerald-500" />
          </div>
          <h2 className="text-xl font-bold text-slate-900">Nenhum pedido pendente!</h2>
          <p className="text-slate-500 mt-1 max-w-sm">
            A cozinha está limpa. Novos pedidos que exigem preparo aparecerão aqui automaticamente.
          </p>
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {pedidosComPreparo.map((pedido) => {
            const dataPedido = parseDateUTC(pedido.data_hora)
            const tempoEspera = Math.max(0, Math.floor((new Date() - dataPedido) / 60000))
            const isUrgente = tempoEspera > 15

            return (
              <div 
                key={pedido.id_nota_fiscal} 
                className={`flex flex-col rounded-2xl border-2 bg-white shadow-sm overflow-hidden transition-all ${
                  isUrgente ? 'border-red-400 shadow-red-100' : 'border-slate-200 hover:border-brand-300'
                }`}
              >
                {/* Header do Card */}
                <div className={`px-4 py-3 border-b ${isUrgente ? 'bg-red-50 border-red-100' : 'bg-slate-50 border-slate-100'}`}>
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Pedido</span>
                      <p className="text-2xl font-black text-slate-900 leading-none mt-1">#{pedido.id_nota_fiscal}</p>
                    </div>
                    <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                      isUrgente ? 'bg-red-100 text-red-700' : 'bg-slate-200 text-slate-700'
                    }`}>
                      <Clock className="h-3.5 w-3.5" />
                      {tempoEspera} min
                    </div>
                  </div>
                </div>

                {/* Lista de Itens */}
                <div className="flex-1 p-4 bg-white">
                  <ul className="space-y-3">
                    {pedido.itensParaPreparo.map((item) => {
                      const produto = produtosMap.get(item.id_produto)
                      return (
                        <li key={item.id_item_pedido} className="flex items-start gap-3">
                          <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-brand-100 text-sm font-bold text-brand-700">
                            {item.quantidade}x
                          </span>
                          <span className="text-base font-semibold text-slate-800 pt-0.5">
                            {produto?.nome}
                          </span>
                        </li>
                      )
                    })}
                  </ul>
                </div>

                {/* Footer / Actions */}
                <div className="p-4 bg-slate-50 border-t border-slate-100">
                  <button
                    onClick={() => marcarComoPronto(pedido.id_nota_fiscal)}
                    disabled={updatingId === pedido.id_nota_fiscal}
                    className="flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-3 text-sm font-bold text-white transition-all hover:bg-emerald-700 active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed"
                  >
                    {updatingId === pedido.id_nota_fiscal ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                      <>
                        <CheckCircle2 className="h-5 w-5" />
                        Marcar como Pronto
                      </>
                    )}
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
