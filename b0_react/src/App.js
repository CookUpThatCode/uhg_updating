import React from "react";
import { BrowserRouter, Switch, Route } from 'react-router-dom';
import { Query } from 'react-apollo';
import  { gql } from 'apollo-boost';

import HomePage from './pages/homepage/homepage';
import TrailDetail from './pages/traildetail/traildetail';
import Authorization from './pages/authorization/authorization';
import Profile from './pages/profile/profile';
import TestPage from './pages/testpage/testpage';

const App = () => (
   <BrowserRouter>
      <Switch>
         <Route exact path='/' component={HomePage} />
         <Route exact path='/traildetail/:id' component={TestPage} />
         <Route exact path='/auth' component={Authorization} />
         <Route exact path='/profile' component={Profile} />
         <Route exact path='/test' component={TestPage} />
      </Switch>
   </BrowserRouter>
);



const CONVO_THREADS_QUERY = gql`
   {
      conversationThreads(hikerID:1) {
      hikerID {
         user {
            username
         }
      }
      recipientID {
         user {
            username
         }
      }
      timeSent 
      content
      }
   }
`


export default App;
