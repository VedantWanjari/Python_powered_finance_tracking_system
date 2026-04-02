import axios from 'axios'
import type {
  User,
  Transaction,
  Category,
  PaginatedResponse,
  DashboardData,
  TrendData,
  CategoryBreakdown,
  ReportData,
  LoginFormData,
  RegisterFormData,
  UpdateProfileFormData,
  UpdatePasswordFormData,
  TransactionFilters,
  TransactionFormData,
} from '../types'

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error) && error.response) {
      return Promise.reject(error.response.data)
    }
    return Promise.reject({ status: 'error', message: 'Network error' })
  },
)

function extractData<T>(response: { data: { data: T } }): T {
  return response.data.data
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export async function login(credentials: LoginFormData): Promise<User> {
  const res = await api.post<{ data: { user: User } }>('/auth/login', credentials)
  return res.data.data.user ?? res.data.data
}

export async function register(data: RegisterFormData): Promise<User> {
  const res = await api.post<{ data: { user: User } }>('/auth/register', data)
  return res.data.data.user ?? res.data.data
}

export async function logout(): Promise<void> {
  await api.post('/auth/logout')
}

export async function getMe(): Promise<User> {
  const res = await api.get('/auth/me')
  return extractData<User>(res)
}

export async function updateMe(data: UpdateProfileFormData): Promise<User> {
  const res = await api.put('/auth/me', data)
  return extractData<User>(res)
}

export async function updatePassword(data: UpdatePasswordFormData): Promise<void> {
  await api.put('/auth/me/password', data)
}

// ── Transactions ──────────────────────────────────────────────────────────────

export async function getTransactions(
  filters: TransactionFilters = {},
): Promise<PaginatedResponse<Transaction>> {
  const params: Record<string, string | number> = {}
  Object.entries(filters).forEach(([k, v]) => {
    if (v !== '' && v !== undefined && v !== null) params[k] = v as string | number
  })
  const res = await api.get('/transactions/', { params })
  return extractData<PaginatedResponse<Transaction>>(res)
}

export async function getTransaction(id: number): Promise<Transaction> {
  const res = await api.get(`/transactions/${id}`)
  return extractData<Transaction>(res)
}

export async function createTransaction(data: TransactionFormData): Promise<Transaction> {
  const payload = {
    ...data,
    amount: parseFloat(data.amount),
    category_id: data.category_id || null,
    tags: data.tags
      ? data.tags
          .split(',')
          .map((t) => t.trim())
          .filter(Boolean)
      : [],
  }
  const res = await api.post('/transactions/', payload)
  return extractData<Transaction>(res)
}

export async function updateTransaction(
  id: number,
  data: Partial<TransactionFormData>,
): Promise<Transaction> {
  const payload: Record<string, unknown> = { ...data }
  if (data.amount !== undefined) payload.amount = parseFloat(data.amount)
  if (data.category_id !== undefined) payload.category_id = data.category_id || null
  if (data.tags !== undefined) {
    payload.tags =
      typeof data.tags === 'string'
        ? data.tags
            .split(',')
            .map((t) => t.trim())
            .filter(Boolean)
        : data.tags
  }
  const res = await api.put(`/transactions/${id}`, payload)
  return extractData<Transaction>(res)
}

export async function deleteTransaction(id: number): Promise<void> {
  await api.delete(`/transactions/${id}`)
}

export async function searchTransactions(
  q: string,
  page = 1,
  perPage = 20,
): Promise<PaginatedResponse<Transaction>> {
  const res = await api.get('/transactions/search', { params: { q, page, per_page: perPage } })
  return extractData<PaginatedResponse<Transaction>>(res)
}

// ── Analytics ─────────────────────────────────────────────────────────────────

export async function getDashboard(): Promise<DashboardData> {
  const res = await api.get('/analytics/dashboard')
  return extractData<DashboardData>(res)
}

export async function getTrends(months = 6): Promise<TrendData[]> {
  const res = await api.get('/analytics/trends', { params: { months } })
  return extractData<TrendData[]>(res)
}

export async function getCategoryBreakdown(
  startDate?: string,
  endDate?: string,
): Promise<CategoryBreakdown[]> {
  const params: Record<string, string> = {}
  if (startDate) params.start_date = startDate
  if (endDate) params.end_date = endDate
  const res = await api.get('/analytics/categories', { params })
  return extractData<CategoryBreakdown[]>(res)
}

export async function getReport(
  period: string,
  year: number,
  month?: number,
): Promise<ReportData> {
  const params: Record<string, string | number> = { period, year }
  if (month !== undefined) params.month = month
  const res = await api.get('/analytics/report', { params })
  return extractData<ReportData>(res)
}

// ── Categories ────────────────────────────────────────────────────────────────

export async function getCategories(): Promise<Category[]> {
  const res = await api.get('/categories/')
  return extractData<Category[]>(res)
}
