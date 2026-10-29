import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { api } from '../services/api'
import { 
  LayoutDashboard, 
  Tags, 
  Package, 
  ShoppingCart, 
  Users, 
  Contact, 
  Truck, 
  Archive, 
  Link2, 
  LogOut,
  Coffee,
  RotateCcw
} from 'lucide-react'

function navClassName({ isActive }) {
  const base =
    'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all group'
  return isActive 
    ? `${base} bg-brand-800 text-brand-400 shadow-sm` 
    : `${base} text-brand-200 hover:bg-brand-800/50 hover:text-brand-50`
}

function iconClassName({ isActive }) {
  const base = 'h-5 w-5 transition-colors'
  return isActive ? `${base} text-brand-400` : `${base} text-brand-400/70 group-hover:text-brand-300`
}

export function AppLayout() {
  const { user, logout, hasAnyRole } = useAuth()
  const navigate = useNavigate()
  const [resetting, setResetting] = useState(false)

  const isDemoUser = user?.login === 'admin@fastcantina.com' || user?.login === 'atendente@fastcantina.com'

  async function handleLogout() {
    await logout()
    navigate('/login', { replace: true })
  }

  async function handleResetDemo() {
    if (!window.confirm('Deseja restaurar a cantina de demonstração para o estado original de teste? Isso redefinirá pedidos, estoque e produtos de exemplo.')) {
      return
    }

    setResetting(true)
    try {
      await api.post('/demo/reset')
      window.location.reload()
    } catch {
      alert('Falha ao restaurar dados de demonstração. Aguarde 1 minuto e tente novamente.')
    } finally {
      setResetting(false)
    }
  }

  const canManage = hasAnyRole(['admin', 'gerente'])

  return (
    <div className="flex min-h-screen bg-brand-50 text-brand-900">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 w-64 border-r border-brand-950 bg-brand-900 shadow-xl flex flex-col z-10">
        <div className="flex items-center gap-3 px-6 py-6 border-b border-brand-800/50">
          <div className="flex shrink-0 items-center justify-center">
            <img src="/logo.png" alt="FastCantina Logo" className="h-16 w-auto object-contain drop-shadow-md" />
          </div>
          <div>
            <p className="text-xl font-bold leading-tight font-serif text-brand-50">FastCantina</p>
            <p className="text-xs font-medium text-brand-300">Gestão Inteligente</p>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="space-y-1">
            <p className="px-3 text-xs font-semibold uppercase tracking-wider text-brand-400/70 mb-2">Operacional</p>
            <NavLink to="/pedidos" className={navClassName}>
              {({ isActive }) => <><ShoppingCart className={iconClassName({ isActive })} /> Pedidos (PDV)</>}
            </NavLink>
            <NavLink to="/cozinha" className={navClassName}>
              {({ isActive }) => <><Coffee className={iconClassName({ isActive })} /> Cozinha</>}
            </NavLink>
          </div>

          {canManage && (
            <div className="mt-8 space-y-1">
              <p className="px-3 text-xs font-semibold uppercase tracking-wider text-brand-400/70 mb-2">Visão Geral</p>
              <NavLink to="/dashboard" className={navClassName}>
                {({ isActive }) => <><LayoutDashboard className={iconClassName({ isActive })} /> Dashboard</>}
              </NavLink>
              <NavLink to="/categorias" className={navClassName}>
                {({ isActive }) => <><Tags className={iconClassName({ isActive })} /> Categorias</>}
              </NavLink>
              <NavLink to="/produtos" className={navClassName}>
                {({ isActive }) => <><Package className={iconClassName({ isActive })} /> Produtos</>}
              </NavLink>
            </div>
          )}

          {canManage && (
            <div className="mt-8 space-y-1">
              <p className="px-3 text-xs font-semibold uppercase tracking-wider text-brand-400/70 mb-2">Administração</p>
              <NavLink to="/usuarios" className={navClassName}>
                {({ isActive }) => <><Users className={iconClassName({ isActive })} /> Usuários</>}
              </NavLink>
              <NavLink to="/funcionarios" className={navClassName}>
                {({ isActive }) => <><Contact className={iconClassName({ isActive })} /> Funcionários</>}
              </NavLink>
              <NavLink to="/fornecedores" className={navClassName}>
                {({ isActive }) => <><Truck className={iconClassName({ isActive })} /> Fornecedores</>}
              </NavLink>
              <NavLink to="/estoque" className={navClassName}>
                {({ isActive }) => <><Archive className={iconClassName({ isActive })} /> Estoque</>}
              </NavLink>
              <NavLink to="/fornecedor-produto" className={navClassName}>
                {({ isActive }) => <><Link2 className={iconClassName({ isActive })} /> Fornecedor-Produto</>}
              </NavLink>
            </div>
          )}
        </div>

        <div className="border-t border-brand-800/50 p-4">
          <div className="rounded-xl bg-brand-950 p-4 border border-brand-800">
            <div className="flex items-center gap-3 mb-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-800 text-brand-100 font-bold text-sm">
                {user?.nome?.charAt(0)?.toUpperCase() || 'U'}
              </div>
              <div className="flex-1 truncate">
                <p className="truncate text-sm font-semibold text-brand-50">{user?.nome}</p>
                <p className="truncate text-xs font-medium text-brand-400 capitalize">{user?.perfil}</p>
              </div>
            </div>

            {isDemoUser && (
              <button
                type="button"
                disabled={resetting}
                onClick={handleResetDemo}
                className="mb-2 flex w-full items-center justify-center gap-2 rounded-lg bg-amber-950/70 border border-amber-800/80 px-3 py-2 text-xs font-semibold text-amber-300 transition-colors hover:bg-amber-900/80 hover:text-amber-200 disabled:opacity-50 cursor-pointer"
                title="Restaura os dados originais da cantina de demonstração"
              >
                <RotateCcw className={`h-3.5 w-3.5 ${resetting ? 'animate-spin' : ''}`} />
                <span>{resetting ? 'Restaurando...' : 'Resetar Dados Demo'}</span>
              </button>
            )}

            <button
              type="button"
              onClick={handleLogout}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand-900 border border-brand-800 px-3 py-2 text-sm font-medium text-red-400 transition-colors hover:bg-red-950 hover:border-red-900 hover:text-red-300 cursor-pointer"
            >
              <LogOut className="h-4 w-4" />
              Sair da conta
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64 flex-1 p-8">
        <div className="mx-auto max-w-5xl">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
