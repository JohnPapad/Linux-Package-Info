import { Component } from 'react';
import { Form, 
    InputGroup,
    InputGroupAddon,
    InputGroupButtonDropdown,
    Input,
    Button,
    ButtonGroup,
    DropdownToggle,
    DropdownMenu,
    DropdownItem } from 'reactstrap';
import produce from 'immer';
import styles from './SearchForm.module.scss';
import { createQueryParams } from '../../utilities/URIutil';
import { withRouter } from 'react-router';


const dropdownOptions = [
    "all",
    "ubuntu",
    "debian"
];

 
class SearchForm extends Component {

    state = {
        dropdownOpen: false,
        searchText: '',
        selectedDropdownItem: dropdownOptions[0]
    };

    toggleDropDown = () => {
        this.setState(
            produce(draft => {
                draft.dropdownOpen = !draft.dropdownOpen;
            })
        );
    }

    dropdownItemClickedHandler = (chosenItem) => {
        this.setState(
            produce(draft => {
                draft.selectedDropdownItem = chosenItem;
            })
        );
    }

    inputChangedHandler = (value) => {
        this.setState(
            produce(draft => {
                draft.searchText = value;
            })
        );
    }

    submitFormHandler = (event) => {
        event.preventDefault();
        event.stopPropagation();
        const queryParams = {
            package: this.state.searchText,
            distro: this.state.selectedDropdownItem
        };
        this.props.history.push("/?" + createQueryParams(queryParams));
    }

    render () {

        const dropdownItems = dropdownOptions.map((item, i) =>(
            <div key={item}>
                <DropdownItem 
                    onClick={()=>this.dropdownItemClickedHandler(item)}
                    className={styles["dropdown-item"] + (item !== this.state.selectedDropdownItem ? " text-muted" : "")}
                >
                    {item}
                </DropdownItem>
                {
                    i < dropdownOptions.size && <DropdownItem divider />
                }
            </div>
        ));
        
        return (
            <form onSubmit={e=>this.submitFormHandler(e)}>
                <InputGroup>
                    <Input
                        placeholder="Example: grep"
                        value={this.state.searchText}
                        onChange={e => this.inputChangedHandler(e.target.value)}
                    />

                    <InputGroupButtonDropdown addonType="append" isOpen={this.state.dropdownOpen} toggle={this.toggleDropDown}>
            
                    <ButtonGroup>
                        <Button onClick={this.submitFormHandler}>Search</Button>
                        <DropdownToggle split>{''}</DropdownToggle>
                    </ButtonGroup>

                    <DropdownMenu>
                        {dropdownItems}
                    </DropdownMenu>

                    </InputGroupButtonDropdown>
                </InputGroup>
            </form>
        );
    }

}

export default withRouter(SearchForm);