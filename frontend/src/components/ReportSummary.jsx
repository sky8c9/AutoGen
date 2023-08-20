import React, {useContext} from 'react';
import { ReportSummaryContext } from '../contexts/ReportSummaryContext';

export default function ReportSummary() {
  const { summary } = useContext(ReportSummaryContext);
  const txt = Object.keys(summary).length !== 0 ? summary.TXT : undefined;
  const reports = Object.keys(summary).length !== 0 ? [summary.EAMS, summary.PFML] : undefined;
  
  return (
    <> 
        {txt &&
        <>
            <h4>Summary</h4>
            {txt.split('\n').map(val => <h6>{val}</h6>)}
            {reports && reports.map((report, _) => 
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th scope="col">#</th>
                            {report && report.header.map((colTitle, _) =>
                                <th>{colTitle}</th>
                            )}
                        </tr>
                    </thead>
                    <tbody>
                        {report && report.entries.map((colVal, index) => 
                            <tr>
                                <th scope="row">{index}</th>
                                {colVal.map((val, _) =>
                                    <td>{val}</td>
                                )}
                            </tr>
                        )}  
                    </tbody>
                </table>
            )}
        </>
        }
    </>
  );
}
