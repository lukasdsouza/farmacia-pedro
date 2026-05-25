import api from './client'

export const sendMessage = (sessionId, text, customerId = null) =>
  api.post('/chat/message', { session_id: sessionId, text, customer_id: customerId })
