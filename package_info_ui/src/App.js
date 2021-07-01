import { Component } from 'react';
import './App.scss';
import PackagesList from './components/PackagesList/PackagesList';
import { Container, Row, Col } from 'reactstrap';
import { Route, Redirect, Switch } from 'react-router-dom';


class App extends Component {

   
    render() {
        return (

            <Switch>
                <Route path="/" exact>
                    <Container fluid className="mt-5">
                        <PackagesList/>
                    </Container>
                </Route>

                <Redirect to="/" />
            </Switch>
        );
    }
    
}

export default App;
