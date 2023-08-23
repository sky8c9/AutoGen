import React, {useContext} from 'react';
import { ReportSummaryContext } from '../contexts/ReportSummaryContext';

export default function ReportSummary() {
  const { summary } = useContext(ReportSummaryContext);

  return (
    <div class="row justify-content-center p-5"> 
        {Object.keys(summary).length !== 0 &&
        <>
            <h5>Summary</h5>
            {summary.descr && summary.descr.split('\n').map(val => <h6>{val}</h6>)}
            {summary.headers && summary.headers.map((titles, idx) =>
                <div class="table-responsive">
                    <table class="table table-bordered table-striped align-middle text-nowrap">
                        <thead>
                            <tr>
                                <th scope="col">#</th>
                                {titles && titles.map((title, _) =>
                                    <th>{title}</th>
                                )}
                            </tr>
                        </thead>
                        <tbody>
                            {summary.entries[idx] && summary.entries[idx].map((vals, index) => 
                                <tr>
                                    <th scope="row">{index}</th>
                                    {vals && vals.map((val, _) =>
                                        <td>{val}</td>
                                    )}
                                </tr>
                            )}  
                        </tbody>
                    </table>
                </div>
            )}
        </>
        }
    </div>
  );
}
