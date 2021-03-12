import React, { useState } from 'react';
import { gql, useQuery } from '@apollo/client';

import CheckIn from '../../components/checkIn/checkIn'
import CheckOut from '../../components/checkOut/checkOut'

import '../../pages/traildetail/traildetail.css'

const CheckInOut = ({ trailID }) => {
   console.log({trailID:trailID})
   const [checkInEnabled, setCheckInEnabled] = useState(!!localStorage.getItem('authToken') ? true : false)
   const [checkOutEnabled, setCheckOutEnabled] = useState(!!localStorage.getItem('authToken') ? true : false)
   const [checkStatusText1, setCheckStatusText1] = useState("")
   const [checkStatusText2, setCheckStatusText2] = useState("")

   const { loading, error, data, refetch } = useQuery(
      MOST_RECENT_HIKE_QUERY,
      {variables: {trailID: trailID}}
   )

   if (loading) return <div>Loading ...</div>
   if (error) {console.log(error); return <div>Error</div>}
   if (!data) return <div>Not Found</div>

   if(!!localStorage.getItem('authToken')) {
      if(data.hikerMostRecentHikeOnTrail.length > 0) {
         if(!data.hikerMostRecentHikeOnTrail[0].checkOutDate) {
            setCheckInEnabled(false)
            setCheckStatusText1("Checked In:")
            setCheckStatusText2(data.hikerMostRecentHikeOnTrail[0].date)
         }
         else {
            setCheckOutEnabled(false);
         }
      }
      else {
         setCheckOutEnabled(false);
      }
   }

   return (
      <div>
         <CheckIn checkInEnabled={checkInEnabled} setCheckInEnabled={setCheckInEnabled} setCheckOutEnabled={setCheckOutEnabled} 
            refetch={refetch} 
         />
         <CheckOut checkOutEnabled={checkOutEnabled} setCheckOutEnabled={setCheckOutEnabled} setCheckInEnabled={setCheckInEnabled} 
            refetch={refetch} 
         />
         <div className="topDetailsSpace"><div className="checkInOutStatus">
            <div>{checkStatusText1}</div><div>{checkStatusText2}</div>
         </div></div>
      </div>
   )
}

const MOST_RECENT_HIKE_QUERY = gql`
   query ($trailID: Int!) {
      hikerMostRecentHikeOnTrail(trailID: $trailID, hikerID:13) {
         date
         checkOutDate
      }
   }
`

export default CheckInOut;