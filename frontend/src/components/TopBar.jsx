import React, {useState, useEffect, useContext} from 'react';
import { EntitySelectContext } from '../contexts/EntitySelectContext';
import { Link } from "react-router-dom";
import axios from 'axios';

export default function TopBar() {
  const { entityList, setIdx, setEntityList } = useContext(EntitySelectContext);
  const axs = axios.create({baseURL: process.env.REACT_APP_API_URL});

  useEffect(() => {
    const fetchEntity = async () => {
      try {
        const res = await axs.get("/entity");
        setEntityList(res.data);
      } catch (e) {
        console.log(e.response);
      }
    };
  
    fetchEntity();
  }, []);

  return (
    <>
      <nav class="navbar navbar-expand-lg bg-body-tertiary">
        <div class="container-fluid">
          <div class="collapse navbar-collapse" id="navbarText">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0 fs-4">
              <li class="nav-item">
                <Link class="nav-link" to="/gen">AutoGen</Link>
              </li>
              <li class="nav-item">
                <Link class="nav-link" to="/util">TaxUtil</Link>
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