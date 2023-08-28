import React, { useState, useEffect, useContext } from 'react';
import { EntitySelectContext } from '../contexts/EntitySelectContext';
import axios from 'axios';

export default function TaxUtil() {
    const { entityList, idx } = useContext(EntitySelectContext);
    const [rate, setRate] = useState(0);

    useEffect(() => {
      const url = process.env.REACT_APP_SALE_TAX_API_URL;
      const fetchEntity = async () => {
        try {
          // preprocessing business address
          let fullAddress = entityList[idx].address;
          let [address, city, state, zip] = fullAddress.split(", ");
          let fieldDict = {};

          // call api to get sale tax
          const res = await axios.get(`${url}&zip=${zip}`);
          
          // preprocessing response data & update sale tax
          const field = res.data.split(" ");
          for(let i = 0; i < field.length; i++) {
              let pair = field[i].split("=");
              fieldDict[pair[0]] = pair[1];
          }

          setRate(fieldDict.Rate);
        } catch (e) {
          console.log(e.response);
        }
      };
    
      fetchEntity();
    }, [idx]);

    return (
        <div class="container text-center display-6 p-5">
            { rate !== "-1"
                ? <>Sale Tax Rate: {rate * 100}%</>
                : <>Invalid address</>
            }
        </div>
    )
}