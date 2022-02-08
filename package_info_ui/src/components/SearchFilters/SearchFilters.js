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
    Row, Col, ModalFooter} from 'reactstrap';
import produce from 'immer';
import styles from './SearchFilters.module.scss';
import { createQueryParams } from '../../utilities/URIutil';
import { withRouter } from 'react-router';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFilter, faSlidersH, faTimesCircle } from '@fortawesome/free-solid-svg-icons';
import Select from 'react-select';
import queryString from 'query-string';


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

    submitFormHandler = (event, selectedFilters) => {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }

        let URLqueryParams = {};
        if (selectedFilters) {
            URLqueryParams = {
                ...selectedFilters,
                'search': this.state.searchText,
                'ordering': ['name', 'distro']
            };
            this.toggleFiltersModal();
        }
        else if (this.state.searchText) {
            // only text search
            URLqueryParams = {
                'search': this.state.searchText,
                'ordering': ['name', 'distro']
            };
        }
        else {
            // no text search - just fetch all ordered by the highest rating in descending order
            URLqueryParams = {
                'ordering': ['-avg_rating', 'name', 'distro']
            };
        }

        this.props.fetchPackages(URLqueryParams);
    }

    getSelectedOptionsSet = (filterKey) => {
        const selectedOptionsSet = new Set();
        for (const opt of this.state[filterKey]) {
            selectedOptionsSet.add(opt.value);
        }
        return selectedOptionsSet;
    }

    render () {
        console.log("search filters state: ", this.state);

        const selectedDistrosSet = this.getSelectedOptionsSet("selectedDistros");
        console.log("selectedDistrosSet", selectedDistrosSet)

        const selectedTypesSet = this.getSelectedOptionsSet("selectedTypes");
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
                            <Button size="sm" className="fw-bold px-3" onClick={this.submitFormHandler}>
                                Search
                            </Button>
                            <Button size="sm" className='border-start' onClick={this.toggleFiltersModal}>
                                <FontAwesomeIcon icon={faSlidersH} className="mx-1 text-light"/>
                            </Button>
                        </ButtonGroup>
                    </InputGroup>
                </form>

                <Modal size="lg" isOpen={this.state.filtersModalOpen} toggle={this.toggleFiltersModal} className='pt-5'>
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
                                    defaultValue={this.state.selectedTypes}
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
                                    defaultValue={this.state.selectedDistros}
                                    isSearchable
                                    isMulti
                                    options={distrosDropdownOptions} 
                                    onChange={selectedOptions => this.onSelectChange(selectedOptions, "selectedDistros")} 
                                    placeholder="Select one or more"
                                />
                            </Col>
                        </Row>
                        <Row className='pt-3'>
                            <Col>
                                <Label className={"fw-bold small"}>
                                    Architecture
                                </Label>
                                <Select
                                    defaultValue={this.state.selectedArchs}
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
                                    defaultValue={this.state.selectedCategories}
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
                    <ModalFooter>
                        <Button className="fw-bold" 
                            onClick={()=>this.submitFormHandler(null,
                                {
                                    "distro__in": [...selectedDistrosSet],
                                    "type__in": [...selectedTypesSet],
                                    "versions__architecture__icontains": [...this.getSelectedOptionsSet("selectedArchs")],
                                    "section__in": [...this.getSelectedOptionsSet("selectedCategories")]
                                }
                            )}
                        >
                            Search
                        </Button>
                    </ModalFooter>
                </Modal>
            </>
        );
    }

}

export default withRouter(SearchFilters);