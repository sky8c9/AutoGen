import React, {useState, useEffect, useContext} from 'react';
import { EntitySelectContext } from '../contexts/EntitySelectContext';

import axios from 'axios';

export default function TemplateGenerator() {
  const { idx, setMessage, setErr } = useContext(EntitySelectContext);
  const [reportType, setReportType] = useState("");
  const [fileA, setFileA] = useState();
  const [fileB, setFileB] = useState();
  const [reportList, setReportList] = useState([]);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const res = await axios.get("/report");
        setReportList(res.data);
      } catch (e) {
        console.log(e.response);
      }
    }
  
    fetchReport();
  }, []);

  const runHandler = () => {
    setErr(false);
    setMessage("");

    if (reportType != "" && fileA && fileB) {
        const form = new FormData();
        form.append("idx", idx);
        form.append("report", reportType);
        form.append("fileA", fileA);
        form.append("fileB", fileB);
    
        axios
        .post("/generator", form)
        .then(res => {
            setErr(false);
            setMessage("Template files are ready!!!")
            console.log(res);
        })
        .catch(e => {
            console.error(e);
        });
    } else {
        setErr(true);
        if (reportType == "") {
            setMessage("Report type is not selected!!!");
        } else {
            setMessage("One of the uploaded file is empty!!!");
        }
    }
  };

  return (
    <div class="container text-center">
        <div class="col align-items-center p-2">
            <div class="btn-group" role="group" aria-label="Basic radio toggle button group">
                {reportList && reportList.map((name, _) => 
                    <>
                        <input type="radio" class="btn-check" name="reportTypeRadio" id={name} autocomplete="off" onClick={e => setReportType(e.target.id)}/>
                        <label class="btn btn-light btn-lg" for={name}>{name}</label>
                    </>
                )}
            </div>
        </div>

        <div class="row align-items-center p-2">
            <div class="col-1 align-items-center col-form-label-lg">
                <label class="form-label">File A</label>
            </div>
            <div class="col align-items-center">
                <input class="form-control form-control-lg" id="PathA" type="file" onChange={e => setFileA(e.target.files[0])}/>
            </div>
        </div>

        <div class="row align-items-center p-2">
            <div class="col-1 align-items-center col-form-label-lg">
                <label class="form-label">File B</label>
            </div>
            <div class="col align-items-center">
                <input class="form-control form-control-lg" id="PathB" type="file" onChange={e => setFileB(e.target.files[0])}/>
            </div>
        </div>

        <div class="d-grid gap-2 col-2 mx-auto">
            <button type="submit" class="btn btn-outline-primary btn-lg" onClick={runHandler}>Run</button>
        </div>
    </div>
  );
}