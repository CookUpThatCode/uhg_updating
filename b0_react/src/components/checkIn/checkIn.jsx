import React from 'react';
import { gql, useMutation } from '@apollo/client';

import '../../pages/traildetail/traildetail.css';

const checkInHandler = async (checkIn, props) => {
   if (props.checkInEnabled) {
      const result = await checkIn();
      console.log(result);
      props.setCheckInEnabled(false);
      props.setCheckOutEnabled(true);
      props.setCheckStatusText1("Checked In:")
      props.setCheckStatusText2(result.data.checkIn.date)
      props.refetch();
      console.log(result.data.checkIn.date)
   } 
} 

const CheckIn = (props) => {
   const [checkIn, { loading, error }] = useMutation(CHECK_IN_MUTATION)

   if(loading) return null;
   if(error) return <div>Error</div>

   return (
      <div className={props.checkInEnabled ? "checkInOutBox chIn" : "checkInOutBox gray"} onClick={() => checkInHandler(checkIn, props)}>CHECK IN</div>
   )
}

const CHECK_IN_MUTATION = gql`
   mutation ($trailID: Int!) {
      checkIn(trailID: $trailID) {
         hike {
            id
         }
         date
      }
   }
`

export default CheckIn;
