import { Component } from 'react';
import './App.scss';
import PackagesList from './components/PackagesList/PackagesList';
import SearchForm from './components/SearchForm/SearchForm';
import dpkgSampleData from './assets/packageData/dpkg-sample-data.json';
import produce from 'immer';
import { Container, Row, Col } from 'reactstrap';
import { Route, Redirect, Switch } from 'react-router-dom';


class App extends Component {

    state = {
        data: dpkgSampleData
    };

    searchQueryHandler = (query, selectedDistro) => {
        this.setState(
            produce(draft=>{
                if (selectedDistro === "all") {
                    draft.data = dpkgSampleData.filter(item=>item["package"].includes(query));
                }
                else {
                    draft.data = dpkgSampleData.filter(item=>item["distro"] === selectedDistro && item["package"].includes(query));
                }
            })
        );
    }

    render() {
        // console.log("data", this.state)
        return (

            <Switch>
                <Route path="/" exact>
                    <Container fluid className="mt-5">
                        <Row>
                            <Col md="3">
                                <SearchForm
                                    searchQueryHandler={this.searchQueryHandler}
                                />
                            </Col>
                        </Row>
                        <PackagesList
                            data={this.state.data}
                        />
                    </Container>
                </Route>

                <Redirect to="/" />
            </Switch>
        );
    }


    componentDidMount () {
        // API call here to fetch packages info
    }
    
}

export default App;
