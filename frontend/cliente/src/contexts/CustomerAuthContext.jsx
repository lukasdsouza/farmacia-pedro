import { createContext, useContext, useState, useEffect } from 'react'

const CustomerAuthContext = createContext(null)

const TOKEN_KEY = 'farmacia_customer_token'
const CUSTOMER_KEY = 'farmacia_customer_data'

export function CustomerAuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [customer, setCustomer] = useState(() => {
    const raw = localStorage.getItem(CUSTOMER_KEY)
    try { return raw ? JSON.parse(raw) : null } catch { return null }
  })

  const login = (accessToken, customerData) => {
    localStorage.setItem(TOKEN_KEY, accessToken)
    localStorage.setItem(CUSTOMER_KEY, JSON.stringify(customerData))
    setToken(accessToken)
    setCustomer(customerData)
  }

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(CUSTOMER_KEY)
    setToken(null)
    setCustomer(null)
  }

  const updateCustomer = (data) => {
    const updated = { ...customer, ...data }
    localStorage.setItem(CUSTOMER_KEY, JSON.stringify(updated))
    setCustomer(updated)
  }

  return (
    <CustomerAuthContext.Provider value={{ token, customer, login, logout, updateCustomer, isLoggedIn: !!token }}>
      {children}
    </CustomerAuthContext.Provider>
  )
}

export function useCustomerAuth() {
  return useContext(CustomerAuthContext)
}
