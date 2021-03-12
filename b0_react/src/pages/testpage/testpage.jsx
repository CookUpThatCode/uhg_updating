import React, { useState } from 'react';
import { gql, useQuery } from '@apollo/client';
// import { connect } from 'react-redux';

import Header from '../../components/header/header';
import SearchTrails from '../../components/searchTrails/searchTrails';
import TrailSearchResultsList from '../../components/trailSearchResultsList/trailSearchResultsList';
import CheckIn from '../../components/checkIn/checkIn'
import CheckOut from '../../components/checkOut/checkOut'
import CheckInOut from '../../components/checkInOut/checkInOut';

import './testpage.css';

const TestPage = (props) => {
   const [searchResults, setSearchResults] = useState([])
   const [resultIdx, setResultIdx] = useState(0);

   const nextResultsHandler = () => {
      if (resultIdx+8 < searchResults.length) {
         setResultIdx(resultIdx+8);
      }
   }

   const prevResultsHandler = () => {
      if (resultIdx-8 >= 0) {
         setResultIdx(resultIdx-8);
      }
   }

   let imageUrl = 'http://localhost:8000/media/';

   const { loading, error, data } = useQuery(
      TRAIL_DETAIL_QUERY,
      {variables: {trailID: props.match.params.id}}
   )

   if (loading) return <div>Loading ...</div>
   if (error) return <div>Error</div>
   if (!data) return <div>Not Found</div>

   imageUrl += data.trailDetails[0].image;
   console.log(imageUrl)

   let tags = data.trailDetails[0].tags.map((tag, idx) => {
      return <div className="tag" key={`tag${idx}`}>{tag.tag}</div>
   })
   tags = tags.slice(0, 14);

   let equ = data.trailDetails[0].suggestedEquipment.map((equ, idx) => {
      return <div className="equ" key={`equ${idx}`}>{equ.equipmentTypeID.equType}</div>
   })
   equ = equ.slice(0, 14);

   let hikers = data.recentHikers.map((hik, idx) => {
      return <div className="recHiker" key={`hik${idx}`}>{hik.hiker.user.username}</div>
   })
   hikers = hikers.slice(0, 14);

   let reviews = data.expertReviews.map((rev, idx) => {
      return (
         <div className="expRev" key={`rev${idx}`}><div className="revInfo">
            <div className="revHiker">{rev.hiker.user.username}:&nbsp;
               <div className="revDate">{rev.date}</div>
            </div>
            <div className="revDifEnjLab">Difficulty:&nbsp;<div className="revDifEnj">{rev.difficulty} / 5</div></div>
            <div className="revDifEnjLab">Enjoyability:&nbsp;<div className="revDifEnj">{rev.enjoyability} / 5</div></div>
            <div className="revReview">{rev.review}</div>
         </div></div>
      )
   })
   reviews = reviews.slice(0, 5);

   let openStatus = "openFeeItem";
   if (!data.trailDetails[0].isOpen) {
      openStatus += " closed";
   }

   return (
      <div className="trailDetailPg">
         <Header currentPg="home" />
         <div>
            <div className="topDetailsContainer">
               <div className="namePropBox">
                  <div className="nmPropLn1">{data.trailDetails[0].name}</div>
                  <div className="nmPropLn2">{data.trailDetails[0].prop}</div>
               </div>
               <div className="labelsBox">
                  <div className="labelItem">Status:</div>
                  <div className="labelItem">Fee:</div>
               </div>
               <div className="openFeeBox">
                  <div className={openStatus}>{data.trailDetails[0].isOpen ? 'OPEN' : 'CLOSED'}</div>
                  <div className="openFeeItem">{data.trailDetails[0].fee===0 ? 'FREE' : `$${data.trailDetails[0].fee.toFixed(2)}`}</div>
               </div>
               <div className="smallSpace"></div>
               <div className="checkInOutBox"><CheckInOut trailID={data.trailDetails[0].id} /></div>
            </div>
            <SearchTrails setSearchResults={setSearchResults} setResultIdx={setResultIdx} />
            {searchResults.length > 0 && <TrailSearchResultsList results={searchResults.slice(resultIdx, resultIdx+8)} 
               nextResults={nextResultsHandler} prevResults={prevResultsHandler} resultIdx={resultIdx} numResults={searchResults.length} 
            />}
            <div className="trailDetailGrid">
               <div className="trailPic" style={{backgroundImage: `url(${imageUrl})`, backgroundSize: `cover`}}></div>
               <div className="trailDetails">
                  <div className="detailLine"><div className="detailLabel">Difficulty:</div><div className="detailData">{data.trailDetails[0].avgDifficulty.toFixed(1)}&nbsp;/&nbsp;5</div></div>
                  <div className="detailLine"><div className="detailLabel">Enjoyability:</div><div className="detailData">{data.trailDetails[0].avgEnjoyability.toFixed(1)}&nbsp;/&nbsp;5</div></div>
                  <div className="detailLine"><div className="detailLabel">Location:</div><div className="detailData">{data.trailDetails[0].city}, {data.trailDetails[0].state}</div></div>
                  <div className="detailLine"><div className="detailLabel">Distance:</div><div className="detailData">{data.trailDetails[0].distance.toFixed(1)}&nbsp;mi.</div></div>
                  <div className="detailLine"><div className="detailLabel">Altitude Gain:</div><div className="detailData">{data.trailDetails[0].altitudeChange}&nbsp;ft.</div></div>
                  <div className="detailLine"><div className="detailLabel">Description:</div><div className="descrText">{data.trailDetails[0].description}</div></div>
               </div>
               <div className="tags">Trail Tags <div>{tags}</div> </div>
               <div className="recEqu">Equipment to Bring <div>{equ}</div> </div>
               <div className="recentHikers">Recent Hikers <div>{hikers}</div> </div>
               <div className="expReviews">Expert Reviews <div>{reviews}</div> </div>
            </div>
         </div>
      </div>
   )
}

const TRAIL_DETAIL_QUERY = gql`
   query ($trailID: Int!) {
      trailDetails(trailID: $trailID) {
         id
         name 
         prop 
         city
         state
         description
         isOpen
         altitudeChange
         distance
         fee
         image
         suggestedEquipment {
            equipmentTypeID {
               equType
            }
         }
         tags {
            tag
         }
         avgDifficulty 
         avgEnjoyability
         image
      }
      expertReviews(trailID: $trailID) {
         hiker {
            id
            user {
              username
            }
         }
         review
         difficulty
         enjoyability
         date
      } 
      recentHikers(trailID: $trailID) {
         hiker {
            id
            user {
               username
            }
         }
      }
   }
`

export default TestPage;