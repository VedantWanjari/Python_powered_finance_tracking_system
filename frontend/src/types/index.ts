export interface User {
  id: number
  username: string
  email: string
  role: 'viewer' | 'analyst' | 'admin'
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Transaction {
  id: number
  user_id: number
  amount: number
  transaction_type: 'income' | 'expense'
  category_id: number | null
  category_name: string | null
  date: string
  description: string
  notes: string | null
  tags: string[]
  is_recurring: boolean
  recurring_frequency: string | null
  budget_month: string | null
  created_at: string
  updated_at: string
}

export interface Category {
  id: number
  name: string
  description: string | null
  color: string | null
  icon: string | null
  created_by: number | null
  is_default: boolean
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export interface DashboardData {
  total_income: number
  total_expenses: number
  net_balance: number
  transaction_count: number
  recent_transactions: Transaction[]
}

export interface TrendData {
  month: string
  income: number
  expenses: number
  net: number
}

export interface CategoryBreakdown {
  category_id: number | null
  category_name: string
  total: number
  percentage: number
}

export interface ApiResponse<T> {
  status: 'success' | 'error'
  data: T
  message: string
  timestamp: string
}

export interface ApiError {
  status: 'error'
  message: string
  errors?: Record<string, string[]>
  timestamp: string
}

export interface TransactionFilters {
  page?: number
  per_page?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
  date_from?: string
  date_to?: string
  transaction_type?: 'income' | 'expense' | ''
  category_id?: number | ''
  amount_min?: number | ''
  amount_max?: number | ''
  search?: string
  tags?: string
}

export interface TransactionFormData {
  amount: string
  transaction_type: 'income' | 'expense'
  date: string
  description: string
  category_id?: number | ''
  notes?: string
  tags?: string
  is_recurring?: boolean
  recurring_frequency?: string
  budget_month?: string
}

export interface LoginFormData {
  username: string
  password: string
}

export interface RegisterFormData {
  username: string
  email: string
  password: string
}

export interface UpdateProfileFormData {
  username?: string
  email?: string
}

export interface UpdatePasswordFormData {
  current_password: string
  new_password: string
}

export interface ReportData {
  period: string
  income: number
  expenses: number
  net: number
  top_categories: CategoryBreakdown[]
  transaction_count: number
}
