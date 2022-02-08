import { Component } from 'react';
import { Form, 
    Label,
    InputGroup,
    Input,
    Modal,
    ModalHeader,
    ModalBody,
    Button,
    ButtonGroup,
    DropdownItem, 
    Row, Col} from 'reactstrap';
import produce from 'immer';
import styles from './SearchFilters.module.scss';
import { createQueryParams } from '../../utilities/URIutil';
import { withRouter } from 'react-router';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFilter, faSlidersH, faTimesCircle } from '@fortawesome/free-solid-svg-icons';
import Select from 'react-select';


const addToOptions = (options, dropdownOptions) => {
    for ( const opt of options ) {
        dropdownOptions.push({
            'label': opt,
            'value': opt
        });
    }
}

const debDistros = [
    "Ubuntu:20.04",
    "Debian:11",
    "Kali:2021.4"
];

const rpmDistros = [
    "Fedora:34",
    "CentOS:8.4.2105"
];

const archs = [
    "all",
    "noarch",
    "x86_64",
    "i686"
];

const categories = [
    "admin",
    "cli-mono",
    "comm",
    "database",
    "debug",
    "devel",
    "doc",
    "editors",
    "education",
    "electronics",
    "embedded",
    "fonts",
    "games",
    "gnome",
    "gnu-r",
    "gnustep",
    "golang",
    "graphics",
    "hamradio",
    "haskell",
    "httpd",
    "interpreters",
    "introspection",
    "java",
    "javascript",
    "kde",
    "kernel",
    "libdevel",
    "libs",
    "lisp",
    "localization",
    "mail",
    "math",
    "metapackages",
    "misc",
    "net",
    "news",
    "ocaml",
    "oldlibs",
    "otherosfs",
    "perl",
    "php",
    "python",
    "ruby",
    "rust",
    "science",
    "shells",
    "sound",
    "tex",
    "text",
    "translations",
    "utils",
    "vcs",
    "video",
    "web",
    "x11",
    "xfce",
];

let categoriesDropdownOptions = [];
addToOptions(categories, categoriesDropdownOptions);

let archsDropdownOptions = [];
addToOptions(archs, archsDropdownOptions);

 
class SearchFilters extends Component {

    state = {
        filtersModalOpen: false,
        searchText: '',
        selectedDistros: [],
        selectedCategories: [],
        selectedTypes: [],
        selectedArchs: []
    };

    toggleFiltersModal = () => {
        this.setState(
            produce(draft => {
                draft.filtersModalOpen = !draft.filtersModalOpen;
            })
        );
    }

    onSelectChange = (selectedOptions, key) => {
        this.setState(
            produce(draft => {
                draft[key] = selectedOptions;
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
        console.log("search filters state: ", this.state)
        const selectedDistrosSet = new Set();
        for (const distro of this.state.selectedDistros) {
            selectedDistrosSet.add(distro.value)
        }
        console.log("selectedDistrosSet", selectedDistrosSet)

        const selectedTypesSet = new Set();
        for (const type of this.state.selectedTypes) {
            selectedTypesSet.add(type.value)
        }
        console.log("selectedTypesSet", selectedTypesSet)

        let distrosDropdownOptions = [];
        if (selectedTypesSet.size === 0){
            addToOptions(debDistros, distrosDropdownOptions);
            addToOptions(rpmDistros, distrosDropdownOptions);
        }
        else {
            if (selectedTypesSet.has("deb")) {
                addToOptions(debDistros, distrosDropdownOptions);
            }

            if (selectedTypesSet.has("rpm")) {
                addToOptions(rpmDistros, distrosDropdownOptions);
            }
        }
    
        return (
            <>
                <form onSubmit={e=>this.submitFormHandler(e)}>
                    <InputGroup>
                        <Input
                            bsSize="sm"
                            placeholder="Example: grep"
                            value={this.state.searchText}
                            onChange={e => this.inputChangedHandler(e.target.value)}
                        />

                        <ButtonGroup>
                            <Button className="fw-bold" onClick={this.submitFormHandler}>
                                Search
                            </Button>
                            <Button className='border-start' onClick={this.toggleFiltersModal}>
                                <FontAwesomeIcon icon={faSlidersH} className="mx-1 text-light"/>
                            </Button>
                        </ButtonGroup>
                    </InputGroup>
                </form>

                <Modal size="lg" centered isOpen={this.state.filtersModalOpen} toggle={this.toggleFiltersModal}>
                    <ModalHeader toggle={this.toggleFiltersModal}>
                        Search Filters
                    </ModalHeader>

                    <ModalBody className="pt-s0 mbs-2">
                        <Row>
                            <Col>
                                <Label className={"fw-bold small"}>
                                    Type
                                </Label>
                                <Select
                                    isSearchable
                                    isMulti
                                    options={[
                                        {
                                            'label': 'deb',
                                            'value': 'deb'
                                        },
                                        {
                                            'label': 'rpm',
                                            'value': 'rpm'
                                        }
                                    ]} 
                                    onChange={selectedOptions => this.onSelectChange(selectedOptions, "selectedTypes")} 
                                    placeholder="Select one or more"
                                />
                            </Col>
                            <Col>
                                <Label className={"fw-bold small"}>
                                    Distribution
                                </Label>
                                <Select 
                                    isSearchable
                                    isMulti
                                    options={distrosDropdownOptions} 
                                    onChange={selectedOptions => this.onSelectChange(selectedOptions, "selectedDistros")} 
                                    placeholder="Select one or more"
                                />
                            </Col>
                        </Row>
                        <Row className='py-3'>
                            <Col>
                                <Label className={"fw-bold small"}>
                                    Architecture
                                </Label>
                                <Select 
                                    isSearchable
                                    isMulti
                                    options={archsDropdownOptions}
                                    onChange={selectedOptions => this.onSelectChange(selectedOptions, "selectedArchs")} 
                                    placeholder="Select one or more"
                                />
                            </Col>
                            <Col>
                                <Label className={"fw-bold small"}>
                                    Category
                                </Label>
                                <Select
                                    isSearchable
                                    isMulti
                                    isDisabled={selectedDistrosSet.has("Fedora:34") || selectedDistrosSet.has("CentOS:8.4.2105")}
                                    options={categoriesDropdownOptions} 
                                    onChange={selectedOptions => this.onSelectChange(selectedOptions, "selectedCategories")} 
                                    placeholder="Select one or more"
                                />
                            </Col>
                        </Row>
                    </ModalBody>
                </Modal>
            </>
        );
    }

}

export default withRouter(SearchFilters);