import { Component } from 'react';
import { Collapse, Navbar, NavbarToggler, NavbarBrand, Nav, NavItem, NavLink, NavbarText, Button } from 'reactstrap';
import { NavLink as RouterNavLink, withRouter }  from 'react-router-dom';
import produce  from 'immer';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSignInAlt, faSignOutAlt, faUserEdit, faListOl, faUserCircle, faArrowRightToBracket, faBoxArchive, faFolderOpen } from '@fortawesome/free-solid-svg-icons';



 class NavigatonBar extends Component {

    state = {
        isOpen: false
    }

    toggle = () => {
        this.setState(
            produce(draft=>{
                draft.isOpen = !draft.isOpen;
            })
        );
    }

    render () {
        const isLoggedIn = false;
        return (
            <Navbar color="secondary" dark expand="sm" className="fixed-top">
                <NavbarBrand className='fw-bold ms-4 border border-2 rounded px-2 py-0'>
                    PKGman
                    <FontAwesomeIcon icon={faFolderOpen} className="ms-2 small"/>
                </NavbarBrand>
                <NavbarToggler onClick={this.toggle}/>
                <Collapse isOpen={this.state.isOpen} navbar className='mb-1'>
                    <Nav className="mr-auto" navbar className="ms-auto">
                        {
                            !isLoggedIn ?
                                <>
                                    <Button size="sm" color='primary' className='fw-bold'>
                                        <span className='border-end pe-1'>Sign in</span>
                                        <FontAwesomeIcon icon={faArrowRightToBracket} className="ms-1 small"/>
                                    </Button>
                               
                                    <Button size="sm" color='info' className='fw-bold pe-1 ms-2'>
                                        <span className='border-end pe-1 border-dark'>Sign up</span>
                                        <FontAwesomeIcon icon={faUserEdit} className="ms-1 small"/>
                                    </Button>
                            </>
                            :
                                <Button size="sm" color='info' className='fw-bold pe-1 ms-2'>
                                    <span className='border-end pe-1 border-dark'>Log out</span>
                                    <FontAwesomeIcon icon={faSignOutAlt} className="ms-1 small"/>
                                </Button>
                        }
                    </Nav>
                </Collapse>
          </Navbar>
        );
    }

}

export default NavigatonBar;