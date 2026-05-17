/* LEXGUARD AI — Root Application */

import { useState } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Shield } from 'lucide-react';
import UploadPage from './pages/UploadPage';
import AnalysisPage from './pages/AnalysisPage';
import type { AnalysisResult } from './types';
import './App.css';

function App() {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  return (
    <BrowserRouter>
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-inner">
          <Link to="/" className="navbar-brand">
            <div className="navbar-logo">
              <Shield size={20} />
            </div>
            <div>
              <div className="navbar-title">LEXGUARD AI</div>
              <div className="navbar-subtitle">Contract Intelligence</div>
            </div>
          </Link>
          <div className="navbar-right">
            <span className="navbar-status">
              <span className="status-dot" />
              AMADA Protocol Active
            </span>
          </div>
        </div>
      </nav>

      {/* Routes */}
      <Routes>
        <Route
          path="/"
          element={<UploadPage onAnalysisComplete={setAnalysisResult} />}
        />
        <Route
          path="/analysis"
          element={<AnalysisPage result={analysisResult} />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
