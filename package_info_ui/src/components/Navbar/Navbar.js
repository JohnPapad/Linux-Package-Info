import { Component } from 'react';
import { Collapse, Navbar, NavbarToggler, NavbarBrand, Nav, NavItem, ModalHeader, Modal, Button, ModalBody } from 'reactstrap';
import { withRouter }  from 'react-router-dom';
import produce  from 'immer';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSignOutAlt, faUserEdit, faArrowRightToBracket, faFolderOpen } from '@fortawesome/free-solid-svg-icons';
import Auth from '../Auth/Auth';
import { API } from '../../services/API';
import axiosInstance from '../../services/axiosConfig';


 class NavigationBar extends Component {

    state = {
        navbarIsOpen: false,
        authModalIsOpen: false,
        authModalType: null,
    }

    toggleNavbar = () => {
        this.setState(
            produce(draft=>{
                draft.navbarIsOpen = !draft.navbarIsOpen;
            })
        );
    }

    toggleAuthModal = (type) => {
        this.setState(
            produce(draft=>{
                draft.authModalIsOpen = !draft.authModalIsOpen;
                draft.authModalType = type;
            })
        );
    }

    logOutHandler = async () => {
        const payload = {
            "refresh_token": localStorage.getItem('refresh_token')
        };
        const response = await API.logOut(payload);
        console.log(response)

        localStorage.removeItem('access_token');
		localStorage.removeItem('refresh_token');
		axiosInstance.defaults.headers['Authorization'] = null;

        this.props.history.push("/");
    }

    render () {
        const isLoggedIn = localStorage.getItem("access_token") ? true : false;
        return (
            <>
            <Navbar color="secondary" dark expand="sm" className="fixed-top">
                <NavbarBrand className='fw-bold ms-4 border border-2 rounded px-2 py-0'>
                    PKGman
                    <FontAwesomeIcon icon={faFolderOpen} className="ms-2 small"/>
                </NavbarBrand>
                <NavbarToggler onClick={this.toggleNavbar}/>
                <Collapse isOpen={this.state.navbarIsOpen} navbar className='mb-1'>
                    <Nav className="mr-auto" navbar className="ms-auto">
                        {
                            !isLoggedIn ?
                                <>
                                    <Button size="sm" color='primary' className='fw-bold' onClick={()=>this.toggleAuthModal("login")}>
                                        <span className='border-end pe-1'>Log in</span>
                                        <FontAwesomeIcon icon={faArrowRightToBracket} className="ms-1 small"/>
                                    </Button>
                               
                                    <Button size="sm" color='info' className='fw-bold pe-1 ms-2' onClick={()=>this.toggleAuthModal("signup")}>
                                        <span className='border-end pe-1 border-dark'>Sign up</span>
                                        <FontAwesomeIcon icon={faUserEdit} className="ms-1 small"/>
                                    </Button>
                            </>
                            :
                                <Button size="sm" color='dark' className='fw-bold pe-1 ms-2' onClick={()=>this.logOutHandler()}>
                                    <span className='border-end pe-1 border-dark'>Log out</span>
                                    <FontAwesomeIcon icon={faSignOutAlt} className="ms-1 small"/>
                                </Button>
                        }
                    </Nav>
                </Collapse>
            </Navbar>

            <Modal size="md" isOpen={this.state.authModalIsOpen} toggle={this.toggleAuthModal} className='pt-5'>
                <Auth type={this.state.authModalType} toggleAuthModal={this.toggleAuthModal}/>
            </Modal>
          </>
        );
    }

}

export default withRouter(NavigationBar);