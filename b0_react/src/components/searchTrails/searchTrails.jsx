import React, { Component, useState, useRef } from 'react';
import { ApolloConsumer } from '@apollo/client';
// import { ApolloConsumer } from 'react-apollo';
import { gql } from 'apollo-boost';

import searchIcon from '../../images/searchIcon.png';

import './searchTrails.css';

const SearchTrails = (props) => {
   const [search, setSearch] = useState("")
   const inputEl = useRef(null)

   const handleSubmit = async (event, client) => {
      event.preventDefault();
      const res = await client.query({
         query: SEARCH_TRAILS_QUERY,
         variables: { search }
      })
      props.setSearchResults(res.data.trails)
   }

   const handleClear = () => {
      props.setSearchResults([])
      props.setResultIdx(0)
      setSearch("")
      inputEl.current.focus()
   }

   return (
      <ApolloConsumer>
         {client => (
            <div className="searchBarContainer">
               <div className="searchSpace"></div>
               <form className="searchBar" onSubmit={event => handleSubmit(event, client)}>
                  <div className="clear" onClick={handleClear}>X</div>
                  <input type="text" className="searchField" placeholder="Search for trails" value={search}
                     onChange={event => setSearch(event.target.value)} ref={inputEl} 
                  />
                  <button type="submit" className="submitSearch"><img src={searchIcon} className="searchIcon" /></button>
               </form>
            </div>
         )}

      </ApolloConsumer>
   )
}

const SEARCH_TRAILS_QUERY = gql`
   query($search: String) {
      trails(search: $search) {
         name 
         prop 
         city 
         state
         id
      }
   }
`

export default SearchTrails;