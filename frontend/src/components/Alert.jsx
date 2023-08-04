import React, {useContext} from 'react';
import { EntitySelectContext } from '../contexts/EntitySelectContext';

export default function Alert() {
  const { err, message, setErr, setMessage } = useContext(EntitySelectContext);
  const closeAlertHandler = () => {
    setErr(false);
    setMessage("");
  };

  return (
    <div class={err === true ? "alert alert-danger alert-dismissible fs-5 text-center" : "alert alert-success alert-dismissible fs-5 text-center"} role="alert">
      {message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close" onClick={closeAlertHandler}></button>
    </div>
  );
}