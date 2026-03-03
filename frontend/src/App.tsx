import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import CompanyList from './pages/CompanyList';
import ExerciceList from './pages/ExerciceList';
import Form2058A from './pages/Form2058A';
import Form2058B from './pages/Form2058B';
import Form2058C from './pages/Form2058C';
import Layout from './components/Layout';

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token');
  return token ? <>{children}</> : <Navigate to="/login" />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/*"
          element={
            <PrivateRoute>
              <Layout>
                <Routes>
                  <Route path="/" element={<CompanyList />} />
                  <Route path="/companies/:companyId/exercices" element={<ExerciceList />} />
                  <Route path="/exercices/:exerciceId/2058a" element={<Form2058A />} />
                  <Route path="/exercices/:exerciceId/2058b" element={<Form2058B />} />
                  <Route path="/exercices/:exerciceId/2058c" element={<Form2058C />} />
                  <Route path="/dashboard/:companyId" element={<Dashboard />} />
                </Routes>
              </Layout>
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
