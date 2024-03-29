import './App.css';
import React, {useState} from 'react';
import { BrowserRouter, Routes, Route} from "react-router-dom"
import TemplateGenerator from './components/TemplateGenerator';
import TaxUtil from './components/TaxUtil';
import Alert from './components/Alert';
import MainLayout from './components/MainLayout';
import { EntitySelectContext } from './contexts/EntitySelectContext';

function App() {
  const [entityList, setEntityList] = useState([]);
  const [idx, setIdx] = useState("0");
  const [message, setMessage] = useState("");
  const [err, setErr] = useState(false);

  return (
    <BrowserRouter>
      <EntitySelectContext.Provider value={{entityList, idx, err, message, setEntityList, setIdx, setMessage, setErr}}>
        {message ? <Alert /> : <></>}
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index="/gen" element={<TemplateGenerator />} />
            <Route path="/gen" element={<TemplateGenerator />} />
            <Route path="/util" element={<TaxUtil />} />
          </Route>
        </Routes>
      </EntitySelectContext.Provider>
    </BrowserRouter>
  );
}

export default App;
