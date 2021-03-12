import React from 'react';
import { gql, useMutation } from '@apollo/client';

import '../../pages/traildetail/traildetail.css';

const checkOutHandler = async (checkOut, props) => {
   if (props.checkOutEnabled) {
      const result = await checkOut();
      console.log(result);
      props.setCheckOutEnabled(false);
      props.setCheckInEnabled(true);
      props.setCheckStatusText1("")
      props.setCheckStatusText2("")
      props.refetch();
   }
} 

const CheckOut = (props) => {
   const [checkOut, { loading, error }] = useMutation(CHECK_OUT_MUTATION)

   if(loading) return null;
   if(error) return <div>Error</div>

   return (
      <div className={props.checkOutEnabled ? "checkInOutBox chOut" : "checkInOutBox gray"} onClick={() => checkOutHandler(checkOut, props)}>CHECK OUT</div>
   )
}

const CHECK_OUT_MUTATION = gql`
   mutation ($trailID: Int!) {
      checkOut(trailID: $trailID) {
         hike {
            id
         }
      }
   }
`

export default CheckOut;
