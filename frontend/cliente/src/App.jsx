import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { CustomerAuthProvider } from './contexts/CustomerAuthContext'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Home from './pages/Home'
import Catalog from './pages/Catalog'
import Chat from './pages/Chat'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'

export default function App() {
  return (
    <CustomerAuthProvider>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col">
          <Navbar />
          <div className="flex-1">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/catalogo" element={<Catalog />} />
              <Route path="/chat" element={<Chat />} />
              <Route path="/entrar" element={<Login />} />
              <Route path="/cadastro" element={<Register />} />
              <Route path="/minha-conta" element={<Profile />} />
            </Routes>
          </div>
          <Footer />
        </div>
      </BrowserRouter>
    </CustomerAuthProvider>
  )
}
