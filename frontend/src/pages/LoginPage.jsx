import { useState } from 'react'
import { useLocation, useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { api } from '../services/api'
import { KeyRound, User, Loader2, ArrowRight, RotateCcw, CheckCircle2 } from 'lucide-react'

export function LoginPage() {
  const { login, loginDemo } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [form, setForm] = useState({ login: '', senha: '' })
  const [loading, setLoading] = useState(false)
  const [resetting, setResetting] = useState(false)
  const [resetSuccess, setResetSuccess] = useState('')
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setResetSuccess('')

    try {
      await login(form.login, form.senha)
      const next = location.state?.from?.pathname || '/dashboard'
      navigate(next, { replace: true })
    } catch (requestError) {
      const detail = requestError.response?.data?.detail
      if (Array.isArray(detail)) {
        setError(detail.map(err => {
          const field = err.loc && err.loc.length > 0 ? err.loc[err.loc.length - 1] : 'Erro'
          return `${field}: ${err.msg}`
        }).join(' | '))
      } else if (typeof detail === 'string') {
        setError(detail)
      } else {
        setError('Falha no login. Verifique suas credenciais.')
      }
    } finally {
      setLoading(false)
    }
  }

  async function handleDemoLogin(perfil = 'admin') {
    setLoading(true)
    setError('')
    setResetSuccess('')

    const email = perfil === 'admin' ? 'admin@fastcantina.com' : 'atendente@fastcantina.com'
    setForm({ login: email, senha: 'password' })

    try {
      await loginDemo(perfil)
      const next = location.state?.from?.pathname || (perfil === 'funcionario' ? '/pedidos' : '/dashboard')
      navigate(next, { replace: true })
    } catch (requestError) {
      const detail = requestError.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Falha ao acessar cantina de demonstração.')
    } finally {
      setLoading(false)
    }
  }

  async function handleResetDemo() {
    if (!window.confirm('Deseja restaurar a cantina de demonstração para o estado original? Isso recriará os produtos, estoque e pedidos padrão de teste.')) {
      return
    }

    setResetting(true)
    setError('')
    setResetSuccess('')

    try {
      const response = await api.post('/demo/reset')
      setResetSuccess(response.data?.mensagem || 'Banco de demonstração restaurado com sucesso!')
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Falha ao restaurar cantina de demonstração. Aguarde 1 minuto.')
    } finally {
      setResetting(false)
    }
  }

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Left Side - Brand & Gradient */}
      <div className="hidden w-1/2 flex-col justify-between bg-linear-to-br from-brand-900 via-brand-800 to-brand-950 p-12 text-white lg:flex relative overflow-hidden">
        {/* Decorative elements */}
        <div className="absolute -top-24 -left-24 h-96 w-96 rounded-full bg-brand-600/20 blur-3xl"></div>
        <div className="absolute -bottom-24 -right-24 h-96 w-96 rounded-full bg-brand-500/20 blur-3xl"></div>

        <div className="relative z-10 flex items-center gap-4">
          <div className="flex shrink-0 items-center justify-center">
            <img src="/logo.png" alt="FastCantina Logo" className="h-24 w-auto object-contain drop-shadow-lg" />
          </div>
          <span className="text-4xl font-bold tracking-tight font-serif">FastCantina</span>
        </div>

        <div className="relative z-10 max-w-md">
          <h1 className="text-4xl font-bold leading-tight mb-6 font-serif">
            Gestão inteligente para sua cantina.
          </h1>
          <p className="text-brand-100 text-lg leading-relaxed">
            Controle de estoque, vendas e produtos em uma plataforma unificada e fácil de usar.
          </p>
        </div>

        <div className="relative z-10 text-sm text-brand-200">
          <p>
            Aviso: Este sistema foi desenvolvido para fins de demonstração e portfólio. Os dados apresentados são fictícios e não representam informações reais.
            Por se tratar de um ambiente de demonstração, os dados cadastrados podem ser alterados, removidos ou perdidos a qualquer momento, sem aviso prévio.
          </p>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="flex w-full flex-col justify-center px-8 sm:px-16 lg:w-1/2 lg:px-24 xl:px-32 relative">
        <div className="mx-auto w-full max-w-sm">
          <div className="mb-10 text-center lg:text-left">
            <div className="lg:hidden flex justify-center mb-8">
              <div className="flex shrink-0 items-center justify-center">
                <img src="/logo.png" alt="FastCantina Logo" className="h-24 w-auto object-contain drop-shadow-md" />
              </div>
            </div>
            <h2 className="text-3xl font-bold text-slate-900 tracking-tight">Bem-vindo de volta</h2>
            <p className="mt-2 text-slate-500">
              Insira suas credenciais para acessar o painel.
            </p>
          </div>

          <form className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-700" htmlFor="login">
                Usuário
              </label>
              <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
                  <User className="h-5 w-5 text-slate-400" />
                </div>
                <input
                  id="login"
                  type="text"
                  minLength={3}
                  maxLength={50}
                  required
                  placeholder="Seu nome de usuário ou e-mail"
                  value={form.login}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, login: event.target.value }))
                  }
                  className="w-full rounded-xl border border-slate-200 bg-white py-3 pl-11 pr-4 text-sm text-slate-900 outline-none transition-all placeholder:text-slate-400 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10"
                />
              </div>
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-700" htmlFor="senha">
                Senha
              </label>
              <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
                  <KeyRound className="h-5 w-5 text-slate-400" />
                </div>
                <input
                  id="senha"
                  type="password"
                  minLength={8}
                  maxLength={100}
                  required
                  placeholder="••••••••"
                  value={form.senha}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, senha: event.target.value }))
                  }
                  className="w-full rounded-xl border border-slate-200 bg-white py-3 pl-11 pr-4 text-sm text-slate-900 outline-none transition-all placeholder:text-slate-400 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10"
                />
              </div>
            </div>

            {error ? (
              <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                {error}
              </div>
            ) : null}

            <button
              type="submit"
              disabled={loading || resetting}
              className="group flex w-full items-center justify-center gap-2 rounded-xl bg-brand-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-brand-500/30 transition-all hover:bg-brand-700 focus:ring-4 focus:ring-brand-500/20 disabled:cursor-not-allowed disabled:opacity-70 cursor-pointer"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Entrando...
                </>
              ) : (
                <>
                  Entrar no sistema
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </>
              )}
            </button>
          </form>

          {/* Divisor Demo */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200"></div>
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-slate-50 px-3 text-slate-400 text-[11px] font-bold tracking-wider">
                Acesso Rápido para Demonstração
              </span>
            </div>
          </div>

          {/* Botões de Acesso Rápido (1 clique) */}
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              disabled={loading || resetting}
              onClick={() => handleDemoLogin('admin')}
              className="group flex flex-col items-center justify-center rounded-xl border border-slate-200 bg-white p-3 text-center transition-all hover:border-brand-500 hover:bg-brand-50/50 hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 disabled:cursor-not-allowed disabled:opacity-60 cursor-pointer"
            >
              <span className="text-xs font-semibold text-slate-800 group-hover:text-brand-700">👤 Admin</span>
              <span className="mt-0.5 text-[10px] text-slate-400">Acesso completo</span>
            </button>

            <button
              type="button"
              disabled={loading || resetting}
              onClick={() => handleDemoLogin('funcionario')}
              className="group flex flex-col items-center justify-center rounded-xl border border-slate-200 bg-white p-3 text-center transition-all hover:border-brand-500 hover:bg-brand-50/50 hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 disabled:cursor-not-allowed disabled:opacity-60 cursor-pointer"
            >
              <span className="text-xs font-semibold text-slate-800 group-hover:text-brand-700">👥 Atendente</span>
              <span className="mt-0.5 text-[10px] text-slate-400">PDV e Cozinha</span>
            </button>
          </div>

          {/* Feedback de Sucesso da Restauração */}
          {resetSuccess ? (
            <div className="mt-3 flex items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-xs font-medium text-emerald-700">
              <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-500" />
              <span>{resetSuccess}</span>
            </div>
          ) : null}

          {/* Botão para Restaurar Banco de Dados Demo */}
          <div className="pt-3 text-center">
            <button
              type="button"
              disabled={loading || resetting}
              onClick={handleResetDemo}
              className="inline-flex items-center gap-1.5 text-[11px] text-slate-500 hover:text-brand-600 transition-colors disabled:opacity-50 cursor-pointer"
              title="Restaura os dados originais da cantina de demonstração"
            >
              <RotateCcw className={`h-3 w-3 ${resetting ? 'animate-spin' : ''}`} />
              <span>{resetting ? 'Restaurando dados demo...' : 'Restaurar dados de teste padrão'}</span>
            </button>
          </div>
          
          <div className="mt-8 text-center">
            <Link to="/registrar" className="text-sm font-medium text-slate-600 hover:text-brand-600 transition-colors">
              Não tem uma conta? Registre sua cantina
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
