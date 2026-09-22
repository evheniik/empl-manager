import { Link, Navigate, Route, BrowserRouter, Routes, useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext.jsx';
import CompaniesPage from './pages/CompaniesPage.jsx';
import EmployeesPage from './pages/EmployeesPage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import ProjectsPage from './pages/ProjectsPage.jsx';

function Nav() {
  const { isAuthenticated, checking, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate('/companies');
  }

  return (
    <nav className="nav">
      <span className="brand">Empl Manager</span>
      <Link to="/companies">Companies</Link>
      <Link to="/employees">Employees</Link>
      <Link to="/projects">Projects</Link>
      <span className="spacer" />
      {checking ? (
        <span>...</span>
      ) : isAuthenticated ? (
        <button type="button" onClick={handleLogout}>
          Logout
        </button>
      ) : (
        <Link to="/login">Login</Link>
      )}
    </nav>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Nav />
      <main className="container">
        <Routes>
          <Route path="/" element={<Navigate to="/companies" replace />} />
          <Route path="/companies" element={<CompaniesPage />} />
          <Route path="/employees" element={<EmployeesPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/login" element={<LoginPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
