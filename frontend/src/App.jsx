import './App.css';
import React, {useState} from 'react';
import TopBar from './components/TopBar';
import TemplateGenerator from './components/TemplateGenerator';
import Alert from './components/Alert';
import { EntitySelectContext } from './contexts/EntitySelectContext';

function App() {
  const [idx, setIdx] = useState("0");
  const [message, setMessage] = useState("");
  const [err, setErr] = useState(false);

  return (
    <>
      <EntitySelectContext.Provider value={{idx, err, message, setIdx, setMessage, setErr}}>
        {message ? <Alert /> : <></>}
        <TopBar />
        <TemplateGenerator />
      </EntitySelectContext.Provider>
    </>
  );
}

export default App;
