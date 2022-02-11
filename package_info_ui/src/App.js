// Copyright 2021 Ioannis Papadopoulos
// SPDX-License-Identifier: AGPL-3.0-or-later

import { Component } from 'react';
import './App.scss';
import PackagesList from './components/PackagesList/PackagesList';
import { Container, Row, Col } from 'reactstrap';
import { Route, Redirect, Switch } from 'react-router-dom';
import Navbar from './components/Navbar/Navbar';


class App extends Component {

   
    render() {
        return (
            <>
                <Navbar/>
                <main className='pt-5'>
                    <Switch>
                        <Route path="/" exact>
                            <PackagesList/>
                        </Route>

                        <Redirect to="/" />
                    </Switch>
                </main>
            </>
        );
    }
    
}

export default App;
