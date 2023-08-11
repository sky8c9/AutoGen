import React, {useState, useEffect, useContext} from 'react';
import { EntitySelectContext } from '../contexts/EntitySelectContext';
import axios from 'axios';

export default function TopBar() {
  const { setIdx } = useContext(EntitySelectContext);
  const [entityList, setEntityList] = useState([]);
  const axs = axios.create({baseURL: process.env.REACT_APP_API_URL});

  useEffect(() => {
    const fetchEntity = async () => {
      try {
        const res = await axs.get("/entity");
        setEntityList(res.data);
      } catch (e) {
        console.log(e.response);
      }
    }
  
    fetchEntity()
  }, []);

  return (
    <>
      <nav class="navbar navbar-expand-lg bg-body-tertiary">
        <div class="container-fluid">
          <div class="collapse navbar-collapse" id="navbarText">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0 fs-4">
              <li class="nav-item">
                <a class="nav-link active" aria-current="page" href="#">AutoGen</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="#">AutoFill</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="#">AutoPay</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="#">TaxUtil</a>
              </li>
            </ul>

            <span>
              <select class="form-select form-select-lg" aria-label=".form-select-lg example" onChange={e => setIdx(e.target.value)}>
                  {entityList.length && entityList.map((info, index) => <option value={index}>{info.dba} | {info.ein} | {info.legal_name} | {info.address} | {info.contact}</option>)}
              </select>
            </span>
          </div>
        </div>
      </nav>
    </>
  );
}