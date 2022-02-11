import { Component } from "react";
import { Form, InputGroup, Input, Label, Button, FormGroup, Alert } from "reactstrap";
import produce from 'immer';
import { API } from "../../services/API";
import { withRouter } from "react-router-dom";


class Auth extends Component {

    state = {
        type: this.props.type,
        alertMsg: null,
        alertColor: "",
        formElems: {
            username: "",
            email: "",
            password: ""
        },
        errorMsgs: {
            username: null,
            email: null,
            password: null
        }
    };

    changeFormType = (type) => {
        this.setState(
            produce(draft=>{
                draft.type = type;
            })
        );
    }

    inputChangedHandler = (key, value) => {
        this.setState(
            produce(draft=>{
                draft.formElems[key] = value;
            })
        );
    }

    onAlertDismiss = () => {
        this.setState(
            produce(draft=>{
                draft.alertMsg = null;
                draft.alertColor = "";
            })
        );
    }

    badRequestHandler = (errors) => {
        this.setState(
            produce(draft=>{
                for (const errorKey in errors) {
                    draft.errorMsgs[errorKey] = errors[errorKey].join(". ");
                }

                for (const errorKey in draft.errorMsgs) {
                    if (errorKey in errors) continue;
                    draft.errorMsgs[errorKey] = null;
                }
            })
        );
    }

    submitFormHandler = async (event) => {
        event.preventDefault();
        event.stopPropagation();

        let payload = {
            "username": this.state.formElems.username,
            "password": this.state.formElems.password
        };

        if (this.state.type === "signup") {
            payload["email"] = this.state.formElems.email;
            const response = await API.signUp(payload);
            if (response.status == 400) {
                //bad request
                this.badRequestHandler(response.data);
            }
            else if (response.status === 201) {
                // all ok user was registered
                this.setState(
                    produce(draft=>{
                        draft.alertMsg = "Successfully signed up! Please log in to proceed.";
                        draft.alertColor = "success";
                        draft.type = "login";
                        for (const errorKey in draft.errorMsgs) {
                            draft.errorMsgs[errorKey] = null;
                        }
                        for (const key in draft.formElems) {
                            draft.formElems[key] = "";
                        }
                    })
                );
            }
        }
        else {
            const response = await API.logIn(payload);
            if (response.status == 400) {
                //bad request
                this.badRequestHandler(response.data);
            }
            else if (response.status === 401) {
                // wrong credentials
                this.setState(
                    produce(draft=>{
                        draft.alertMsg = "Wrong credentials";
                        draft.alertColor = "danger";
                        for (const errorKey in draft.errorMsgs) {
                            draft.errorMsgs[errorKey] = null;
                        }
                        for (const key in draft.formElems) {
                            draft.formElems[key] = "";
                        }
                    })
                );
            }
            else if (response.status === 200) {
                // all ok user logged in
                localStorage.setItem('access_token', response.data.access);
                localStorage.setItem('refresh_token', response.data.refresh);

                this.props.toggleAuthModal();
                this.props.history.push("/");
            }
        }
    }

    render () {

        return (
            <div style={{backgroundColor: '#f8f9fa'}} className="p-3 rounded">
            <header className="border-bottom mb-4 pb-2">
                <h3>
                {
                    this.state.type === "signup" ?
                        "Sign up"
                    :
                        "Log in" 
                }
                </h3>
            </header>

            {
                this.state.alertMsg &&
                <Alert color={this.state.alertColor} isOpen={this.state.alertMsg != null} toggle={this.onAlertDismiss}>
                    {this.state.alertMsg}
                </Alert>
            }
            <Form inline onSubmit={e=>this.submitFormHandler(e)}>
                <FormGroup floating>
                    <Input
                        id="username"
                        type="text"
                        placeholder="Username"
                        value={this.state.formElems.username}
                        onChange={(e)=>this.inputChangedHandler("username", e.target.value)}
                    />
                    <Label for="username">
                        Username
                    </Label>

                    <small className="text-danger">
                        {this.state.errorMsgs.username}
                    </small>
                </FormGroup>

                {
                    this.state.type === "signup" &&
                    <FormGroup floating>
                        <Input
                            id="email"
                            type="email"
                            placeholder="Email"
                            value={this.state.formElems.email}
                            onChange={(e)=>this.inputChangedHandler("email", e.target.value)}
                        />
                        <Label for="email">
                            Email
                        </Label>
                   
                        <small className="text-danger">
                            {this.state.errorMsgs.email}
                        </small>
                    </FormGroup>
                }

                <FormGroup floating>
                    <Input
                        id="password"
                        type="password"
                        placeholder="Password"
                        value={this.state.formElems.password}
                        onChange={(e)=>this.inputChangedHandler("password", e.target.value)}
                    />
                    <Label for="password">
                        Password
                    </Label>
                    <small className="text-danger">
                        {this.state.errorMsgs.password}
                    </small>
                </FormGroup>

                <div className="d-flex justify-content-end border-top mt-3 pt-3">
                    {
                        this.state.type === "signup" ?
                            <>
                                <Button color="link" className="me-3" onClick={()=>this.changeFormType("login")}>
                                    Already have an account?
                                </Button>
                                <Button color="info" className="fw-bold">
                                    Sign up
                                </Button>
                            </>
                        :
                            <>
                                <Button color="link" className="me-3" onClick={()=>this.changeFormType("signup")}>
                                    Don't have an account?
                                </Button>
                                <Button color="primary" className="fw-bold">
                                    Log in
                                </Button>
                            </>
                    }
                </div>
            </Form>
            </div>
        );
    }
}

export default withRouter(Auth);