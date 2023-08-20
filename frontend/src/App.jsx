import './App.css';
import React, {useState} from 'react';
import { BrowserRouter, Routes, Route} from "react-router-dom"
import TemplateGenerator from './components/TemplateGenerator';
import TaxUtil from './components/TaxUtil';
import Alert from './components/Alert';
import MainLayout from './components/MainLayout';
import { EntitySelectContext } from './contexts/EntitySelectContext';

function App() {
  const [idx, setIdx] = useState("0");
  const [message, setMessage] = useState("");
  const [err, setErr] = useState(false);

  return (
    <BrowserRouter>
      <EntitySelectContext.Provider value={{idx, err, message, setIdx, setMessage, setErr}}>
        {message ? <Alert /> : <></>}
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route path="/gen" element={<TemplateGenerator />} />
            <Route path="/util" element={<TaxUtil />} />
          </Route>
        </Routes>
      </EntitySelectContext.Provider>
    </BrowserRouter>
  );
}

export default App;
