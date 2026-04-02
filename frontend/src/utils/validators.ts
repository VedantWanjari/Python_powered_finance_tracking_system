export function validatePassword(password: string): string[] {
  const errors: string[] = []
  if (password.length < 8) errors.push('At least 8 characters')
  if (!/[A-Z]/.test(password)) errors.push('At least one uppercase letter')
  if (!/[a-z]/.test(password)) errors.push('At least one lowercase letter')
  if (!/\d/.test(password)) errors.push('At least one number')
  return errors
}

export function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

export function validateUsername(username: string): boolean {
  return /^[a-zA-Z0-9_]{3,30}$/.test(username)
}

export function validateAmount(amount: string | number): boolean {
  const n = typeof amount === 'string' ? parseFloat(amount) : amount
  return !isNaN(n) && n > 0
}
